#!/bin/bash
set -euo pipefail

last_song=""
while true; do
  if [ "$STATION_PROVIDER" == "tunegenie" ]; then
    payload=$(curl -s -H "Referer: http://$STATION_NAME.tunegenie.com/onair/)" http://$STATION_NAME.tunegenie.com/api/v1/brand/nowplaying/)
    this_song=$(echo $payload | jq -r .response[0].song)
    this_artist=$(echo $payload | jq -r .response[0].artist)
  elif [ "$STATION_PROVIDER" == "tritondigital" ]; then
    payload=$(curl -s "http://np.tritondigital.com/public/nowplaying?mountName=${STATION_NAME}FMAAC&numberToFetch=1")
    this_song=$(echo $payload | xmlstarlet sel -T -t -m '//nowplaying-info-list/nowplaying-info/property[@name="cue_title"]/text()' -v . | xmlstarlet unesc)
    this_artist=$(echo $payload | xmlstarlet sel -T -t -m '//nowplaying-info-list/nowplaying-info/property[@name="track_artist_name"]/text()' -v . | xmlstarlet unesc)
  else
    echo "Unsupported station provider."
    exit 1
  fi

  if [ "$this_song" != "$last_song" ]; then
    last_song=$this_song
    curl -s -H "Content-Type: application/json" -X POST $ES_URL/_doc -d \
      "{\"station\": \"$STATION_NAME\", \"time\": $(date +%s)000, \"song\": \"$this_song\", \"artist\": \"$this_artist\"}" \
      > /dev/null 2>&1
  fi
  sleep 60;
done

