import logging
from models import User
from oauth import SpotifyUserService
from spotifyextractors import  *
from chromaclass import client_config,Chroma

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chroma = Chroma(client_config)
COLLECTION_NAMES = ['user_details','followed_artists','user_albums','new_releases','user_audio_books','user_saved_episodes','user_playback_state','user_available_devices','user_played_tracks','user_queue','user_playlist','featured_playlist','user_saved_shows']

user_data = User.query.all()
access_token = [(user.token,user.refresh_token,user.id) for user in user_data]


for index,value_tuple in enumerate(access_token):
    try:


        user_id = value_tuple[2]

        spotify_user_service_instance = SpotifyUserService(value_tuple[0])
        logger.info(f"\n==== Starting processing for user {user_id} ====")
        docs = []
        try:
            user_details = spotify_user_service_instance.get_user_details()
            user_details = extract_spotify_user_info(user_details)
            user_details_embeddings = get_spotify_user_embeddings(user_details)
            logger.info(f"[{user_id}] Fetched user_details")
        except Exception as e:
            docs.append([])
            logger.warning(f"[{user_id}] Failed user_details: {e}")

        try:
            followed_artists = spotify_user_service_instance.get_followed_artists()
            followed_artists = extract_spotify_artists_info(followed_artists)
            followed_artists_embeddings = get_spotify_artists_embeddings(followed_artists)
            logger.info(f"[{user_id}] Fetched followed_artists")
        except Exception as e:
            docs.append([])
            logger.warning(f"[{user_id}] Failed followed_artists: {e}")

        try:
            user_albums = spotify_user_service_instance.get_user_albums()
            user_albums = extract_spotify_user_info(user_albums)
            user_albums_embeddings = get_album_embeddings(user_albums)
            logger.info(f"[{user_id}] Fetched user_albums")
        except Exception as e:
            docs.append([])
            logger.warning(f"[{user_id}] Failed to fetch user_albums: {e}")

        try:
            new_releases= spotify_user_service_instance.get_new_releases()
            new_releases = extract_new_releases(new_releases)
            new_releases_embeddings = get_new_releases_embeddings(new_releases)
            logger.info(f"[{user_id}] Fetched new_releases")
        except Exception as e:
            docs.append([])
            logger.warning(f"[{user_id}] Failed new_releases: {e}")


        try:
            user_audio_books = spotify_user_service_instance.get_user_audio_books()
            user_audio_books = extract_user_audiobooks_list(user_audio_books)
            user_audio_books_embeddings = get_user_audiobooks_embeddings(user_audio_books)
            logger.info(f"[{user_id}] Fetched user_audio_books")
        except Exception as e:
            docs.append([])
            logger.warning(f"[{user_id}] Failed user_audio_books: {e}")


        user_saved_episodes = spotify_user_service_instance.get_user_saved_episodes()
        user_saved_episodes = extract_saved_episode_details(user_saved_episodes)
        user_saved_episodes_embeddings = get_saved_episode_embeddings(user_saved_episodes)
        logger.info(f"[{user_id}] Fetched user_saved_episodes")

        user_playback_state = spotify_user_service_instance.get_user_playback_state()
        user_playback_state = extract_spotify_playback_status(user_playback_state)
        user_playback_state_embeddings = get_spotify_playback_status_embeddings(user_playback_state)
        logger.info(f"[{user_id}] Fetched user_playback_state")

        user_available_devices = spotify_user_service_instance.get_available_devices()
        user_available_devices = extract_device_info(user_available_devices)
        user_available_devices_embeddings = get_device_info_embeddings(user_available_devices)
        logger.info(f"[{user_id}] Fetched user_available_devices")

        user_played_tracks = spotify_user_service_instance.get_recently_played_track()
        user_played_tracks = extract_recently_played_spotify_tracks(user_played_tracks)
        user_played_tracks_embeddings = get_recently_played_spotify_tracks_embeddings(user_played_tracks)
        logger.info(f"[{user_id}] Fetched user_played_tracks")

        user_queue = spotify_user_service_instance.get_users_queue()
        user_queue = extract_currently_playing_and_queue(user_queue)
        user_queue_embeddings = get_currently_playing_and_queue_embeddings(user_queue)
        logger.info(f"[{user_id}] Fetched user_queue")

        user_playlist = spotify_user_service_instance.get_user_playlist()
        user_playlist = extract_user_playlists_data(user_playlist)
        user_playlist_embeddings = get_user_playlists_embeddings(user_playlist)
        logger.info(f"[{user_id}] Fetched user_playlist")

        featured_playlist = spotify_user_service_instance.get_featured_playlist()
        featured_playlist = extract_featured_playlists_data(featured_playlist)
        featured_playlist_embeddings = get_featured_playlists_embeddings(featured_playlist)
        logger.info(f"[{user_id}] Fetched featured_playlist")

        user_saved_shows= spotify_user_service_instance.get_users_saved_shows()
        user_saved_shows = extract_saved_shows_data(user_saved_shows)
        user_saved_shows_embeddings = get_saved_shows_embeddings(user_saved_shows)
        logger.info(f"[{user_id}] Fetched user_saved_shows")

        logger.info(f"\n==== ended processing for user {user_id} ====")

        docs = [user_details, followed_artists, user_albums, new_releases, user_audio_books,
                            user_saved_episodes, user_playback_state, user_available_devices, user_played_tracks,
                            user_queue, user_playlist, featured_playlist, user_saved_shows]

        for pos,collection_name in enumerate(COLLECTION_NAMES):
            if not docs[pos]:  # Skip if document list is empty or None
                logger.info(f"[{user_id}] Skipped empty collection: {collection_name}")
                continue
            if chroma.collection_exist(f'{user_id}{collection_name}'):
                chroma.use_collection(f'{user_id}{collection_name}')
                chroma.update_to_collection({'documents':docs[pos],'metadatas': [{'source': collection_name} for _ in docs[pos]],'ids': [f'{collection_name}_{pos}_{i}' for i in range(len(docs[pos]))]},f'{user_id}{collection_name}')
                logger.info(f"[{user_id}] Updated collection: {collection_name} with {len(docs[pos])} documents")

            else:
                chroma.create_collection(f'{user_id}{collection_name}',metadata={'type':collection_name})
                chroma.add_to_collection({'documents':docs[pos],'metadatas': [{'source': collection_name} for _ in docs[pos]],'ids': [f'{collection_name}_{pos}_{i}' for i in range(len(docs[pos]))]},f'{user_id}{collection_name}')
                logger.info(f"[{user_id}] Created collection: {user_id}{collection_name} with {len(docs[pos])} documents")
    except Exception as e:
        logger.error(f"[GLOBAL] Error processing user {user_id}: {e}")

