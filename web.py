from uuid import uuid4
import threading
from flask import render_template, request, url_for, session, redirect, flash, jsonify, Flask
from flask_login import logout_user, LoginManager, login_required
from flask_migrate import Migrate,upgrade

from chromaclass import Chroma, client_config
from datapipeline import process_user_data
from helpers import login_user_process, build_llm_prompt, requires_vector_data, background_process,user_processing_status
from llmservice.instructions import first_instruction, second_instruction, third_instruction
from llmservice.llm import llm
from oauth import OauthFacade
from dotenv import load_dotenv
from models import User, db
import logging
import os
from flask_apscheduler import APScheduler
import joblib
from model.model import get_collection_from_prompt
from flask_login import current_user

load_dotenv()
app = Flask(__name__)
model = joblib.load("model/prompt_classifier.joblib")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_SECRET_KEY = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_SCOPE = [
    "user-read-private",
    "user-read-email",
    "user-library-read",
    "user-library-modify",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "app-remote-control",
    "streaming",
    "user-read-recently-played",
    "user-top-read",
    "user-read-playback-position",
    "user-follow-read",
    "user-follow-modify",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private"
]
MAX_HISTORY = 6



@app.before_request
def assign_user():
    """
    Assigns or initializes a session for the current user before processing a request.

    For authenticated users, this function ensures that a chat history session variable
    is initialized and associated with the user. For unauthenticated users, it generates
    a temporary session with a unique user identifier (UUID) and initializes an
    anonymous chat history session variable.

    Parameters:
        None

    Returns:
        None
    """
    if current_user.is_authenticated:
        # Use current_user.id as session identifier
        session.setdefault('chat_history', [])
    else:
        # For anonymous users (not logged in), generate temp session
        session.setdefault('user_id', str(uuid4()))
        session.setdefault('chat_history', [])



# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """
        Loads a user from the database by their user ID. This function is used by the
        login manager to retrieve user information during the session management process.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            User: The user object corresponding to the given user ID if found,
            otherwise None.
    """
    return User.query.get(user_id)


# Error Handlers
@app.errorhandler(401)
def unauthorized(error):
    """
    Handles unauthorized access error (HTTP 401).

    This error handler is triggered when a 401 Unauthorized error occurs in the application. It logs the error
    message and returns a JSON response indicating the failure status and the reason for the authorization failure.

    Args:
        error: The error object containing information about the 401 Unauthorized error that occurred.

    Returns:
        A tuple containing a JSON response specifying the failure status and error message along with the HTTP
        status code 401.
    """
    logger.info(error)
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401


@app.errorhandler(404)
def page_not_found(e):
    """
    Handles the 404 error for the application and renders a custom 404 page.

    Arguments:
        e: Exception
            The exception instance for the 404 error.

    Returns:
        tuple
            A tuple containing the rendered 404 page and the 404 status code.
    """
    return render_template('404.html'), 404


@login_manager.unauthorized_handler
def unauthorized():
    """
    Handles unauthorized access attempts for routes requiring login.

    A callback function for the Flask-Login unauthorized_handler. When users try
    to access a route that requires authentication without being logged in,
    this function sends a feedback message and redirects them to the login view.

    Raises:
        Redirects the user to the URL specified by login_manager.login_view
        after flashing a warning message.

    Returns:
        Response: A Flask response object resulting from a redirect to the
        login view.
    """
    flash("You need to log in to access this page.", "warning")
    return redirect(url_for(login_manager.login_view))


@app.route('/')
@login_required
def index():
    """
    This function serves as the route for the index page of the application. It requires
    user authentication and displays the main HTML template.

    Summary:
    The function is a Flask route handler that manages the display of the application's
    index page. It ensures that only authenticated users can access this route and
    renders the appropriate HTML template.

    Decorators:
    - app.route: Maps the function to the root URL ('/') of the application.
    - login_required: Ensures the user must be logged in to access this route.

    Returns:
    Render a Flask template for the index page.
    """
    return render_template('index.html')


@app.route('/loader')
@login_required
def loader():
    """
    This function serves as a route handler for the '/loader' endpoint in a Flask web
    application. The route is restricted to authenticated users due to the presence of
    the `@login_required` decorator. When accessed, this function returns the
    'loader.html' template for rendering by the Flask application.

    Returns:
        flask.Response: The rendered 'loader.html' template as the response for the
        client.
    """
    return render_template('loader.html')


@app.route('/login')
def login():
    """
    Renders the login page along with authentication links for various services.

    This function is responsible for displaying the login page to the user and
    providing dynamic authentication links for specified services. Links are
    generated based on the OauthFacade handler configured for each service.

    Parameters:
        None

    Returns:
        HTML template: The rendered 'login.html' template containing the
        authentication links for the services.
    """
    logger.info('Rendering login page.')

    auth_links = {
        # 'github_link': OauthFacade('github', response_type="code", scope=["user:read:email"]).get_auth_link(),
        # 'twitch_link': OauthFacade('twitch', response_type="code", scope=["user:read:email"]).get_auth_link(),
        'spotify_link': OauthFacade('spotify', response_type="code", scope=SPOTIFY_SCOPE).get_auth_link()
    }

    return render_template('login.html', auth_links=auth_links)


@app.route('/callback')
def callback_route():
    """
    Handles the OAuth callback endpoint for authorization process.

    This route processes the result of an OAuth authorization request, retrieves the
    authorization code from the request, exchanges it for an access token, and handles
    user login flow.

    Raises:
        Redirects to /login with an error message in case of an error during the OAuth
        process, missing required parameters, or unexpected scenarios.

    Arguments:
        None

    Returns:
        Response object: A redirect response to the appropriate path based on success
        or failure during the OAuth process.
    """
    code = request.args.get('code')
    state = request.args.get('state')
    scope = request.args.get('scope')
    client = request.args.get('client')
    error = request.args.get('error')
    error_description = request.args.get('error_description')

    logger.info(f'This is client: {client}')

    if error:
        logger.error(f'Error during OAuth callback: {error_description}')
        flash(f'Error: {error_description}', 'error')
        return redirect('/login')

    if code:
        data = {'code': code, 'state': state, 'scope': scope}
        try:
            oauth_obj = OauthFacade(client=client, response_type="code", scope=scope)
            access_token = oauth_obj.get_access_token(data=data)
            access_data = {'access_token': access_token, 'client': client}
            session['oauth_token_data'] = access_data
            logger.info(f'Saved token: {access_token}')

            response = login_user_process()
            status_code = response[1] if isinstance(response, tuple) else response
            logger.info(response)
            if status_code == 201:
                flash('Logged in successfully!', 'success')
                try:
                    user_processing_status[current_user.id] = 'processing'
                    threading.Thread(target=background_process, args=(app, current_user.id)).start()
                except Exception as err:
                    logger.error(f'Error fetching from spotify pipeline{err}')
                    user_processing_status[current_user.id] = 'error'
                return redirect('/loader')
            elif hasattr(response, 'status') and response.status == 'error':
                flash('Failed to log in.', 'error')
                return redirect('/login')

            else:
                logger.warning('Unexpected login response.')
                flash('An unexpected error occurred during login.', 'error')
                return redirect('/login')

        except Exception as e:
            logger.exception('Failed during token handling.')
            flash('An error occurred during authentication.', 'error')
            return redirect('/login')

    # Fallback for any unexpected scenario
    flash('Invalid or missing code parameter.', 'error')
    return redirect('/login')


@app.route('/processing-status')
@login_required
def processing_status():
    """
    Handles the processing status retrieval for the currently logged-in user.

    This endpoint is designed to check the processing status of the logged-in user,
    based on their user ID. It retrieves the status, logs the details for debugging
    purposes, and responds with a JSON object containing"""
    status = user_processing_status.get(current_user.id)
    logger.info(f"[STATUS CHECK] User ID: {current_user.id}, Status: {status}")
    return jsonify({'status': status})



@app.route('/prompt', methods=['POST'])
@login_required
def prompt():
    """
    Handles user prompt processing, including generating AI responses and querying vector
    databases if needed. It supports storing conversation history, determining when vector
    database querying is necessary, and constructing additional data for response generation.

    This function processes the input prompt in multiple stages:
    1. Processes input JSON and validates its structure and content.
    2. Retrieves or updates the in-memory conversation history.
    3. Evaluates the necessity for querying a vector database and configures access if required.
    4. Generates an AI-based hallucinated response.
    5. Performs vector database queries using relevant collections.
    6. Constructs final output using AI and any retrieved data.
    7. Manages session chat history storage.

    The endpoint is restricted to logged-in users and accepts POST methods only.

    Arguments:
        None

    Returns:https://open.spotify.com/user/3156k2ink7zvduerdeixlxsxqvrq
        JSON response indicating the success or failure of processing. On successful
        execution, returns an AI-generated or data-enriched response. If any stage
        of processing fails, provides a descriptive error message in the response.

    Raises:
        KeyError: If expected keys are missing in the JSON payload.
        Exception: For general errors during any stage of processing. Error details are logged.
    """
    if not request.is_json:
        return jsonify({'status': 'failed', 'error': 'Invalid content type, expected application/json'}), 400

    data = request.json.get('prompt')
    user_id = current_user.id
    hallucinated_response = ''
    logger.info(f'Prompt received: {data}')

    if not data:
        return jsonify({'status': 'failed', 'error': 'No prompt provided'}), 400

    history = session.get('chat_history', [])

    context = "\n".join([
        f"User: {entry['user']}\nAssistant: {entry['assistant']}"
        for entry in history
    ])
    needs_vector_data = requires_vector_data(data)
    logger.info(f"Prompt intent: {'Vector DB' if needs_vector_data else 'Direct LLM'}")
    # Step 1: Generate hallucinated response
    if needs_vector_data:
        try:
            chroma_obj = None
            if needs_vector_data:
                chroma_obj = Chroma(client_config)
        except Exception as e:
            logger.error(f'Error initializing Chroma: {str(e)}')
            return jsonify({'status': 'failed', 'error': 'Internal server error during setup'}), 500

        try:
            hallucinated_response = llm(initial_query=data, instruction=first_instruction)
            hallucinated_response.seek(0)
            if hasattr(hallucinated_response, 'read'):
                hallucinated_response = hallucinated_response.read()

            logger.info(f'Hallucinated response: {hallucinated_response}')
        except Exception as e:
            logger.error(f'Error during hallucinated LLM processing: {str(e)}')
            hallucinated_response = ''

        try:
            # Step 2: Construct joint query
            joint_query = f"{hallucinated_response.strip()} {data.strip()}" if hallucinated_response else data.strip()

            # Step 3: Predict relevant collections
            filtered_collections = get_collection_from_prompt(model, joint_query, threshold=0.5)
            logger.info(f'Prediction result: {filtered_collections}')

            responses = []

            # Step 4: Query collections
            for collection_name in filtered_collections:
                full_collection_name = f'{user_id}{collection_name[0]}'
                logger.info(f"Querying collection: {full_collection_name}")

                if chroma_obj.collection_exist(name=full_collection_name):

                    chroma_obj.use_collection(name=full_collection_name)
                    query_response = chroma_obj.query_collection(
                        param={'query': joint_query},
                        name=full_collection_name
                    )

                    print(query_response['documents'])

                    if query_response:
                        responses.append({
                            'collection': collection_name[0],
                            'query_response': query_response
                        })
                        logger.info(f"Found relevant data in {collection_name[0]}: {query_response}")
                    else:
                        logger.info(f"No relevant data found in {collection_name[0]}.")
                else:
                    logger.info(f"Collection {full_collection_name} does not exist.")

            if not responses:
                return jsonify({'status': 'failed', 'message': 'No relevant data found for the prompt'}), 404

            # Step 5: Generate final response with LLM
            try:

                final_input_for_llm = build_llm_prompt(context, joint_query)
                print(final_input_for_llm)
                for response in responses:
                    final_input_for_llm += f"From collection '{response['collection']}':\n{response['query_response']}\n\n"

                generated_response = llm(initial_query=final_input_for_llm, instruction=second_instruction)
                generated_response.seek(0)
                generated_response = generated_response.read()

                history.append({
                    'user': data,
                    'assistant': generated_response
                })

                if len(history) > MAX_HISTORY:
                    history = history[-MAX_HISTORY:]

                try:
                    print(len(session.get('chat_history')))
                    session['chat_history'] = history
                except Exception as e:
                    logger.error(f'Failed to save chat history: {str(e)}')

                return jsonify({
                    'status': 'success',
                    'data': generated_response
                })

            except Exception as e:
                logger.error(f'Error during final LLM processing: {str(e)}')
                hallucinated_response = ''
                return jsonify({'status': 'failed', 'error': 'Error generating final response'}), 500

        except Exception as e:
            logger.error(f'Error during prediction: {str(e)}')
            return jsonify({'status': 'failed', 'error': str(e)}), 500
    else:
        try:
            final_input = build_llm_prompt(context, data.strip())
            logger.info(f'LLM-only prompt: {final_input}')

            response = llm(initial_query=final_input, instruction=third_instruction)
            response.seek(0)
            response = response.read()

            history.append({'user': data, 'assistant': response})
            if len(history) > MAX_HISTORY:
                history = history[-MAX_HISTORY:]

            try:
                session['chat_history'] = history
            except Exception as e:
                logger.error(f'Failed to save chat history: {str(e)}')

            return jsonify({'status': 'success', 'data': response})

        except Exception as e:
            logger.error(f'Error during LLM-only generation: {str(e)}')
            return jsonify({'status': 'failed', 'error': 'LLM-only response failed'}), 500


@app.route('/logout')
def logout():
    """
    Logs out the current user by clearing the session, removing stored
    OAuth token data, and redirecting to the home page.

    Args:
        None

    Returns:
        redirect: Redirects the user to the home page after logout.
    """
    logger.info('User initiated logout.')

    flash('You have been logged out successfully.', 'success')

    session.pop('oauth_token_data', None)
    logout_user()
    session.clear()

    return redirect('/')


# @scheduler.task('interval', id='dynamic_job', minutes=20)
# def job():
#     print("🧠 This runs every 20 seconds")

scheduler.add_job(
    id='spotify_user_pipeline',
    func=process_user_data,
    trigger='interval',
    minutes=20,
    kwargs={'object': app}
)


if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'development':

        app.run(debug=True)  # Only run Flask's built-in server in development mode
