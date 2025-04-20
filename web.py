from flask import Blueprint, render_template, request, url_for, session, redirect, flash, jsonify, Flask
from flask_login import logout_user,LoginManager,login_required
from flask_migrate import Migrate

from chromaclass import Chroma, client_config
from datapipeline import process_user_data
from helpers import login_user_process
from llmservice.instructions import first_instruction, second_instruction
from llmservice.llm import llm
from oauth import OauthFacade
from dotenv import load_dotenv
from models import User,db
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
SPOTIFY_SCOPE =[
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


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Error Handlers
@app.errorhandler(401)
def unauthorized(error):
    logger.info(error)
    return jsonify({'status': 'failed', 'error': 'You need to be logged in to access this resource'}), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@login_manager.unauthorized_handler
def unauthorized():
    flash("You need to log in to access this page.", "warning")
    return redirect(url_for(login_manager.login_view))


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    """
    Renders the login page for the application.

    This route serves the login page where users can authenticate themselves
    using OAuth providers like Twitch, GitHub, and Spotify.

    Returns:
        render_template: Renders the 'login.html' template with authentication links.
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
                return redirect('/')
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

@app.route('/prompt', methods=['POST'])
def prompt():
    data = request.json.get('prompt')
    user_id = '1'
    hallucinated_response = None
    logger.info(f'Prompt received: {data}')

    if not data:
        return jsonify({'status': 'failed', 'error': 'No prompt provided'}), 400

    try:
        # First LLM Call to get hallucinated expansion
        hallucinated_response = llm(initial_query=data, instruction=first_instruction)
        hallucinated_response.seek(0)
        hallucinated_response = hallucinated_response.read()
    except Exception as e:
        logger.error('Error during hallucinated LLM processing: %s', str(e))
        hallucinated_response = None

    try:
        joint_query = f"{hallucinated_response.strip()} {data.strip()}" if hallucinated_response else data.strip()

        # Get relevant collections
        filtered_collections = get_collection_from_prompt(model,joint_query, threshold=0.5)
        logger.info(f'Prediction result: {filtered_collections}')

        chroma_obj = Chroma(client_config)
        responses = []

        # Query each relevant collection
        for collection_name in filtered_collections:
            chroma_obj.use_collection(name=f'{user_id}{collection_name}')
            query_response = chroma_obj.query_collection(param={'query': joint_query}, name=f'{user_id}{collection_name}')

            if query_response:
                responses.append({
                    'collection': collection_name,
                    'query_response': query_response
                })
                logger.info(f"Found relevant data in {collection_name}: {query_response}")
            else:
                logger.info(f"No relevant data found in {collection_name}.")

        if not responses:
            return jsonify({'status': 'failed', 'message': 'No relevant data found for the prompt'}), 404

        # Prepare final input for second LLM call
        try:
            final_input_for_llm = f"The user is asking: {joint_query}\n\nHere is some relevant data:\n"

            for response in responses:
                collection_name = response['collection']
                query_response = response['query_response']
                final_input_for_llm += f"From collection '{collection_name}':\n{query_response}\n\n"

            generated_response = llm(initial_query=final_input_for_llm, instruction=second_instruction)
            generated_response.seek(0)
            generated_response = generated_response.read()

            return jsonify({
                'status': 'success',
                'data': generated_response
            })

        except Exception as e:
            logger.error('Error during final LLM processing: %s', str(e))
            return jsonify({'status': 'failed', 'error': 'Error generating final response'}), 500

    except Exception as e:
        logger.error(f'Error during prediction: {str(e)}')
        return jsonify({'status': 'failed', 'error': str(e)}), 500


@app.route('/logout')
def logout():
    logger.info('User initiated logout.')

    flash('You have been logged out successfully.', 'success')

    session.pop('oauth_token_data', None)
    logout_user()
    session.clear()

    return redirect('/')

@scheduler.task('interval', id='dynamic_job', seconds=20)
def job():
    print("🧠 This runs every 20 seconds")

# scheduler.add_job(
#     id='spotify_user_pipeline',
#     func=process_user_data,
#     trigger='interval',
#     hours=12,
#     kwargs={'object': app}
# )
if __name__  == '__main__':
    app.run(debug=True)