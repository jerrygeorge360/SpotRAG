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
def get_spotify_user_embeddings(user_info: dict) -> list[str]:
    if not user_info:
        return []

    info_str = " - ".join([
        f'ID:{user_info.get("id", "")}',
        f'Display name:{user_info.get("display_name", "")}',
        f'Email: {user_info.get("email", "")}',
        f'Country: {user_info.get("country", "")}',
        f'Product: {user_info.get("product", "")}',
        f'Followers Count: {str(user_info.get("followers", ""))}',
        f'Profile url: {user_info.get("profile_url", "")}',
    ])
    return [info_str]

# def get_spotify_user_embeddings(user_data):
#     user_info = user_data
#     return [user_info.get("id"), user_info.get("display_name"), user_info.get("email"),
#             user_info.get("country"), user_info.get("profile_url"), user_info.get("product"),
#             user_info.get("followers"), user_info.get("profile_image"),
#             user_info.get("explicit_content_filter_enabled"), user_info.get("explicit_content_filter_locked")]


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
# def get_spotify_items_embeddings(data):
#     items_info = data
#     return [
#         [
#             item.get("name"), item.get("spotify_url"), item.get("image_url"), item.get("popularity"),
#             item.get("followers"), ", ".join(item.get("genres"))
#         ]
#         for item in items_info
#     ]
def get_spotify_items_embeddings(items_info: list[dict]) -> list[str]:
    formatted = []
    for item in items_info:
        parts = [
            f"Item Name: {item.get('name', '')}",
            f"Genres: {', '.join(item.get('genres', []))}",
            f"Spotify URL: {item.get('spotify_url', '')}",
            f"Popularity: {str(item.get('popularity', ''))}",
            f"Followers: {str(item.get('followers', ''))}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted



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
# def get_targeted_spotify_user_embeddings(data):
#     user_info = data
#     return [user_info.get("display_name"), user_info.get("spotify_url"),
#             user_info.get("followers"), user_info.get("profile_image"), user_info.get("id"),
#             user_info.get("uri"), user_info.get("href"), user_info.get("type")]
def get_targeted_spotify_user_embeddings(user_info: dict) -> list[str]:
    parts = [
        f"Display Name: {user_info.get('display_name', '')}",
        f"Spotify URL: {user_info.get('spotify_url', '')}",
        f"Followers: {str(user_info.get('followers', ''))}",
        f"Profile Image: {user_info.get('profile_image', '')}",
        f"User ID: {user_info.get('id', '')}",
        f"User URI: {user_info.get('uri', '')}",
        f"User Type: {user_info.get('type', '')}",
        f"Link: {user_info.get('href', '')}",
    ]
    return [" - ".join(part for part in parts if part)]

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
# def get_spotify_artists_embeddings(data):
#     artists_info = data
#     return [
#         [
#             artist.get("name"), artist.get("spotify_url"), artist.get("image"), artist.get("popularity"),
#             artist.get("followers"), ", ".join(artist.get("genres")), artist.get("id"), artist.get("uri"),
#             artist.get("type"), artist.get("href")
#         ]
#         for artist in artists_info
#     ]
def get_spotify_artists_embeddings(artists_info: list[dict]) -> list[str]:
    formatted = []
    for artist in artists_info:
        parts = [
            f"Artist Name: {artist.get('name', '')}",
            f"Genres: {', '.join(artist.get('genres', []))}",
            f"Spotify URL: {artist.get('spotify_url', '')}",
            f"Popularity: {str(artist.get('popularity', ''))}",
            f"Followers: {str(artist.get('followers', ''))}",
            f"Artist ID: {artist.get('id', '')}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted


# albums
def extract_album_info(data):
    flattened = []
    for item in data.get("items", []):
        album = item.get("album", {})
        for track in album.get("tracks", {}).get("items", []):
            flattened.append({
                "added_at": item.get("added_at"),
                "album_name": album.get("name"),
                "album_id": album.get("id"),
                "album_url": album.get("external_urls", {}).get("spotify"),
                "album_release_date": album.get("release_date"),
                "album_image": album.get("images", [{}])[0].get("url"),
                "track_name": track.get("name"),
                "track_id": track.get("id"),
                "track_url": track.get("external_urls", {}).get("spotify"),
                "track_duration_ms": track.get("duration_ms"),
                "track_number": track.get("track_number"),
                "artist_name": track.get("artists", [{}])[0].get("name"),
                "artist_id": track.get("artists", [{}])[0].get("id"),
                "artist_url": track.get("artists", [{}])[0].get("external_urls", {}).get("spotify"),
            })
    return flattened
def get_album_embeddings(docs: list[dict]) -> list[str]:
    formatted = []
    for doc in docs:
        parts = [
            f"Track: {doc.get('track_name', '')}",
            f"Artist: {doc.get('artist_name', '')}",
            f"Album: {doc.get('album_name', '')}",
            f"Release Date: {doc.get('album_release_date', '')}",
            f"Track URL: {doc.get('track_url', '')}",
            f"Album URL: {doc.get('album_url', '')}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted



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

def get_new_releases_embeddings(data: dict) -> list[str]:
    formatted = []
    for album in data.get("albums", []):
        parts = [
            f"Album: {album.get('name', '')}",
            f"Artists: {', '.join(artist.get('name', '') for artist in album.get('artists', []))}",
            f"Release Date: {album.get('release_date', '')}",
            f"Album Type: {album.get('album_type', '')}",
            f"Spotify URL: {album.get('spotify_url', '')}"
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted

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
# def get_user_audiobooks_embeddings(data):
#     audiobooks_info = data
#     return [
#         [
#             audiobook.get("id"), audiobook.get("name"), audiobook.get("description"),
#             audiobook.get("explicit"), audiobook.get("publisher"), audiobook.get("media_type"),
#             audiobook.get("uri"), audiobook.get("type"), audiobook.get("total_chapters"),
#             audiobook.get("spotify_url"), ", ".join(audiobook.get("languages")), audiobook.get("image"),
#             ", ".join(audiobook.get("authors")), ", ".join(audiobook.get("narrators"))
#         ]
#         for audiobook in audiobooks_info.get("audiobooks", [])
#     ]
def get_user_audiobooks_embeddings(data) -> list[str]:
    formatted = []
    for audiobook in data.get("audiobooks", []):
        parts = [
            f"Title: {audiobook.get('name', '')}",
            f"Publisher: {audiobook.get('publisher', '')}",
            f"Description: {audiobook.get('description', '')}",
            f"Explicit: {'Yes' if audiobook.get('explicit') else 'No'}",
            f"Media Type: {audiobook.get('media_type', '')}",
            f"Total Chapters: {audiobook.get('total_chapters', '')}",
            f"Languages: {', '.join(audiobook.get('languages', []))}",
            f"Authors: {', '.join(audiobook.get('authors', []))}",
            f"Narrators: {', '.join(audiobook.get('narrators', []))}",
            f"URL: {audiobook.get('spotify_url', '')}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted


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

# def get_saved_episode_embeddings(data):
#     episodes_info = data
#     return [
#         [
#             episode.get("added_at"), episode.get("episode", {}).get("id"),
#             episode.get("episode", {}).get("name"), episode.get("episode", {}).get("description"),
#             episode.get("episode", {}).get("audio_preview_url"), episode.get("episode", {}).get("duration_ms"),
#             episode.get("episode", {}).get("explicit"), episode.get("episode", {}).get("external_url"),
#             episode.get("episode", {}).get("release_date"), episode.get("episode", {}).get("release_date_precision"),
#             episode.get("episode", {}).get("image"), episode.get("episode", {}).get("is_playable"),
#             episode.get("episode", {}).get("is_externally_hosted")
#         ]
#         for episode in episodes_info.get("episodes", [])
#     ]

# player
def get_saved_episode_embeddings(data) -> list[str]:
    formatted = []
    for episode in data.get("episodes", []):
        ep_info = episode.get("episode", {})
        show_info = ep_info.get("show", {})
        parts = [
            f"Episode: {ep_info.get('name', '')}",
            f"Description: {ep_info.get('description', '')}",
            f"Release Date: {ep_info.get('release_date', '')}",
            f"URL: {ep_info.get('external_url', '')}",
            f"Show: {show_info.get('name', '')}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted

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
# def get_spotify_playback_status_embeddings(data):
#     playback_status_info = data
#
#     return [
#         str(playback_status_info.get("device", {}).get("id", "")),
#         str(playback_status_info.get("device", {}).get("name", "")),
#         str(playback_status_info.get("device", {}).get("type", "")),
#         str(playback_status_info.get("device", {}).get("volume_percent", "")),
#         str(playback_status_info.get("repeat_state", "")),
#         str(playback_status_info.get("shuffle_state", "")),
#         str(playback_status_info.get("context", {}).get("type", "")),
#         str(playback_status_info.get("context", {}).get("href", "")),
#         str(playback_status_info.get("context", {}).get("external_urls", "")),
#         str(playback_status_info.get("timestamp", "")),
#         str(playback_status_info.get("progress_ms", "")),
#         str(playback_status_info.get("is_playing", "")),
#         str(playback_status_info.get("currently_playing_type", "")),
#         str(playback_status_info.get("item", {}).get("name", "")),
#         str(playback_status_info.get("item", {}).get("external_urls", "")),  # fix key name
#         str(playback_status_info.get("item", {}).get("id", ""))
#     ]
def get_spotify_playback_status_embeddings(docs: list[dict]) -> list[str]:
    formatted = []
    for doc in docs:
        parts = [
            f"Status: {'Playing' if doc.get('is_playing') else 'Paused'}",
            f"Track: {doc.get('track_name', '')}",
            f"Artist: {doc.get('artist_name', '')}",
            f"Album: {doc.get('album_name', '')}",
            f"Context: {doc.get('context_type', '')}",  # playlist, album, etc.
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted


def extract_device_info(devices):
    device_info = []
    devices = devices.get('devices')
    if devices:
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
# def get_device_info_embeddings(devices):
#     if not isinstance(devices, list):
#         print("Expected a list of devices but got:", type(devices))
#         return []
#
#
#     return [
#         [
#             f"id:{device.get('id', '')}",
#             f"name:{device.get('name', '')}",
#             f"type:{device.get('type', '')}",
#             f"volume_percent:{device.get('volume_percent', '')}",
#             f"supports_volume:{device.get('supports_volume', '')}",
#             f"is_active:{device.get('is_active', '')}",
#             f"is_private_session:{device.get('is_private_session', '')}",
#             f"is_restricted:{device.get('is_restricted', '')}"
#         ]
#         for device in devices
#     ]
def get_device_info_embeddings(docs: list[dict]) -> list[str]:
    formatted = []
    for doc in docs:
        parts = [
            f"Device Name: {doc.get('device_name', '')}",
            f"Device Type: {doc.get('device_type', '')}",
            f"Status: {'Active' if doc.get('is_active') else 'Inactive'}",
            f"Volume: {doc.get('volume_percent', '')}%",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted


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
# def get_recently_played_spotify_tracks_embeddings(data):
#     recently_played_info = data
#     return [
#         [
#             track.get("track_name"), track.get("track_id"), track.get("album_name"), track.get("album_id"),
#             track.get("album_type"), track.get("release_date"), track.get("album_image_url"),
#             ", ".join([a.get("name", "") for a in track.get("artists", [])])
#         ]
#         for track in recently_played_info
#     ]
def get_recently_played_spotify_tracks_embeddings(docs: list[dict]) -> list[str]:
    formatted = []
    for doc in docs:
        parts = [
            f"Track Name: {doc.get('track_name', '')}",
            f"Artist: {doc.get('artist_name', '')}",
            f"Album: {doc.get('album_name', '')}",
            f"Release Date: {doc.get('release_date', '')}",
            f"Track URL: {doc.get('track_url', '')}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted



def extract_currently_playing_and_queue(data):
    # Extract currently playing track info

    currently_playing = data.get("currently_playing", {})
    if not currently_playing:
        return []
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
    if not data:
        return []

    # Format for currently playing track
    currently_playing = data.get("currently_playing", {})
    currently_playing_info = [
        f"track_name:{currently_playing.get('track_name', '')}",
        f"track_id:{currently_playing.get('track_id', '')}",
        f"album_name:{currently_playing.get('album_name', '')}",
        f"album_id:{currently_playing.get('album_id', '')}",
        f"album_type:{currently_playing.get('album_type', '')}",
        f"release_date:{currently_playing.get('release_date', '')}",
        f"album_image_url:{currently_playing.get('album_image_url', '')}",
        f"artists:{', '.join([artist.get('name', '') for artist in currently_playing.get('artists', [])])}",
        f"is_playable:{currently_playing.get('is_playable', '')}",
        f"duration_ms:{currently_playing.get('duration_ms', '')}",
        f"explicit:{currently_playing.get('explicit', '')}",
        f"external_urls:{currently_playing.get('external_urls', '')}",
    ]

    # Format for queue
    queue_data = []
    for item in data.get("queue", []):
        queue_info = [
            f"track_name:{item.get('track_name', '')}",
            f"track_id:{item.get('track_id', '')}",
            f"album_name:{item.get('album_name', '')}",
            f"album_id:{item.get('album_id', '')}",
            f"album_type:{item.get('album_type', '')}",
            f"release_date:{item.get('release_date', '')}",
            f"album_image_url:{item.get('album_image_url', '')}",
            f"artists:{', '.join([artist.get('name', '') for artist in item.get('artists', [])])}",
            f"is_playable:{item.get('is_playable', '')}",
            f"duration_ms:{item.get('duration_ms', '')}",
            f"explicit:{item.get('explicit', '')}",
            f"external_urls:{item.get('external_urls', '')}",
        ]
        queue_data.append(queue_info)

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
# def get_user_playlists_embeddings(json_data):
#     playlists_data = json_data
#     return [
#         [
#             playlist.get("name"), playlist.get("id"), playlist.get("description"),
#             playlist.get("external_url"), playlist.get("image_url"), playlist.get("owner_name"),
#             playlist.get("owner_url"), playlist.get("tracks_total"), playlist.get("public"), playlist.get("uri")
#         ]
#         for playlist in playlists_data
#     ]
def get_user_playlists_embeddings(docs: list[dict]) -> list[str]:
    formatted = []
    for doc in docs:
        parts = [
            f"Playlist Name: {doc.get('playlist_name', '')}",
            f"Owner: {doc.get('owner', '')}",
            f"Track Count: {doc.get('track_count', '')}",
            f"Description: {doc.get('description', '')}",
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted



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
    message, playlists_data = playlists_json

    embeddings = []
    for playlist in playlists_data:
        embedding = " - ".join([
            f"Name: {playlist.get('name', '')}",
            f"Description: {playlist.get('description', '')}",
            f"URL: {playlist.get('external_url', '')}",
            f"ID: {playlist.get('id', '')}",
            f"Image URL: {playlist.get('image_url', '')}",
            f"Image Height: {playlist.get('image_height', '')}",
            f"Image Width: {playlist.get('image_width', '')}",
            f"Owner Name: {playlist.get('owner_name', '')}",
            f"Owner URL: {playlist.get('owner_external_url', '')}",
            f"Public: {playlist.get('is_public', '')}",
            f"Track Count: {playlist.get('tracks_total', '')}",
            f"URI: {playlist.get('uri', '')}"
        ])
        embeddings.append(embedding)

    return embeddings



def extract_saved_shows_data(shows_json):
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

    return shows
def get_saved_shows_embeddings(docs: list[dict]) -> list[str]:
    formatted = []
    for doc in docs:
        parts = [
            f'Show name:{doc.get("show_name", "")}',
            f'Show publisher: {doc.get("show_publisher", "")}',
            f'Show description: {doc.get("show_description", "")}',
        ]
        formatted.append(" - ".join(part for part in parts if part))
    return formatted
