# radioNowPlaying

This is a small, very work-in-progress app to save off what's playing on radio stations to
Elasticsearch.

Earlier in its life (see the first commit), it started as a more ambitious project to save to a
SQL database and build out a web UI; this turned out to be overkill, as Kibana is much more than
capable of doing the same, with less work. Thus the project migrated to bash and Elasticsearch.

Two Web sources are currently supported, depending on what your local radio stations support:
[TuneGenie](https://tunegenie.com/) and [Triton Digital](https://www.tritondigital.com/).

# Requirements

The tools [jq](https://stedolan.github.io/jq/) and
[XMLStarlet](https://pypi.org/project/xmlstarlet/) are required for parsing.
[curl](https://curl.se/) is required for writing to Elasticsearch. These are available in just
about all environments via package managers.

# Using

Daemonize the included shell scripts using your favorite method - systemd, Docker containers, or
otherwise. An example systemd unit file is provided as a convenience.

These environment variables must be set:
* `ES_URL` to the Elasticsearch index address, e.g. `http://localhost:9200/radio`
* `STATION_NAME` to the station name, e.g. `WERS`
* `STATION_PROVIDER` to the provider name, either `tunegenie` or `tritondigital`.

# Notes on Operation

In general, finding the right script to use, and the right parameters, is a matter of loading your
favorite radio station with your browser's dev tools open.

## TuneGenie

TuneGenie's API endpoints speak JSON. The API itself appears to be consistent across stations;
only the DNS name changes.

Confusingly, the API requires authentication to use:

```
$ curl http://wers.tunegenie.com/api/v1/brand/nowplaying/
{"meta": {"status": 401, "error": "Authentication Required"}}
```

Giving it an expected authentication header is sufficient to "authenticate":

```
pi@raspberrypi:/usr/local/bin $ curl -s -H "Referer: http://wers.tunegenie.com/onair/" http://wers.tunegenie.com/api/v1/brand/nowplaying/ | jq .
{
  "meta": {
    "status": 200,
    "base_url": "http://wers.tunegenie.com"
  },
  "response": [
    {
      "artistlink": "/music/red-hot-chili-peppers/",
      "sid": 450747628,
      "played_at_display": "6:14 PM",
      "sslg": "look-around",
      "songlink": "/music/red-hot-chili-peppers/_/look-around/",
      "concertslink": "/music/red-hot-chili-peppers/_concerts/",
      "played_at": "2022-01-08T18:14:29-05:00",
      "albumslink": "/music/red-hot-chili-peppers/_albums/",
      "artist": "Red Hot Chili Peppers",
      "song": "Look Around",
      "videolink": "/music/red-hot-chili-peppers/_/look-around/_video/",
      "aslg": "red-hot-chili-peppers",
      "lyriclink": "/music/red-hot-chili-peppers/_/look-around/_lyric/",
      "campaignlink": "/contest/red-hot-chili-peppers/",
      "topttrackslink": "/music/red-hot-chili-peppers/_toptracks/"
    }
  ]
}
```

## Triton Digital

Triton Digital's API speaks XML:

```
$ curl -s 'https://np.tritondigital.com/public/nowplaying?mountName=WBOSFMAAC&numberToFetch=1' | xmlstarlet fo
<?xml version="1.0" encoding="UTF-8"?>
<nowplaying-info-list>
  <nowplaying-info mountName="WBOSFMAAC" timestamp="1641683906" type="track">
    <property name="cue_time_start"><![CDATA[1641683906920]]></property>
    <property name="cue_title"><![CDATA[What Ive Done]]></property>
    <property name="track_artist_name"><![CDATA[Linkin Park]]></property>
  </nowplaying-info>
</nowplaying-info-list>

```

The default `numberToFetch` appears to be the last six entries; we specify `numberToFetch` to
limit to the one we care about. There is additionally an `eventType=track` provider specified on
all URLs I've found, but I haven't found its purpose. There also appears to be cache-busting
parameter, `request.preventCache=(UNIX timestamp)`, that likewise seems to have no purpose.
