# radioNowPlaying

This is a small, very work-in-progress app to save off what's playing on radio stations to a
SQL database and search/visualize them over time.

It is currently very rough and requires manually inserting records into a SQLite database to
configure it. For example, to start polling WERS on TuneGenie:

```
[don@zeus ~/workspace/radioNowPlaying:HEAD] sqlite3 database.db
SQLite version 3.34.1 2021-01-20 14:10:07
Enter ".help" for usage hints.
sqlite> insert into stations values('wers', 'tunegenie', 1);
```

## To-Do
* Support iHeartRadio as a source
* Support StreamTheWorld as a source
* Build a web UI (tabular, with search)
* Build a better web UI (timeline)
