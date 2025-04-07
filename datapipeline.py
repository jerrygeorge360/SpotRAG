from models import User
from oauth import SpotifyUserService
from spotifyextractors import  *
from chromaclass import client_config,Chroma


user_data = User.query.all()
access_token = [(user.token,user.refresh_token) for user in user_data]

for index,value_tuple in enumerate(access_token):
    spotify_user_service_instance = SpotifyUserService(value_tuple[0])

    user_details = spotify_user_service_instance.get_user_details()
    user_details = extract_spotify_user_info(user_details)
    user_details_embeddings = get_spotify_user_embeddings(user_details)

    followed_artists = spotify_user_service_instance.get_followed_artists()
    followed_artists = extract_spotify_artists_info(followed_artists)
    followed_artists_embeddings = get_spotify_artists_embeddings(followed_artists)

    user_albums = spotify_user_service_instance.get_user_albums()
    user_albums = extract_spotify_user_info(user_albums)
    user_albums_embeddings = get_album_embeddings(user_albums)


    new_releases= spotify_user_service_instance.get_new_releases()
    new_releases = extract_new_releases(new_releases)
    new_releases_embeddings = get_new_releases_embeddings(new_releases)




    user_audio_books = spotify_user_service_instance.get_user_audio_books()
    user_audio_books = extract_user_audiobooks_list(user_audio_books)
    user_audio_books_embeddings = get_user_audiobooks_embeddings(user_audio_books)


    user_saved_episodes = spotify_user_service_instance.get_user_saved_episodes()
    user_saved_episodes = extract_saved_episode_details(user_saved_episodes)
    user_saved_episodes_embeddings = get_saved_episode_embeddings(user_saved_episodes)





    user_playback_state = spotify_user_service_instance.get_user_playback_state()
    user_playback_state = extract_spotify_playback_status(user_playback_state)
    user_playback_state_embeddings = get_spotify_playback_status_embeddings(user_playback_state)


    user_available_devices = spotify_user_service_instance.get_available_devices()
    user_available_devices = extract_device_info(user_available_devices)
    user_available_devices_embeddings = get_device_info_embeddings(user_available_devices)


    user_played_tracks = spotify_user_service_instance.get_recently_played_track()
    user_played_tracks = extract_recently_played_spotify_tracks(user_played_tracks)
    user_played_tracks_embeddings = get_recently_played_spotify_tracks_embeddings(user_played_tracks)




    user_queue = spotify_user_service_instance.get_users_queue()
    user_queue = extract_currently_playing_and_queue(user_queue)
    user_queue_embeddings = get_currently_playing_and_queue_embeddings(user_queue)


    user_playlist = spotify_user_service_instance.get_user_playlist()
    user_playlist = extract_user_playlists_data(user_playlist)
    user_playlist_embeddings = get_user_playlists_embeddings(user_playlist)

    featured_playlist = spotify_user_service_instance.get_featured_playlist()
    featured_playlist = extract_featured_playlists_data(featured_playlist)
    featured_playlist_embeddings = get_featured_playlists_embeddings(featured_playlist)


    user_saved_shows= spotify_user_service_instance.get_users_saved_shows()
    user_saved_shows = extract_saved_shows_data(user_saved_shows)
    user_saved_shows_embeddings = get_saved_shows_embeddings(user_saved_shows)