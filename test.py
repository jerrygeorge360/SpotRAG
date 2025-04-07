# users
def extract_spotify_user_info(user_data):
    if not user_data:
        return []

    return [{
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
    }]

def extract_spotify_items(data):
    return [{
        "name": item.get("name", "Unknown"),
        "genres": item.get("genres", []),
        "spotify_url": item.get("external_urls", {}).get("spotify"),
        "image_url": item.get("images", [{}])[0].get("url") if item.get("images") else None,
        "popularity": item.get("popularity"),
        "followers": item.get("followers", {}).get("total", 0),
    } for item in data.get("items", [])]

def extract_targeted_spotify_user_info(data):
    return [{
        "display_name": data.get("display_name", "Unknown"),
        "spotify_url": data.get("external_urls", {}).get("spotify"),
        "followers": data.get("followers", {}).get("total", 0),
        "profile_image": data.get("images", [{}])[0].get("url") if data.get("images") else None,
        "id": data.get("id"),
        "uri": data.get("uri"),
        "href": data.get("href"),
        "type": data.get("type")
    }]

def extract_spotify_artists_info(data):
    return [{
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
    } for artist in data.get("artists", {}).get("items", [])]

# albums
def extract_album_info(data):
    album_info = [{
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
        "tracks": [{
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
        } for track in data.get("tracks", {}).get("items", [])]
    }]
    return album_info

def extract_new_releases(data):
    return [{
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
    } for album in data.get("albums", {}).get("items", [])]

# More functions would follow the same pattern.
