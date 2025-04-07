from enum import Enum, auto
from  flask import session,jsonify
import logging
from oauth import TwitchUserService, GithubUserService, SpotifyUserService, extract_twitch_info
from models import db,User
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
from spotifyextractors import extract_spotify_user_info
from oauth import extract_github_info
import json
import os
from dotenv import load_dotenv

load_dotenv()
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_data_from_oauth(client, access_token,refresh_token=None):
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

    user_data = {
        "id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email,
        "profile_image_url": existing_user.profile_image_url,  # optional, if you have thi
    }

    return jsonify({'status':'success','message':'user logged in','data':user_data}),201

