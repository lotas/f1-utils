f1-utils
========


retrieve_stats.py
-
Retrieves F1 GP results for any event

Usage:

#### Get specific session
```sh
$python retrieve_stats.py 2013 Spain qualifying
```

Will return JSON-encoded results for the 2013 Spain Quailfying session:

```javascript
{"2013": {"Spain": {"qualifying": [{"Q1": "1:21.913", "Q3": " 1:20.718", "Q2": " 1:21.776", "No": "9", "Laps": "12", "Driver": "Nico Rosberg", "Pos" : "1", "Team": "Mercedes"}, {"Q1": "1:21.728", "Q3": " 1:20.972", "Q2": " 1:21.001", "No": "10", "Laps": "12", "Driver": "Lewis Hamilton", "Pos": "2 ", "Team": "Mercedes"}, {"Q1": "1:22.158", "Q3": " 1:21.054", "Q2": " 1:21.602", "No": "1", "Laps": "12", "Driver": "Sebastian Vettel", "Pos": "3",  "Team": "Red Bull Racing-Renault"}, {"Q1": "1:22.210", "Q3": " 1:21.177", "Q2": " 1:21.676", "No": "7", "Laps": "17", "Driver": "Kimi R\u00e4ikk\u00 f6nen", "Pos": "4", "Team": "Lotus-Renault"}, ...
```

#### Get all sessions
```sh
$python retrieve_stats.py 2013 Monaco all
```
will return
```javascript
{"2013": {"Monaco": {"practice 1": [{"No": "9", "Laps": "31", "Driver": "Nico Rosberg", "Pos": "1", "Gap": "[]", "Team": "Mercedes", "Time/Retired": "1:16.195"}, ...
"practice 2": [..],
"practice 3": [..],
"qualifying": [..],
"race": [..]
```


