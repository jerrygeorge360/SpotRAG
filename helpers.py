from enum import Enum, auto
from  flask import session,jsonify
import logging

from datapipeline import process_user_data
from llmservice.llm import llm
from oauth import TwitchUserService, GithubUserService, SpotifyUserService, extract_twitch_info
from models import db,User
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
from spotifyextractors import extract_spotify_user_info
from oauth import extract_github_info
import json
import os
from dotenv import load_dotenv

from web import user_processing_status

load_dotenv()
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_data_from_oauth(client, access_token,refresh_token=None):
    """
    Retrieves user data from an OAuth provider.

    This function initializes the appropriate user service for a given OAuth provider
    and retrieves the user details using the provided access token. Supported OAuth
    providers include 'twitch', 'github', and 'spotify'.

    Parameters:
    client : str
        The name of the OAuth provider, such as 'twitch', 'github', or 'spotify'.

    access_token : str
        The access token provided by the OAuth provider for authenticating API requests.

    refresh_token : Optional[str]
        The refresh token issued by the OAuth provider, used to obtain a new access token
        if the current one expires. Required only for the 'spotify' provider.

    Returns:
    Any
        User details retrieved by the corresponding user service.

    Raises:
    ValueError
        If an invalid OAuth provider is passed as the `client` parameter.
    """
    if client == 'twitch':
        user_service = TwitchUserService(access_token)
    elif client == 'github':
        user_service = GithubUserService(access_token)
    elif client == 'spotify':
        user_service = SpotifyUserService(access_token,refresh_token=refresh_token,client_id=spotify_client_id,client_secret=spotify_client_secret)
    else:
        raise ValueError("Invalid OAuth provider")

    return user_service.get_user_details()


def login_user_process():
    """
    Handles the user login process using OAuth data retrieved from the session. The function validates
    OAuth data, extracts user details from multiple potential OAuth providers (Spotify, GitHub, Twitch), and
    authenticates the user. If the user doesn't exist, it creates a new user record in the database. During the
    login process, appropriate error handling and logging are performed.

    Raises:
        ValueError: Raised when the OAuth provider is invalid or the user data extraction fails.
        SQLAlchemyError: Raised on database operation errors, such as when adding a new user fails.
        Exception: Raised for any unexpected errors during user data extraction or database operations.

    Returns:
        tuple: A JSON response indicating the authentication status and containing user-related data,
        along with an HTTP status code.
    """
    oauth_data = session.get('oauth_token_data')
    client = oauth_data.get('client') if oauth_data else None
    oauth_data = oauth_data['access_token'] if isinstance(oauth_data, dict) else json.loads(oauth_data)


    if not oauth_data:
        logger.error("No OAuth data found in session, redirecting to login page")
        return jsonify({'status': 'error', 'message': 'No session data, please log in again','data':None}), 401

    access_token = oauth_data.get('access_token')
    client = client
    refresh_token = oauth_data.get('refresh_token')
    expires_in = oauth_data.get('expires_in')
    try:
        username = None
        user_id = None
        email = None
        profile_image_url = None

        user_data = get_user_data_from_oauth(client, access_token,refresh_token=refresh_token)
        if client == 'spotify':
            user_data = extract_spotify_user_info(user_data)
            user_id  = user_data.get('id')
            username = user_data.get('display_name')
            email = user_data.get('email')
            profile_image_url = user_data.get('profile_image')
        elif client == 'github':
            user_id = str(extract_github_info(user_data, 'id'))
            username = extract_github_info(user_data, 'name')
            email = extract_github_info(user_data, 'email')
            profile_image_url = extract_github_info(user_data, 'avatar_url')
        elif client == 'twitch':
            user_id = extract_twitch_info(user_data, 'id')
            username = extract_twitch_info(user_data, 'display_name')
            email = extract_twitch_info(user_data, 'email')
            profile_image_url = extract_twitch_info(user_data, 'profile_image_url')

        print(user_data)
    except ValueError as e:
        logger.error(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid OAuth provider', 'data': None}), 400

    except Exception as e:
        logger.error(f"Error fetching user details from Github: {e}")
        return jsonify({'status':'error','message':'Internal Server error','error_code':'SERVER ERROR','data':None}), 500

    logger.info(f"Fetched user details: {username}, {user_id}, {email}, {profile_image_url}")

    existing_user = db.session.execute(db.select(User).filter_by(oauth_id=user_id)).scalar_one_or_none()

    if existing_user:
        login_user(existing_user)
        session.permanent = True
        logger.info(f"User logged in: {existing_user.username}")
        logger.info(f"Current user: {current_user.username}")
        logger.info(f"Is authenticated: {current_user.is_authenticated}")
        user_data = {
            "id": existing_user.id,
            "username": existing_user.username,
            "email": existing_user.email,
            "profile_image_url": existing_user.profile_image_url,  # optional, if you have this
        }
        return jsonify({'status':'success','message':'user logged in','data':user_data}),201

    new_user = User(
        oauth_id=str(user_id),
        username=username,
        profile_image_url=profile_image_url,
        email=email,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in

    )

    try:
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session.permanent = True
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding new user: {e}")
        db.session.rollback()
        jsonify({'status':'error','message':'Internal Server error','error_code':'VALIDATION ERROR','data':None}), 500
    except Exception as e:
        logger.error(f"Unexpected error while adding new user: {e}")
        db.session.rollback()
        return jsonify({'status':'error','message':'Internal Server error','error_code':'VALIDATION ERROR','data':None}), 500

    return jsonify({'status':'success','message':'user logged in','data':user_data}),201

def build_llm_prompt(context: str, joint_query: str) -> str:
    """
    Generates a formatted large language model (LLM) prompt that structures the context
    and a new query provided, in order to facilitate understanding for downstream tasks.

    Args:
        context (str): The preceding information or conversation history that the user
            referenced in their previous interactions.
        joint_query (str): A new query or question posed by the user.

    Returns:
        str: A formatted string that combines the context and the new query in a structured
            prompt format designed for LLM input processing.
    """
    return f"""
The user previously asked:
{context}

The user is asking:
{joint_query}

Here is some information that might help answer the question:
"""
def requires_vector_data(prompt: str) -> bool:
    """
    Determine if user prompt requires external data to answer by processing it against
    a specific instruction using a large language model (LLM). The function evaluates
    the user's prompt and determines the necessity for additional vector-based data.
    It returns True if external data is required, otherwise returns False. A fallback
    mechanism is enabled to return False in case of an exception during execution.

    Args:
        prompt (str): The user prompt to evaluate. It should be a string input that needs
        assessment for whether it requires external data to provide an answer.

    Returns:
        bool: A boolean value indicating whether the user's prompt requires external
        vector-based data ('yes' evaluates to True, 'no' evaluates to False).

    Raises:
        This function does not explicitly raise or document any exceptions, but logs
        warnings and defaults to False in the event of an exception.
    """
    instruction = """
Determine if the user prompt requires external data to answer.
Reply with only 'yes' or 'no'.
"""
    try:
        decision = llm(initial_query=prompt, instruction=instruction)
        decision.seek(0)
        decision = decision.read().strip().lower()
        return decision == 'yes'
    except Exception as e:
        logger.warning(f"Fallback: assuming no vector data required due to error: {e}")
        return False  # Fallback to LLM only

def background_process(app, user_id):
    with app.app_context():
        try:
            process_user_data(app, user_id)
            user_processing_status[user_id] = 'done'
        except Exception as err:
            logger.error(f'Error in background processing: {err}')
            user_processing_status[user_id] = 'error'
