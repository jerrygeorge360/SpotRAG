# users
def extract_spotify_user_info(user_data):
    if not user_data:
        return None

    return {
        "id": user_data.get("id"),
        "display_name": user_data.get("display_name"),
        "email": user_data.get("email"),
        "country": user_data.get("country"),
        "profile_url": user_data.get("external_urls", {}).get("spotify"),
        "product": user_data.get("product"),
        "followers": user_data.get("followers", {}).get("total"),
        "profile_image": user_data.get("images")[0]["url"] if user_data.get("images") else None,
        "explicit_content_filter_enabled": user_data.get("explicit_content", {}).get("filter_enabled"),
        "explicit_content_filter_locked": user_data.get("explicit_content", {}).get("filter_locked"),
    }
def get_spotify_user_embeddings(user_data):
    user_info = extract_spotify_user_info(user_data)
    return [user_info.get("id"), user_info.get("display_name"), user_info.get("email"),
            user_info.get("country"), user_info.get("profile_url"), user_info.get("product"),
            user_info.get("followers"), user_info.get("profile_image"),
            user_info.get("explicit_content_filter_enabled"), user_info.get("explicit_content_filter_locked")]


def extract_spotify_items(data):
    extracted_items = []

    for item in data.get("items", []):
        extracted = {
            "name": item.get("name", "Unknown"),
            "genres": item.get("genres", []),
            "spotify_url": item.get("external_urls", {}).get("spotify"),
            "image_url": item.get("images", [{}])[0].get("url") if item.get("images") else None,
            "popularity": item.get("popularity"),
            "followers": item.get("followers", {}).get("total", 0),
        }
        extracted_items.append(extracted)

    return extracted_items
def get_spotify_items_embeddings(data):
    items_info = extract_spotify_items(data)
    return [
        [
            item.get("name"), item.get("spotify_url"), item.get("image_url"), item.get("popularity"),
            item.get("followers"), ", ".join(item.get("genres"))
        ]
        for item in items_info
    ]


def extract_targeted_spotify_user_info(data):
    return {
        "display_name": data.get("display_name", "Unknown"),
        "spotify_url": data.get("external_urls", {}).get("spotify"),
        "followers": data.get("followers", {}).get("total", 0),
        "profile_image": data.get("images", [{}])[0].get("url") if data.get("images") else None,
        "id": data.get("id"),
        "uri": data.get("uri"),
        "href": data.get("href"),
        "type": data.get("type")
    }
def get_targeted_spotify_user_embeddings(data):
    user_info = extract_targeted_spotify_user_info(data)
    return [user_info.get("display_name"), user_info.get("spotify_url"),
            user_info.get("followers"), user_info.get("profile_image"), user_info.get("id"),
            user_info.get("uri"), user_info.get("href"), user_info.get("type")]


def extract_spotify_artists_info(data):
    artists = data.get("artists", {}).get("items", [])
    extracted = []

    for artist in artists:
        extracted.append({
            "name": artist.get("name"),
            "genres": artist.get("genres", []),
            "popularity": artist.get("popularity", 0),
            "followers": artist.get("followers", {}).get("total", 0),
            "spotify_url": artist.get("external_urls", {}).get("spotify"),
            "image": artist.get("images", [{}])[0].get("url") if artist.get("images") else None,
            "id": artist.get("id"),
            "uri": artist.get("uri"),
            "type": artist.get("type"),
            "href": artist.get("href")
        })

    return extracted
def get_spotify_artists_embeddings(data):
    artists_info = extract_spotify_artists_info(data)
    return [
        [
            artist.get("name"), artist.get("spotify_url"), artist.get("image"), artist.get("popularity"),
            artist.get("followers"), ", ".join(artist.get("genres")), artist.get("id"), artist.get("uri"),
            artist.get("type"), artist.get("href")
        ]
        for artist in artists_info
    ]


# albums
def extract_album_info(data):
    album_info = {
        "name": data.get("name"),
        "album_type": data.get("album_type"),
        "total_tracks": data.get("total_tracks"),
        "release_date": data.get("release_date"),
        "release_precision": data.get("release_date_precision"),
        "available_markets": data.get("available_markets", []),
        "spotify_url": data.get("external_urls", {}).get("spotify"),
        "image": data.get("images", [{}])[0].get("url") if data.get("images") else None,
        "id": data.get("id"),
        "uri": data.get("uri"),
        "label": data.get("label"),
        "popularity": data.get("popularity", 0),
        "restrictions": data.get("restrictions", {}).get("reason"),
        "copyrights": [c.get("text") for c in data.get("copyrights", [])],
        "external_ids": data.get("external_ids", {}),
        "genres": data.get("genres", []),
        "artists": [
            {
                "name": artist.get("name"),
                "id": artist.get("id"),
                "uri": artist.get("uri"),
                "spotify_url": artist.get("external_urls", {}).get("spotify")
            }
            for artist in data.get("artists", [])
        ],
        "tracks": []
    }

    track_items = data.get("tracks", {}).get("items", [])
    for track in track_items:
        album_info["tracks"].append({
            "name": track.get("name"),
            "duration_ms": track.get("duration_ms"),
            "explicit": track.get("explicit", False),
            "track_number": track.get("track_number"),
            "preview_url": track.get("preview_url"),
            "spotify_url": track.get("external_urls", {}).get("spotify"),
            "artists": [
                {
                    "name": a.get("name"),
                    "id": a.get("id"),
                    "uri": a.get("uri"),
                    "spotify_url": a.get("external_urls", {}).get("spotify")
                }
                for a in track.get("artists", [])
            ]
        })

    return album_info
def get_album_embeddings(data):
    album_info = extract_album_info(data)
    return [
        album_info.get("name"), album_info.get("album_type"), album_info.get("total_tracks"),
        album_info.get("release_date"), album_info.get("release_precision"), ", ".join(album_info.get("available_markets")),
        album_info.get("spotify_url"), album_info.get("image"), album_info.get("id"), album_info.get("uri"),
        album_info.get("label"), album_info.get("popularity"), album_info.get("restrictions"),
        ", ".join(album_info.get("copyrights")), str(album_info.get("external_ids")), ", ".join(album_info.get("genres"))
    ]


def extract_new_releases(data):
    albums_data = data.get("albums", {})
    albums = []

    for album in albums_data.get("items", []):
        album_info = {
            "name": album.get("name"),
            "album_type": album.get("album_type"),
            "total_tracks": album.get("total_tracks"),
            "release_date": album.get("release_date"),
            "release_precision": album.get("release_date_precision"),
            "available_markets": album.get("available_markets", []),
            "spotify_url": album.get("external_urls", {}).get("spotify"),
            "image": album.get("images", [{}])[0].get("url") if album.get("images") else None,
            "id": album.get("id"),
            "uri": album.get("uri"),
            "type": album.get("type"),
            "restrictions": album.get("restrictions", {}).get("reason"),
            "artists": [
                {
                    "name": artist.get("name"),
                    "id": artist.get("id"),
                    "uri": artist.get("uri"),
                    "spotify_url": artist.get("external_urls", {}).get("spotify")
                }
                for artist in album.get("artists", [])
            ]
        }
        albums.append(album_info)

    return {
        "pagination": {
            "href": albums_data.get("href"),
            "limit": albums_data.get("limit"),
            "next": albums_data.get("next"),
            "offset": albums_data.get("offset"),
            "previous": albums_data.get("previous"),
            "total": albums_data.get("total"),
        },
        "albums": albums
    }
def get_new_releases_embeddings(data):
    new_releases_info = extract_new_releases(data)
    return [
        [
            album.get("name"), album.get("album_type"), album.get("total_tracks"), album.get("release_date"),
            album.get("release_precision"), ", ".join(album.get("available_markets")), album.get("spotify_url"),
            album.get("image"), album.get("id"), album.get("uri"), album.get("type"), album.get("restrictions"),
            ", ".join([artist.get("name") for artist in album.get("artists")])
        ]
        for album in new_releases_info.get("albums", [])
    ]


def extract_user_audiobooks_list(data):
    audiobooks = []

    for item in data.get("items", []):
        audiobook_info = {
            "id": item.get("id"),
            "name": item.get("name"),
            "description": item.get("description"),
            "html_description": item.get("html_description"),
            "edition": item.get("edition"),
            "explicit": item.get("explicit"),
            "publisher": item.get("publisher"),
            "media_type": item.get("media_type"),
            "uri": item.get("uri"),
            "type": item.get("type"),
            "total_chapters": item.get("total_chapters"),
            "spotify_url": item.get("external_urls", {}).get("spotify"),
            "available_markets": item.get("available_markets", []),
            "languages": item.get("languages", []),
            "image": item.get("images", [{}])[0].get("url") if item.get("images") else None,
            "authors": [author.get("name") for author in item.get("authors", [])],
            "narrators": [narrator.get("name") for narrator in item.get("narrators", [])],
            "copyrights": [
                {
                    "text": copyright.get("text"),
                    "type": copyright.get("type")
                }
                for copyright in item.get("copyrights", [])
            ]
        }
        audiobooks.append(audiobook_info)

    return {
        "pagination": {
            "href": data.get("href"),
            "limit": data.get("limit"),
            "next": data.get("next"),
            "offset": data.get("offset"),
            "previous": data.get("previous"),
            "total": data.get("total"),
        },
        "audiobooks": audiobooks
    }
def get_user_audiobooks_embeddings(data):
    audiobooks_info = extract_user_audiobooks_list(data)
    return [
        [
            audiobook.get("id"), audiobook.get("name"), audiobook.get("description"),
            audiobook.get("explicit"), audiobook.get("publisher"), audiobook.get("media_type"),
            audiobook.get("uri"), audiobook.get("type"), audiobook.get("total_chapters"),
            audiobook.get("spotify_url"), ", ".join(audiobook.get("languages")), audiobook.get("image"),
            ", ".join(audiobook.get("authors")), ", ".join(audiobook.get("narrators"))
        ]
        for audiobook in audiobooks_info.get("audiobooks", [])
    ]



def extract_saved_episode_details(data):
    episodes = []

    for item in data.get("items", []):
        episode_info = {
            "added_at": item.get("added_at"),
            "episode": {
                "id": item.get("episode", {}).get("id"),
                "name": item.get("episode", {}).get("name"),
                "description": item.get("episode", {}).get("description"),
                "html_description": item.get("episode", {}).get("html_description"),
                "audio_preview_url": item.get("episode", {}).get("audio_preview_url"),
                "duration_ms": item.get("episode", {}).get("duration_ms"),
                "explicit": item.get("episode", {}).get("explicit"),
                "external_url": item.get("episode", {}).get("external_urls", {}).get("spotify"),
                "language": item.get("episode", {}).get("language"),
                "languages": item.get("episode", {}).get("languages", []),
                "release_date": item.get("episode", {}).get("release_date"),
                "release_date_precision": item.get("episode", {}).get("release_date_precision"),
                "image": item.get("episode", {}).get("images", [{}])[0].get("url"),
                "is_playable": item.get("episode", {}).get("is_playable"),
                "is_externally_hosted": item.get("episode", {}).get("is_externally_hosted"),
                "resume_point": item.get("episode", {}).get("resume_point", {}),
                "uri": item.get("episode", {}).get("uri"),
                "show": {
                    "name": item.get("episode", {}).get("show", {}).get("name"),
                    "show_uri": item.get("episode", {}).get("show", {}).get("uri"),
                    "total_episodes": item.get("episode", {}).get("show", {}).get("total_episodes"),
                    "show_description": item.get("episode", {}).get("show", {}).get("description"),
                    "show_image": item.get("episode", {}).get("show", {}).get("images", [{}])[0].get("url")
                }
            }
        }
        episodes.append(episode_info)

    return {
        "pagination": {
            "href": data.get("href"),
            "limit": data.get("limit"),
            "next": data.get("next"),
            "offset": data.get("offset"),
            "previous": data.get("previous"),
            "total": data.get("total")
        },
        "episodes": episodes
    }
def get_saved_episode_embeddings(data):
    episodes_info = extract_saved_episode_details(data)
    return [
        [
            episode.get("added_at"), episode.get("episode", {}).get("id"),
            episode.get("episode", {}).get("name"), episode.get("episode", {}).get("description"),
            episode.get("episode", {}).get("audio_preview_url"), episode.get("episode", {}).get("duration_ms"),
            episode.get("episode", {}).get("explicit"), episode.get("episode", {}).get("external_url"),
            episode.get("episode", {}).get("release_date"), episode.get("episode", {}).get("release_date_precision"),
            episode.get("episode", {}).get("image"), episode.get("episode", {}).get("is_playable"),
            episode.get("episode", {}).get("is_externally_hosted")
        ]
        for episode in episodes_info.get("episodes", [])
    ]


# player
def extract_spotify_playback_status(data):
    device = data.get("device", {})
    item = data.get("item", {})
    album = item.get("album", {})
    artist = item.get("artists", [{}])[0]  # Assuming only one artist for now

    playback_status = {
        "device": {
            "id": device.get("id"),
            "is_active": device.get("is_active"),
            "is_private_session": device.get("is_private_session"),
            "is_restricted": device.get("is_restricted"),
            "name": device.get("name"),
            "type": device.get("type"),
            "volume_percent": device.get("volume_percent"),
            "supports_volume": device.get("supports_volume")
        },
        "repeat_state": data.get("repeat_state"),
        "shuffle_state": data.get("shuffle_state"),
        "context": {
            "type": data.get("context", {}).get("type"),
            "href": data.get("context", {}).get("href"),
            "external_urls": data.get("context", {}).get("external_urls", {}).get("spotify"),
            "uri": data.get("context", {}).get("uri")
        },
        "timestamp": data.get("timestamp"),
        "progress_ms": data.get("progress_ms"),
        "is_playing": data.get("is_playing"),
        "currently_playing_type": data.get("currently_playing_type"),
        "item": {
            "name": item.get("name"),
            "uri": item.get("uri"),
            "explicit": item.get("explicit"),
            "popularity": item.get("popularity"),
            "duration_ms": item.get("duration_ms"),
            "track_number": item.get("track_number"),
            "disc_number": item.get("disc_number"),
            "preview_url": item.get("preview_url"),
            "is_local": item.get("is_local"),
            "external_urls": item.get("external_urls", {}).get("spotify"),
            "id": item.get("id"),
            "type": item.get("type"),
            "restrictions": item.get("restrictions", {}).get("reason"),
            "external_ids": item.get("external_ids", {}),
            "images": album.get("images", [{}])[0].get("url"),
            "album": {
                "name": album.get("name"),
                "uri": album.get("uri"),
                "release_date": album.get("release_date"),
                "release_date_precision": album.get("release_date_precision"),
                "total_tracks": album.get("total_tracks"),
                "available_markets": album.get("available_markets"),
                "external_urls": album.get("external_urls", {}).get("spotify")
            },
            "artists": [{
                "name": artist.get("name"),
                "uri": artist.get("uri"),
                "external_urls": artist.get("external_urls", {}).get("spotify")
            }]
        },
        "actions": data.get("actions", {})
    }

    return playback_status
def get_spotify_playback_status_embeddings(data):
    playback_status_info = extract_spotify_playback_status(data)
    return [
        playback_status_info.get("device", {}).get("id"), playback_status_info.get("device", {}).get("name"),
        playback_status_info.get("device", {}).get("type"), playback_status_info.get("device", {}).get("volume_percent"),
        playback_status_info.get("repeat_state"), playback_status_info.get("shuffle_state"),
        playback_status_info.get("context", {}).get("type"), playback_status_info.get("context", {}).get("href"),
        playback_status_info.get("context", {}).get("external_urls"), playback_status_info.get("timestamp"),
        playback_status_info.get("progress_ms"), playback_status_info.get("is_playing"),
        playback_status_info.get("currently_playing_type"), playback_status_info.get("item", {}).get("name"),
        playback_status_info.get("item", {}).get("spotify_url"), playback_status_info.get("item", {}).get("id")
    ]


def extract_device_info(devices):
    device_info = []

    for device in devices:
        device_data = {
            "id": device.get("id"),
            "is_active": device.get("is_active"),
            "is_private_session": device.get("is_private_session"),
            "is_restricted": device.get("is_restricted"),
            "name": device.get("name"),
            "type": device.get("type"),
            "volume_percent": device.get("volume_percent"),
            "supports_volume": device.get("supports_volume")
        }
        device_info.append(device_data)

    return device_info
def get_device_info_embeddings(devices):
    device_info = extract_device_info(devices)
    return [
        [
            device.get("id"), device.get("name"), device.get("type"), device.get("volume_percent"),
            device.get("supports_volume"), device.get("is_active"), device.get("is_private_session"),
            device.get("is_restricted")
        ]
        for device in device_info
    ]


def extract_recently_played_spotify_tracks(data):
    processed_data = []

    for item in data.get("items", []):
        track = item.get("track", {})
        album = track.get("album", {})
        artists = track.get("artists", [])

        # Extract information from the track and album
        track_data = {
            "track_name": track.get("name"),
            "track_id": track.get("id"),
            "album_name": album.get("name"),
            "album_id": album.get("id"),
            "album_type": album.get("album_type"),
            "release_date": album.get("release_date"),
            "album_image_url": album.get("images", [{}])[0].get("url", ""),
            "artists": [{"name": artist.get("name"), "id": artist.get("id")} for artist in artists],
            "is_playable": track.get("is_playable"),
            "duration_ms": track.get("duration_ms"),
            "explicit": track.get("explicit"),
            "external_urls": track.get("external_urls", {}).get("spotify")
        }

        processed_data.append(track_data)

    return processed_data
def get_recently_played_spotify_tracks_embeddings(data):
    recently_played_info = extract_recently_played_spotify_tracks(data)
    return [
        [
            track.get("track_name"), track.get("track_id"), track.get("album_name"), track.get("album_id"),
            track.get("album_type"), track.get("release_date"), track.get("album_image_url"),
            ", ".join(track.get("artists"))
        ]
        for track in recently_played_info
    ]


def extract_currently_playing_and_queue(data):
    # Extract currently playing track info
    currently_playing = data.get("currently_playing", {})
    track_info = currently_playing.get("album", {})

    # Extract useful track details
    track_data = {
        "currently_playing": {
            "track_name": currently_playing.get("name"),
            "track_id": currently_playing.get("id"),
            "album_name": track_info.get("name"),
            "album_id": track_info.get("id"),
            "album_type": track_info.get("album_type"),
            "release_date": track_info.get("release_date"),
            "album_image_url": track_info.get("images", [{}])[0].get("url", ""),
            "artists": [{"name": artist.get("name"), "id": artist.get("id")} for artist in
                        currently_playing.get("artists", [])],
            "is_playable": currently_playing.get("is_playable"),
            "duration_ms": currently_playing.get("duration_ms"),
            "explicit": currently_playing.get("explicit"),
            "external_urls": currently_playing.get("external_urls", {}).get("spotify"),
        }
    }

    # Process the queue
    queue_data = []
    for item in data.get("queue", []):
        album_info = item.get("album", {})
        queue_track_data = {
            "track_name": item.get("name"),
            "track_id": item.get("id"),
            "album_name": album_info.get("name"),
            "album_id": album_info.get("id"),
            "album_type": album_info.get("album_type"),
            "release_date": album_info.get("release_date"),
            "album_image_url": album_info.get("images", [{}])[0].get("url", ""),
            "artists": [{"name": artist.get("name"), "id": artist.get("id")} for artist in item.get("artists", [])],
            "is_playable": item.get("is_playable"),
            "duration_ms": item.get("duration_ms"),
            "explicit": item.get("explicit"),
            "external_urls": item.get("external_urls", {}).get("spotify"),
        }
        queue_data.append(queue_track_data)

    track_data["queue"] = queue_data
    return track_data
def get_currently_playing_and_queue_embeddings(data):
    track_data = extract_currently_playing_and_queue(data)

    # Format for currently playing track
    currently_playing = track_data.get("currently_playing", {})
    currently_playing_info = [
        currently_playing.get("track_name"), currently_playing.get("track_id"),
        currently_playing.get("album_name"), currently_playing.get("album_id"),
        currently_playing.get("album_type"), currently_playing.get("release_date"),
        currently_playing.get("album_image_url"),
        ", ".join([artist.get("name") for artist in currently_playing.get("artists", [])]),
        currently_playing.get("is_playable"), currently_playing.get("duration_ms"),
        currently_playing.get("explicit"), currently_playing.get("external_urls")
    ]

    # Format for queue
    queue_data = [
        [
            item.get("track_name"), item.get("track_id"), item.get("album_name"), item.get("album_id"),
            item.get("album_type"), item.get("release_date"), item.get("album_image_url"),
            ", ".join([artist.get("name") for artist in item.get("artists", [])]),
            item.get("is_playable"), item.get("duration_ms"), item.get("explicit"),
            item.get("external_urls")
        ]
        for item in track_data.get("queue", [])
    ]

    return [currently_playing_info, queue_data]


# playlist

def extract_user_playlists_data(json_data):

    # Initialize a list to store extracted show information
    shows = []

    # Loop through the 'items' in the JSON data
    for show in json_data.get('items', []):
        show_data = {
            'name': show.get('name'),
            'id': show.get('id'),
            'description': show.get('description'),
            'external_url': show.get('external_urls', {}).get('spotify'),
            'image_url': show.get('images', [{}])[0].get('url'),
            'owner_name': show.get('owner', {}).get('display_name'),
            'owner_url': show.get('owner', {}).get('external_urls', {}).get('spotify'),
            'tracks_total': show.get('tracks', {}).get('total', 0),
            'public': show.get('public'),
            'uri': show.get('uri'),
        }

        # Add the show data to the list
        shows.append(show_data)

    # Return the extracted list of shows
    return shows
def get_user_playlists_embeddings(json_data):
    playlists_data = extract_user_playlists_data(json_data)
    return [
        [
            playlist.get("name"), playlist.get("id"), playlist.get("description"),
            playlist.get("external_url"), playlist.get("image_url"), playlist.get("owner_name"),
            playlist.get("owner_url"), playlist.get("tracks_total"), playlist.get("public"), playlist.get("uri")
        ]
        for playlist in playlists_data
    ]


def extract_featured_playlists_data(playlists_json):
    # Extract the 'message' and 'playlists' part
    message = playlists_json.get('message', 'No message available')
    playlists = []

    # Extract playlist details from the 'items' list
    for playlist in playlists_json.get('playlists', {}).get('items', []):
        playlist_data = {
            'name': playlist.get('name', 'N/A'),
            'description': playlist.get('description', 'No description available'),
            'external_url': playlist.get('external_urls', {}).get('spotify', 'N/A'),
            'id': playlist.get('id', 'N/A'),
            'image_url': playlist.get('images', [{}])[0].get('url', 'No image available'),
            'image_height': playlist.get('images', [{}])[0].get('height', 'N/A'),
            'image_width': playlist.get('images', [{}])[0].get('width', 'N/A'),
            'owner_name': playlist.get('owner', {}).get('display_name', 'Unknown'),
            'owner_external_url': playlist.get('owner', {}).get('external_urls', {}).get('spotify', 'N/A'),
            'is_public': playlist.get('public', False),
            'tracks_total': playlist.get('tracks', {}).get('total', 0),
            'uri': playlist.get('uri', 'N/A')
        }
        playlists.append(playlist_data)

    return message, playlists
def get_featured_playlists_embeddings(playlists_json):
    message, playlists_data = extract_featured_playlists_data(playlists_json)
    return [
        [
            playlist.get("name"), playlist.get("description"), playlist.get("external_url"), playlist.get("id"),
            playlist.get("image_url"), playlist.get("image_height"), playlist.get("image_width"),
            playlist.get("owner_name"), playlist.get("owner_external_url"), playlist.get("is_public"),
            playlist.get("tracks_total"), playlist.get("uri")
        ]
        for playlist in playlists_data
    ]


def extract_saved_shows_data(shows_json):
    # Extract the 'href', 'limit', 'next', 'previous', and 'total' information
    href = shows_json.get('href', 'N/A')
    limit = shows_json.get('limit', 0)
    next_url = shows_json.get('next', 'N/A')
    previous_url = shows_json.get('previous', 'N/A')
    total = shows_json.get('total', 0)

    shows = []

    # Extract details for each show from the 'items' list
    for item in shows_json.get('items', []):
        show_data = {
            'added_at': item.get('added_at', 'N/A'),
            'show_id': item.get('show', {}).get('id', 'N/A'),
            'show_name': item.get('show', {}).get('name', 'N/A'),
            'show_description': item.get('show', {}).get('description', 'No description available'),
            'show_html_description': item.get('show', {}).get('html_description', 'No HTML description available'),
            'show_external_url': item.get('show', {}).get('external_urls', {}).get('spotify', 'N/A'),
            'show_image_url': item.get('show', {}).get('images', [{}])[0].get('url', 'No image available'),
            'show_image_height': item.get('show', {}).get('images', [{}])[0].get('height', 'N/A'),
            'show_image_width': item.get('show', {}).get('images', [{}])[0].get('width', 'N/A'),
            'show_total_episodes': item.get('show', {}).get('total_episodes', 0),
            'show_is_externally_hosted': item.get('show', {}).get('is_externally_hosted', False),
            'show_available_markets': item.get('show', {}).get('available_markets', []),
            'show_languages': item.get('show', {}).get('languages', []),
            'show_media_type': item.get('show', {}).get('media_type', 'N/A'),
            'show_publisher': item.get('show', {}).get('publisher', 'N/A'),
            'show_type': item.get('show', {}).get('type', 'N/A'),
            'show_uri': item.get('show', {}).get('uri', 'N/A')
        }
        shows.append(show_data)

    return href, limit, next_url, previous_url, total, shows
def get_saved_shows_embeddings(shows_json):
    href, limit, next_url, previous_url, total, shows_data = extract_saved_shows_data(shows_json)
    return [
        [
            show.get("added_at"), show.get("show_id"), show.get("show_name"), show.get("show_description"),
            show.get("show_html_description"), show.get("show_external_url"), show.get("show_image_url"),
            show.get("show_image_height"), show.get("show_image_width"), show.get("show_total_episodes"),
            show.get("show_is_externally_hosted"), ", ".join(show.get("show_available_markets", [])),
            ", ".join(show.get("show_languages", [])), show.get("show_media_type"), show.get("show_publisher"),
            show.get("show_type"), show.get("show_uri")
        ]
        for show in shows_data
    ]

