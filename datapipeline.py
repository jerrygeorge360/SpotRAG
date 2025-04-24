import logging
from models import User
from oauth import SpotifyUserService
from spotifyextractors import  *
from chromaclass import client_config,Chroma
import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chroma = Chroma(client_config)
COLLECTION_NAMES = ['user_details','followed_artists','user_albums','new_releases','user_audio_books','user_saved_episodes','user_available_devices','user_played_tracks','user_queue','user_playlist','featured_playlist','user_saved_shows']
def process_user_data(object,user_id=None):
    """
    Processes user data by interacting with the Spotify API and updating or creating document collections
    using Chroma for user-specific data embeddings.

    This function retrieves various types of user data, including personal details, followed artists, albums, new releases,
    audiobooks, saved episodes, available devices, recently played tracks, queue, playlists, featured playlists, and
    saved shows. For each data type, the corresponding details are processed to extract meaningful information and
    generate embeddings, which are then used to update or create collections in the database.

    Args:
        object (Flask.application): The Flask application context object required for database access.

    Raises:
        Exception: Handles exceptions in data retrieval, embedding generation, and collection updates on a per-user basis.

    """
    with object.app_context():
        if not user_id:
            user_data = User.query.filter_by(user_id=user_id).first()
        else:
            user_data = User.query.all()
        access_token = [(user.access_token,user.refresh_token,user.id) for user in user_data]

        for index,value_tuple in enumerate(access_token):
            try:


                user_id = value_tuple[2]

                spotify_user_service_instance = SpotifyUserService(value_tuple[0],refresh_token=value_tuple[1],client_id=client_id,client_secret=client_secret)
                logger.info(f"\n==== Starting processing for user {user_id} ====")
                docs = []
                try:
                    user_details = spotify_user_service_instance.get_user_details()
                    print(user_details)
                    user_details = extract_spotify_user_info(user_details)
                    print(user_details)
                    user_details_embeddings = get_spotify_user_embeddings(user_details)
                    print(user_details_embeddings)
                    logger.info(f"[{user_id}] Fetched user_details")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_details: {e}")

                try:
                    followed_artists = spotify_user_service_instance.get_followed_artists()
                    print(followed_artists)
                    followed_artists = extract_spotify_artists_info(followed_artists)
                    print(followed_artists)
                    followed_artists_embeddings = get_spotify_artists_embeddings(followed_artists)
                    print(followed_artists_embeddings)
                    logger.info(f"[{user_id}] Fetched followed_artists")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed followed_artists: {e}")

                try:
                    user_albums = spotify_user_service_instance.get_user_albums()
                    print(user_albums)
                    user_albums = extract_album_info(user_albums)
                    print(user_albums)
                    user_albums_embeddings = get_album_embeddings(user_albums)
                    print(user_albums_embeddings)
                    logger.info(f"[{user_id}] Fetched user_albums")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed to fetch user_albums: {e}")

                try:
                    new_releases= spotify_user_service_instance.get_new_releases()
                    print(new_releases)
                    new_releases = extract_new_releases(new_releases)
                    print(new_releases)
                    if get_new_releases_embeddings(new_releases):
                        new_releases_embeddings = get_new_releases_embeddings(new_releases)[0]
                    new_releases_embeddings = get_new_releases_embeddings(new_releases)
                    print(new_releases_embeddings)
                    logger.info(f"[{user_id}] Fetched new_releases")


                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed new_releases: {e}")


                try:
                    user_audio_books = spotify_user_service_instance.get_user_audio_books()
                    print(user_audio_books)
                    user_audio_books = extract_user_audiobooks_list(user_audio_books)
                    print(user_audio_books)
                    user_audio_books_embeddings = get_user_audiobooks_embeddings(user_audio_books)
                    print(user_audio_books_embeddings)
                    logger.info(f"[{user_id}] Fetched user_audio_books")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_audio_books: {e}")

                try:
                    user_saved_episodes = spotify_user_service_instance.get_user_saved_episodes()
                    print(user_saved_episodes)
                    user_saved_episodes = extract_saved_episode_details(user_saved_episodes)
                    print(user_saved_episodes)
                    if get_saved_episode_embeddings(user_saved_episodes):
                        user_saved_episodes_embeddings = get_saved_episode_embeddings(user_saved_episodes)[0]
                    user_saved_episodes_embeddings = get_saved_episode_embeddings(user_saved_episodes)
                    print(user_saved_episodes_embeddings)
                    logger.info(f"[{user_id}] Fetched user_saved_episodes")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_saved_episodes: {e}")

                try:
                    user_available_devices = spotify_user_service_instance.get_available_devices()
                    print(user_available_devices)
                    user_available_devices = extract_device_info(user_available_devices)
                    print(user_available_devices)
                    if get_device_info_embeddings(user_available_devices):
                        user_available_devices_embeddings = get_device_info_embeddings(user_available_devices)[0]
                    else:
                        user_available_devices_embeddings = get_device_info_embeddings(user_available_devices)
                    print(user_available_devices_embeddings)
                    logger.info(f"[{user_id}] Fetched user_available_devices")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_available_devices: {e}")

                try:
                    user_played_tracks = spotify_user_service_instance.get_recently_played_track()
                    print(user_played_tracks)
                    user_played_tracks = extract_recently_played_spotify_tracks(user_played_tracks)
                    print(user_played_tracks)
                    user_played_tracks_embeddings = get_recently_played_spotify_tracks_embeddings(user_played_tracks)
                    print(user_played_tracks_embeddings)
                    logger.info(f"[{user_id}] Fetched user_played_tracks")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_played_track: {e}")

                try:
                    user_queue = spotify_user_service_instance.get_users_queue()
                    print(user_queue)
                    user_queue = extract_currently_playing_and_queue(user_queue)
                    print(user_queue)
                    if get_currently_playing_and_queue_embeddings(user_queue):
                        user_queue_embeddings = get_currently_playing_and_queue_embeddings(user_queue)[0]
                    else:
                        user_queue_embeddings = get_currently_playing_and_queue_embeddings(user_queue)
                    print(user_queue_embeddings)
                    logger.info(f"[{user_id}] Fetched user_queue")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_queue: {e}")


                try:
                    user_playlist = spotify_user_service_instance.get_user_playlist()
                    print(user_playlist)
                    user_playlist = extract_user_playlists_data(user_playlist)
                    print(user_playlist)
                    user_playlist_embeddings = get_user_playlists_embeddings(user_playlist)
                    print(user_playlist_embeddings)
                    logger.info(f"[{user_id}] Fetched user_playlist")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_playlist: {e}")

                try:
                    featured_playlist = spotify_user_service_instance.get_featured_playlist()
                    print(featured_playlist)
                    featured_playlist = extract_featured_playlists_data(featured_playlist)
                    print(featured_playlist)
                    featured_playlist_embeddings = get_featured_playlists_embeddings(featured_playlist)
                    print(featured_playlist_embeddings)
                    logger.info(f"[{user_id}] Fetched featured_playlist")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed featured_playlist: {e}")

                try:
                    user_saved_shows= spotify_user_service_instance.get_users_saved_shows()
                    print(user_saved_shows)
                    user_saved_shows = extract_saved_shows_data(user_saved_shows)
                    print(user_saved_shows)
                    user_saved_shows_embeddings = get_saved_shows_embeddings(user_saved_shows)
                    print(user_saved_shows_embeddings)
                    logger.info(f"[{user_id}] Fetched user_saved_shows")
                except Exception as e:
                    docs.append([])
                    logger.warning(f"[{user_id}] Failed user_saved_shows: {e}")

                logger.info(f"\n==== ended processing for user {user_id} ====")

                docs = [user_details_embeddings, followed_artists_embeddings, user_albums_embeddings, new_releases_embeddings, user_audio_books_embeddings,
                                    user_saved_episodes_embeddings, user_available_devices_embeddings, user_played_tracks_embeddings,
                                    user_queue_embeddings, user_playlist_embeddings, featured_playlist_embeddings, user_saved_shows_embeddings]

                for pos,collection_name in enumerate(COLLECTION_NAMES):
                    if not docs[pos]:  # Skip if document list is empty or None
                        logger.info(f"[{user_id}] Skipped empty collection: {collection_name}")
                        continue

                    try:
                        if chroma.collection_exist(f'{user_id}{collection_name}'):
                            chroma.use_collection(f'{user_id}{collection_name}')
                            chroma.update_to_collection({'documents':docs[pos],'metadatas': [{'source': collection_name} for _ in docs[pos]],'ids': [f'{collection_name}_{pos}_{i}' for i in range(len(docs[pos]))]},f'{user_id}{collection_name}')
                            logger.info(f"[{user_id}] Updated collection: {collection_name} with {len(docs[pos])} documents")

                        else:
                            chroma.create_collection(f'{user_id}{collection_name}',metadata={'type':collection_name})
                            print(f'{user_id}{collection_name}')
                            print('this is doc pso')
                            print(docs[pos])
                            chroma.add_to_collection({'documents':docs[pos],'metadatas': [{'source': collection_name} for _ in docs[pos]],'ids': [f'{collection_name}_{pos}_{i}' for i in range(len(docs[pos]))]},f'{user_id}{collection_name}')
                            logger.info(f"[{user_id}] Created collection: {user_id}{collection_name} with {len(docs[pos])} documents")
                    except Exception as e:
                        logger.error(f"[{user_id}] Error handling collection {collection_name}: {e}")
            except Exception as e:
                logger.error(f"[GLOBAL] Error processing user {user_id}: {e}")

