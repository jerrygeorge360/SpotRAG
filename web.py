from flask import Blueprint, render_template, request, url_for, session, redirect, flash, jsonify, Flask
from flask_login import logout_user,LoginManager
from flask_migrate import Migrate
from helpers import login_user_process
from oauth import OauthFacade
from dotenv import load_dotenv
from models import User,db
import logging
import os

load_dotenv()
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




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



@app.route('/logout')
def logout():
    """
    Logs the user out of the application, invalidates the GitHub OAuth token if it exists,
    and clears the session.

    This route performs the following actions:
    - Logs the user out of the Flask app by calling `logout_user()`.
    - If an OAuth token exists in the session, it attempts to invalidate the token
      by sending a DELETE request to the GitHub OAuth application API.
    - Clears any session data related to the OAuth token.
    - Displays a success message via `flash` indicating that the user has been logged out.
    - Redirects the user to the home page after logout.

    Responses:
        - 200: Successfully logged out and invalidated GitHub OAuth token.
        - 400: Error occurred while invalidating the GitHub OAuth token.

    Returns:
        redirect: Redirects to the home page (`views.index`).
    """


    logger.info('User initiated logout.')

    flash('You have been logged out successfully.', 'success')

    session.pop('oauth_token_data', None)
    logout_user()
    session.clear()

    return redirect('/')

if __name__  == '__main__':
    app.run(debug=True)