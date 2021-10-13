#!/usr/bin/env python3

import json
import logging
import os
import requests
import sqlite3
import time
from dateutil import parser

def init_stations() -> list[dict]:
    config = []
    for row in db.execute("SELECT callsign, service from stations where enabled=1;"):
        config.append({'callsign': row[0], 'service': row[1]})
    return config

def init_db(db_filename: str):
    db = sqlite3.connect(db_filename, isolation_level=None).cursor()
    db.execute("""
        CREATE TABLE IF NOT EXISTS stations (
          callsign text not null,
          service text not null,
          enabled integer not null default 1
        );
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS songs (
          callsign text not null,
          time integer not null,
          artist text not null,
          song text not null,
          foreign key (callsign) references stations(callsign),
          constraint unique_by_time unique(callsign, time)
        );
    """)
    return db

def last_playing(db, callsign: str) -> dict[str, str]:
    # a unique constraint prevents there from ever being more than one
    for row in db.execute("SELECT artist, song from songs where callsign = ? and time = " \
        "(select max(time) from songs where callsign = ?);", (callsign, callsign)):
        return {'artist': row[0], 'song': row[1]}
    return {'artist': None, 'song': None} # there can be zero if this is the first poll

def poll_stations(stations):
    now_playing = []
    for station in stations:
        playing = None

        if station['service'] == 'tunegenie':
            playing = poll_tunegenie(station['callsign'])
        else:
            logging.warn("Unsupported service % on %s", station['service'], station['callsign'])

        if playing:
            logging.info("%s - %s @ %s", playing['artist'], playing['song'], station['callsign'])
            now_playing.append({
                'callsign': station['callsign'],
                **playing
            })

    return now_playing

def poll_tunegenie(callsign: str) -> dict:
    r = requests.get(f"http://{callsign}.tunegenie.com/api/v1/brand/nowplaying/",
        headers={'Referer': f"http://{callsign}.tunegenie.com/onair/"})

    body = json.loads(r.text)['response'][0]

    return {
        'artist': body['artist'],
        'song': body['song'],
        'time': parser.parse(body['played_at_display']),
    }

def update_db(db, records: list[dict]):
    for record in records:
        last = last_playing(db, record['callsign'])

        if last['artist'] != record['artist'] and last['song'] != record['song']:
            logging.debug('New song for %s', record['callsign'])
            db.execute("INSERT INTO songs VALUES (?, ?, ?, ?);", (record['callsign'],
                record['time'], record['artist'], record['song']))

db = init_db(os.environ.get('DATABASE_FILENAME', 'database.db'))
stations = init_stations()
logging.basicConfig(
  format='[%(levelname)s] (%(asctime)s) %(message)s',
  level=os.environ.get('LOG_LEVEL', 'INFO')
)
while True:
    logging.debug('The time for polling has come')
    songs = poll_stations(stations)
    update_db(db, songs)
    logging.debug('Polling has finished')
    time.sleep(int(os.environ.get('POLL_INTERVAL', 60)))
