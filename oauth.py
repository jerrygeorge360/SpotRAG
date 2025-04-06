from abc import abstractmethod, ABC
import http.client
from http.client import HTTPException
from urllib.parse import quote, urlencode
from uuid import uuid4, UUID
from typing import Union, Dict, Any
import os
import json
import base64

from dotenv import load_dotenv

load_dotenv()

class TwitchOauthBase(ABC):
    @abstractmethod
    def validate_token(self, access_token):
        ...

    @abstractmethod
    def authorize(self, authorize_obj):
        ...

    @abstractmethod
    def get_redirect_data(self, code, scope, state):
        ...

    @abstractmethod
    def get_token(self, authorize_obj):
        ...

    @abstractmethod
    def refresh_access_token(self,authorize_obj):
        ...

class Authorization:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, response_type: str, scope: list[str],
                 state: UUID = uuid4()):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._response_type = response_type
        self._scope = scope
        self._state = state.hex
        self._code = Union[str, None]
        self._error = Union[str, None]
        self._description = Union[str, None]
        self._grant_type = 'authorization_code'
        self._access_token = Union[str, None]

    @property
    def client_id(self) -> str:
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = value

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, value):
        self._redirect_uri = value

    @property
    def response_type(self) -> str:
        return self._response_type

    @response_type.setter
    def response_type(self, value):
        self._response_type = value

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def scope(self) -> str:
        scope_string = ' '.join(self._scope)
        encoded_scope_string = quote(scope_string)
        return encoded_scope_string

    @scope.setter
    def scope(self, value):
        self._scope = value

    @property
    def code(self) -> Union[str, None]:
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    @property
    def grant_type(self) -> str:
        return self._grant_type

    @grant_type.setter
    def grant_type(self, value):
        self._grant_type = value

    @property
    def error(self) -> Union[str, None]:
        return self._error

    @error.setter
    def error(self, value):
        self._error = value

    @property
    def description(self) -> Union[str, None]:
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def access_token(self) -> Union[str, None]:
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

class GithubOauthAccessCode(TwitchOauthBase):
    base_url = 'github.com'

    def __init__(self):
        self.conn = http.client.HTTPSConnection(GithubOauthAccessCode.base_url)

    def validate_token(self, access_token: str):
        endpoint = '/oauth2/validate'
        header = {'Authorization': f'OAUTH {access_token}'}
        self.conn.request("GET", endpoint, headers=header)

    def authorize(self, authorize_obj: Authorization):
        endpoint = 'https://github.com/login/oauth/authorize'
        query = f'?response_type={authorize_obj.response_type}&client_id={authorize_obj.client_id}&redirect_uri={authorize_obj.redirect_uri}' \
                f'&scope={authorize_obj.scope}&state={authorize_obj.state}&client=github'
        return endpoint + query

    def get_redirect_data(self, authorize_obj: Authorization, **kwargs):
        try:
            access_code = kwargs['data']['code']
            state = kwargs['data']['state']
            authorize_obj.code = access_code
            authorize_obj.state = state

        except KeyError:
            error = kwargs['data']['error']
            error_description = kwargs['data']['error_description']
            state = kwargs['data']['state']
            authorize_obj.error = error
            authorize_obj.description = error_description
            authorize_obj.state = state

    def get_token(self, authorize_obj: Authorization):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        endpoint = '/login/oauth/access_token'
        body = {'client_id': authorize_obj.client_id, 'client_secret': authorize_obj.client_secret,
                'code': authorize_obj.code, 'grant_type': authorize_obj.grant_type,
                'redirect_uri': authorize_obj.redirect_uri}
        encoded_params = urlencode(body)

        try:
            self.conn.request('POST', endpoint, body=encoded_params, headers=headers)
            res = self.conn.getresponse()



            if res.status != 200:
                raise HTTPException(f"Error {res.status}: {res.reason}")

            data = res.read()
            json_data:str = data.decode('utf-8')
            access_token = json_data.split('&')[0].split('=')[1]
            access_token = access_token
            if access_token is None:
                raise ValueError("Access token not found in the response")

            authorize_obj.access_token = access_token
            return access_token

        except HTTPException as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except json.JSONDecodeError as json_err:
            print('here')
            print(f"Failed to parse JSON response: {json_err}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

        # TODO: store access_token and refresh_token in database.

    def refresh_access_token(self, authorize_obj):
        # TODO: write a query to get the stored refresh token
        refresh_token = ...  # Retrieve from storage
        endpoint = '/oauth2/token'
        body = {
            'client_id': authorize_obj.client_id,
            'client_secret': authorize_obj.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        json_body = json.dumps(body)
        self.conn.request('POST', endpoint, body=json_body)
        res = self.conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode('utf-8'))
        access_token = json_data['access_token']
        authorize_obj.access_token = access_token
        return json_data


class TwitchOauthAccessCode(TwitchOauthBase):
    base_url = 'id.twitch.tv'

    def __init__(self):
        self.conn = http.client.HTTPSConnection(TwitchOauthAccessCode.base_url)

    def validate_token(self, access_token: str):
        endpoint = '/oauth2/validate'
        header = {'Authorization': f'OAUTH {access_token}'}
        self.conn.request("GET", endpoint, headers=header)

    def authorize(self, authorize_obj: Authorization):
        endpoint = 'https://id.twitch.tv/oauth2/authorize'
        query = f'?response_type={authorize_obj.response_type}&client_id={authorize_obj.client_id}&redirect_uri={authorize_obj.redirect_uri}' \
                f'&scope={authorize_obj.scope}&state={authorize_obj.state}&client=twitch'
        return endpoint + query

    def get_redirect_data(self, authorize_obj: Authorization, **kwargs):
        try:
            access_code = kwargs['data']['code']
            state = kwargs['data']['state']
            authorize_obj.code = access_code
            authorize_obj.state = state

        except KeyError:
            error = kwargs['data']['error']
            error_description = kwargs['data']['error_description']
            state = kwargs['data']['state']
            authorize_obj.error = error
            authorize_obj.description = error_description
            authorize_obj.state = state

    def get_token(self, authorize_obj: Authorization):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        endpoint = '/oauth2/token'
        body = {'client_id': authorize_obj.client_id, 'client_secret': authorize_obj.client_secret,
                'code': authorize_obj.code, 'grant_type': authorize_obj.grant_type,
                'redirect_uri': authorize_obj.redirect_uri}
        encoded_params = urlencode(body)
        try:
            self.conn.request('POST', endpoint, body=encoded_params, headers=headers)
            res = self.conn.getresponse()

            if res.status != 200:
                raise HTTPException(f"Error {res.status}: {res.reason}")

            data = res.read()
            json_data = json.loads(data.decode('utf-8'))

            access_token = json_data.get('access_token')
            if access_token is None:
                raise ValueError("Access token not found in the response")

            authorize_obj.access_token = access_token
            return json_data

        except HTTPException as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

        # TODO: store access_token and refresh_token in database.

    def refresh_access_token(self, authorize_obj):
        #TODO: write a query to get the stored refresh token
        refresh_token = ...  # Retrieve from storage
        endpoint = '/oauth2/token'
        body = {
            'client_id': authorize_obj.client_id,
            'client_secret': authorize_obj.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        json_body = json.dumps(body)
        self.conn.request('POST', endpoint, body=json_body)
        res = self.conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode('utf-8'))
        access_token = json_data['access_token']
        authorize_obj.access_token = access_token
        return json_data

class SpotifyOauthAccessCode(TwitchOauthBase):
    base_url = 'accounts.spotify.com'

    def __init__(self):
        self.conn = http.client.HTTPSConnection(SpotifyOauthAccessCode.base_url)

    def validate_token(self, access_token: str):
        endpoint = '/oauth2/validate'
        header = {'Authorization': f'OAUTH {access_token}'}
        self.conn.request("GET", endpoint, headers=header)

    def authorize(self, authorize_obj: Authorization):
        endpoint = 'https://accounts.spotify.com/authorize'
        query = f'?response_type={authorize_obj.response_type}&client_id={authorize_obj.client_id}&redirect_uri={authorize_obj.redirect_uri}' \
                f'&scope={authorize_obj.scope}&state={authorize_obj.state}&client=spotify'
        return endpoint + query
    def get_redirect_data(self, authorize_obj: Authorization, **kwargs):
        try:
            access_code = kwargs['data']['code']
            state = kwargs['data']['state']
            authorize_obj.code = access_code
            authorize_obj.state = state

        except KeyError:
            error = kwargs['data']['error']
            error_description = kwargs['data']['error_description']
            state = kwargs['data']['state']
            authorize_obj.error = error
            authorize_obj.description = error_description
            authorize_obj.state = state
    def get_token(self, authorize_obj: Authorization):
        client_id = authorize_obj.client_id
        client_secret = authorize_obj.client_secret
        auth_str = f"{client_id}:{client_secret}"
        base64_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {'Content-Type': 'application/x-www-form-urlencoded','Authorization':f'Basic {base64_auth}'}
        endpoint = '/api/token'
        body = {'client_id': authorize_obj.client_id, 'client_secret': authorize_obj.client_secret,
                'code': authorize_obj.code, 'grant_type': authorize_obj.grant_type,
                'redirect_uri': authorize_obj.redirect_uri}
        encoded_params = urlencode(body)
        try:
            self.conn.request('POST', endpoint, body=encoded_params, headers=headers)
            res = self.conn.getresponse()

            if res.status != 200:
                raise HTTPException(f"Error {res.status}: {res.reason}")

            data = res.read()
            json_data = json.loads(data.decode('utf-8'))

            access_token = json_data.get('access_token')
            if access_token is None:
                raise ValueError("Access token not found in the response")

            authorize_obj.access_token = access_token
            return json_data

        except HTTPException as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def refresh_access_token(self, authorize_obj):
        # TODO: write a query to get the stored refresh token
        refresh_token = ...  # Retrieve from storage
        endpoint = '/oauth2/token'
        body = {
            'client_id': authorize_obj.client_id,
            'client_secret': authorize_obj.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        json_body = json.dumps(body)
        self.conn.request('POST', endpoint, body=json_body)
        res = self.conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode('utf-8'))
        access_token = json_data['access_token']
        authorize_obj.access_token = access_token
        return json_data

# class OauthFacade:
#
#     twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
#     twitch_client_secret = os.getenv('TWITCH_CLIENT_SECRET_KEY')
#     twitch_redirect_uri = os.getenv('TWITCH_REDIRECT_URI')
#
#     github_client_id = os.getenv('GITHUB_ID')
#     github_client_secret=os.getenv('GITHUB_SECRET_KEY')
#     github_redirect_uri=os.getenv('GITHUB_REDIRECT_URI')
#
#     spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
#     spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET_KEY')
#     spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
#
#
#     # Check if the environment variables are set
#     if not all([twitch_client_id, twitch_client_secret, twitch_redirect_uri]):
#         raise EnvironmentError("Missing required environment variables for Twitch OAuth.")
#     if not all([github_client_id, github_client_secret, github_redirect_uri]):
#         raise EnvironmentError("Missing required environment variables for Github OAuth.")
#     if not all([spotify_client_id, spotify_client_secret, spotify_redirect_uri]):
#         raise EnvironmentError("Missing required environment variables for Spotify OAuth.")
#
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, 'instance'):
#             cls.instance = super(OauthFacade, cls).__new__(cls)
#         return cls.instance
#
#     def __init__(self,client:str=None, response_type: str = None, scope: list = None):
#         self.response_type = response_type
#         self.scope = scope
#         print(client)
#         if client == 'twitch':
#             self.authorize_obj = Authorization(
#                 client_id=OauthFacade.twitch_client_id,
#                 client_secret=OauthFacade.twitch_client_secret,
#                 redirect_uri=OauthFacade.twitch_redirect_uri,
#                 response_type=self.response_type,
#                 scope=scope
#             )
#             self.client = TwitchOauthAccessCode()
#         elif client =='github':
#             self.authorize_obj = Authorization(
#                 client_id=OauthFacade.github_client_id,
#                 client_secret=OauthFacade.github_client_secret,
#                 redirect_uri=OauthFacade.github_redirect_uri,
#                 response_type=self.response_type,
#                 scope=scope
#             )
#             self.client = GithubOauthAccessCode()
#         elif client == 'spotify':
#             self.authorize_obj = Authorization(
#                 client_id=OauthFacade.spotify_client_id,
#                 client_secret=OauthFacade.spotify_client_secret,
#                 redirect_uri=OauthFacade.spotify_redirect_uri,
#                 response_type=self.response_type,
#                 scope=scope
#             )
#             self.client = SpotifyOauthAccessCode()
#         else:
#             raise ValueError('must be either twitch  or github or spotify keyword')
#
#     def get_auth_link(self):
#         authorization_url = self.client.authorize(authorize_obj=self.authorize_obj)
#         print(authorization_url)
#         return authorization_url
#
#     def _get_access_code(self, **kwargs):
#         self.client.get_redirect_data(authorize_obj=self.authorize_obj, data=kwargs['data'])
#
#     def get_access_token(self, **kwargs):
#
#         if kwargs['data'].get('code'):
#             self._get_access_code(data=kwargs['data'])
#             access_token_data = self.client.get_token(authorize_obj=self.authorize_obj)
#             return access_token_data
#         else:
#             self._get_access_code(data=kwargs['data'])
#             return {'msg': 'authorization failed'}
#
#     def refresh_token(self):
#         self.client.refresh_access_token(self.authorize_obj)

class OauthFacade:
    OAUTH_CONFIG = {
        'twitch': {
            'env': {
                'id': 'TWITCH_CLIENT_ID',
                'secret': 'TWITCH_CLIENT_SECRET_KEY',
                'redirect': 'TWITCH_REDIRECT_URI'
            },
            'class': lambda: TwitchOauthAccessCode()
        },
        'github': {
            'env': {
                'id': 'GITHUB_ID',
                'secret': 'GITHUB_SECRET_KEY',
                'redirect': 'GITHUB_REDIRECT_URI'
            },
            'class': lambda: GithubOauthAccessCode()
        },
        'spotify': {
            'env': {
                'id': 'SPOTIFY_CLIENT_ID',
                'secret': 'SPOTIFY_CLIENT_SECRET_KEY',
                'redirect': 'SPOTIFY_REDIRECT_URI'
            },
            'class': lambda: SpotifyOauthAccessCode()
        }
    }

    _instances = {}

    def __new__(cls, client: str, *args, **kwargs):
        if client not in cls._instances:
            cls._instances[client] = super().__new__(cls)
        return cls._instances[client]

    def __init__(self, client: str, response_type: str = None, scope: list = None):
        self.client_key = client.lower()
        config = self.OAUTH_CONFIG.get(self.client_key)
        if not config:
            raise ValueError(f"Invalid client type: {client}. Must be one of {list(self.OAUTH_CONFIG.keys())}")

        # Load environment variables dynamically
        self.client_id = os.getenv(config['env']['id'])
        self.client_secret = os.getenv(config['env']['secret'])
        self.redirect_uri = os.getenv(config['env']['redirect'])

        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise EnvironmentError(f"Missing required environment variables for {self.client_key} OAuth.")

        self.response_type = response_type
        self.scope = scope or []

        # Build Authorization and access handler
        self.authorize_obj = Authorization(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            response_type=self.response_type,
            scope=self.scope
        )
        self.client = config['class']()

    def get_auth_link(self) -> str:
        """Get OAuth authorization URL."""
        return self.client.authorize(authorize_obj=self.authorize_obj)

    def _get_access_code(self, data: dict):
        """Extract auth code or token from callback data."""
        self.client.get_redirect_data(authorize_obj=self.authorize_obj, data=data)

    def get_access_token(self, data: dict) -> dict:
        """Exchange auth code for access token."""
        if not data.get('code'):
            return {'msg': 'authorization failed', 'error': 'missing code in callback'}

        self._get_access_code(data=data)
        return self.client.get_token(authorize_obj=self.authorize_obj)

    def refresh_token(self) -> dict:
        """Refresh access token (if supported)."""
        return self.client.refresh_access_token(self.authorize_obj)




class TwitchUserBase(ABC):
    @abstractmethod
    def get_user_details(self):
        ...

class GithubUserService(TwitchUserBase):
    base_url = 'api.github.com'

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.conn = http.client.HTTPSConnection(GithubUserService.base_url)
        github_secret_key = os.environ.get('GITHUB_ID')

        self.headers = {'Authorization': f'Bearer {self.access_token}',"Accept": "application/json", 'Client-Id':github_secret_key, "User-Agent": "shortcast" }

    def get_user_details(self):
        endpoint = '/user'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_details = json.loads(data.decode('utf-8'))
        return user_details

class SpotifyUserService(TwitchUserBase):
    base_url = 'api.spotify.com'

    def __init__(self,access_token:str):
        self.access_token = access_token
        self.conn = http.client.HTTPSConnection(SpotifyUserService.base_url)
        self.headers = {'Authorization': f'Bearer {self.access_token}', "Accept": "application/json"}
    # users
    def get_user_details(self):
        endpoint = '/v1/me'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_details = json.loads(data.decode('utf-8'))
        return user_details

    def get_user_top_items(self,offset='',limit='',type_of_item:str='tracks'):
        endpoint = f'/v1/me/top/{type_of_item}?limit={limit}&offset={offset}'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_top_items = json.loads(data.decode('utf-8'))
        return user_top_items

    def targeted_user_details(self,user_id):
        endpoint = f'/v1/users/{user_id}'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_details = json.loads(data.decode('utf-8'))
        return user_details

    def get_followed_artists(self):
        endpoint = '/v1/me/following'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        followed_artists = json.loads(data.decode('utf-8'))
        return followed_artists

    # albums
    def get_user_albums(self):
        endpoint = '/v1/me/albums'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_saved_albums = json.loads(data.decode('utf-8'))
        return user_saved_albums

    def get_new_releases(self):
        endpoint = '/v1/browse/new-releases'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        new_releases = json.loads(data.decode('utf-8'))
        return new_releases

    def get_user_audio_books(self):
        endpoint = '/v1/me/audiobooks'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        saved_audio_books = json.loads(data.decode('utf-8'))
        return saved_audio_books

    def get_user_saved_episodes(self):
        endpoint ='/v1/me/episodes'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        saved_episodes = json.loads(data.decode('utf-8'))
        return saved_episodes


    # player
    def get_user_playback_state(self):
        endpoint ='/v1/me/player'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        playback_state = json.loads(data.decode('utf-8'))
        return playback_state

    def get_available_devices(self):
        endpoint = '/v1/me/player/devices'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        available_devices = json.loads(data.decode('utf-8'))
        return available_devices

    def get_recently_played_track(self):
        endpoint = '/v1/me/player/recently-played'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        recently_played = json.loads(data.decode('utf-8'))
        return recently_played

    def get_users_queue(self):
        endpoint = '/v1/me/player/queue'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_queue = json.loads(data.decode('utf-8'))
        return user_queue

    def get_user_playlist(self):
        endpoint = '/v1/me/playlists'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        playlists = json.loads(data.decode('utf-8'))
        return playlists

    def get_featured_playlist(self):
        endpoint = '/v1/browse/featured-playlists'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        featured_playlists = json.loads(data.decode('utf-8'))
        return featured_playlists

    def get_users_saved_shows(self):
        endpoint = '/v1/me/shows'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_shows = json.loads(data.decode('utf-8'))
        return user_shows

class TwitchUserService(TwitchUserBase):
    base_url = 'api.twitch.tv'

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.conn = http.client.HTTPSConnection(TwitchUserService.base_url)
        self.headers = {'Authorization': f'Bearer {self.access_token}', 'Client-Id': os.environ.get('TWITCH_CLIENT_ID')}

    def get_user_details(self):
        endpoint = '/helix/users'
        self.conn.request('GET', endpoint, headers=self.headers)
        response = self.conn.getresponse()
        data = response.read()
        user_details = json.loads(data.decode('utf-8'))
        return user_details

def extract_twitch_info(data: Dict[str, Any], key: str) -> Union[str, None]:
    user_info = None
    if "data" in data and len(data["data"]) > 0:
        user_data = data["data"][0]
        user_info = user_data.get(key)
        if user_info is None:
            print(f"Key '{key}' not found in user data.")
        return user_info
    return None

def extract_github_info(data: Dict[str, Any], key: str) -> Union[str, None]:
    user_info = None
    if data:
        user_data = data
        user_info = user_data.get(key)
        if user_info is None:
            print(f"Key '{key}' not found in user data.")
            return 'none'
        return user_info
    return None