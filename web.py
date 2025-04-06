from flask import Blueprint, render_template, request, url_for, session, redirect, flash, jsonify
from dotenv import load_dotenv
import logging
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GITHUB_CLIENT_ID = os.getenv('GITHUB_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_SECRET_KEY')
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
        return redirect(url_for('views.login'))

    if code:
        data = {'code': code, 'state': state, 'scope': scope}
        try:
            oauth_obj = OauthFacade(client=client, response_type="code", scope=["user:read:email"])
            access_token = oauth_obj.get_access_token(data=data)
            access_data = {'access_token': access_token, 'client': client}
            session['oauth_token_data'] = access_data
            logger.info(f'Saved token: {access_token}')

            response = login_user_()
            status_code = response[1] if isinstance(response, tuple) else response
            logger.info(response)
            if status_code == 201:
                flash('Logged in successfully!', 'success')
                return redirect(url_for('views.podcast'))
            elif hasattr(response, 'status') and response.status == 'error':
                flash('Failed to log in.', 'error')
                return redirect(url_for('views.login'))

            else:
                logger.warning('Unexpected login response.')
                flash('An unexpected error occurred during login.', 'error')
                return redirect(url_for('views.login'))

        except Exception as e:
            logger.exception('Failed during token handling.')
            flash('An error occurred during authentication.', 'error')
            return redirect(url_for('views.login'))

    # Fallback for any unexpected scenario
    flash('Invalid or missing code parameter.', 'error')
    return redirect(url_for('views.login'))



@views_bp.route('/logout')
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

    access_data = session.pop('oauth_token_data', None)
    if access_data and 'access_token' in access_data:
        try:
            token = access_data['access_token']

            response = requests.delete(
                f'https://api.github.com/applications/{GITHUB_CLIENT_ID}/grant',
                auth=(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET),
                json={"access_token": token}
            )

            if response.status_code == 204:
                logger.info('GitHub OAuth token successfully invalidated.')
            else:
                logger.warning(
                    f'Failed to invalidate GitHub OAuth token. Status: {response.status_code}, Response: {response.text}'
                )

        except Exception as e:
            logger.exception('Error while invalidating GitHub OAuth token.')

    logout_user()
    session.clear()

    return redirect(url_for('views.index'))
