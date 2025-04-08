a = {'currently_playing': None, 'queue': []}
a={
  "currently_playing": {
    "album": {
      "album_type": "compilation",
      "total_tracks": 9,
      "available_markets": [
        "CA",
        "BR",
        "IT"
      ],
      "external_urls": {
        "spotify": "string"
      },
      "href": "string",
      "id": "2up3OPMp9Tb4dAKM2erWXQ",
      "images": [
        {
          "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
          "height": 300,
          "width": 300
        }
      ],
      "name": "string",
      "release_date": "1981-12",
      "release_date_precision": "year",
      "restrictions": {
        "reason": "market"
      },
      "type": "album",
      "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
      "artists": [
        {
          "external_urls": {
            "spotify": "string"
          },
          "href": "string",
          "id": "string",
          "name": "string",
          "type": "artist",
          "uri": "string"
        }
      ]
    },
    "artists": [
      {
        "external_urls": {
          "spotify": "string"
        },
        "href": "string",
        "id": "string",
        "name": "string",
        "type": "artist",
        "uri": "string"
      }
    ],
    "available_markets": [
      "string"
    ],
    "disc_number": 0,
    "duration_ms": 0,
    "explicit": False,
    "external_ids": {
      "isrc": "string",
      "ean": "string",
      "upc": "string"
    },
    "external_urls": {
      "spotify": "string"
    },
    "href": "string",
    "id": "string",
    "is_playable": False,
    "linked_from": {},
    "restrictions": {
      "reason": "string"
    },
    "name": "string",
    "popularity": 0,
    "preview_url": "string",
    "track_number": 0,
    "type": "track",
    "uri": "string",
    "is_local": False
  },
  "queue": [
    {
      "album": {
        "album_type": "compilation",
        "total_tracks": 9,
        "available_markets": [
          "CA",
          "BR",
          "IT"
        ],
        "external_urls": {
          "spotify": "string"
        },
        "href": "string",
        "id": "2up3OPMp9Tb4dAKM2erWXQ",
        "images": [
          {
            "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "height": 300,
            "width": 300
          }
        ],
        "name": "string",
        "release_date": "1981-12",
        "release_date_precision": "year",
        "restrictions": {
          "reason": "market"
        },
        "type": "album",
        "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
        "artists": [
          {
            "external_urls": {
              "spotify": "string"
            },
            "href": "string",
            "id": "string",
            "name": "string",
            "type": "artist",
            "uri": "string"
          }
        ]
      },
      "artists": [
        {
          "external_urls": {
            "spotify": "string"
          },
          "href": "string",
          "id": "string",
          "name": "string",
          "type": "artist",
          "uri": "string"
        }
      ],
      "available_markets": [
        "string"
      ],
      "disc_number": 0,
      "duration_ms": 0,
      "explicit": False,
      "external_ids": {
        "isrc": "string",
        "ean": "string",
        "upc": "string"
      },
      "external_urls": {
        "spotify": "string"
      },
      "href": "string",
      "id": "string",
      "is_playable": False,
      "linked_from": {},
      "restrictions": {
        "reason": "string"
      },
      "name": "string",
      "popularity": 0,
      "preview_url": "string",
      "track_number": 0,
      "type": "track",
      "uri": "string",
      "is_local": False
    }
  ]
}

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



c=extract_currently_playing_and_queue(a)
print(c)
print(get_currently_playing_and_queue_embeddings(c))