__author__ = "Yaraslau Kurmyza"
__license__ = "GPL"
__email__ = "lotask@gmail.com"

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "f1db"

"""

Import practices results into statistics table from http://ergast.com/mrd/
using returned by retrieve_stats.py JSON

Attention!! Will delete all results for given event&session before inserting

Mysql table:

DROP TABLE IF EXISTS `practices`;
CREATE TABLE IF NOT EXISTS `practices` (
  `practiceId` int(11) NOT NULL AUTO_INCREMENT,
  `practiceNumber` tinyint(4) NOT NULL DEFAULT '1',
  `raceId` int(11) NOT NULL DEFAULT '0',
  `driverId` int(11) NOT NULL DEFAULT '0',
  `constructorId` int(11) NOT NULL DEFAULT '0',
  `number` int(11) NOT NULL DEFAULT '0',
  `position` int(11) DEFAULT NULL,
  `time` varchar(255) DEFAULT NULL,
  `gap` varchar(255) DEFAULT NULL,
  `milliseconds` int(11) DEFAULT NULL,
  `laps` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`practiceId`),
  UNIQUE KEY `practiceNumber` (`practiceNumber`,`raceId`,`driverId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


"""

import sys
import json
import MySQLdb
import urllib2
import time
import re
from pprint import pprint

###########################

def _getRaceId(year, raceName, db):
    """
    Find raceId in races table
    Will successfully try to shorten race name to overcome GP titles like "Spanish GP - Spain", "Great Britain" -> British etc..
    """
    if raceName == 'Great Britain': raceName = 'British'

    cur = db.cursor()
    for i in range(3):
        numrows = cur.execute("SELECT raceId FROM races WHERE year=%s AND name LIKE %s", (year, raceName+'%'))
        if numrows == 1:
            return cur.fetchone()[0]
        # try shorter names
        raceName = raceName[:-1]
    return None

def _getTeamId(name, db):
    """
    Tryint to find contstructor team for a given name
    Some tricks apply, though:
       STR -> Toro Rosso
       Red Bull Racing -> Red Bull
    """
    cur = db.cursor()
    if cur.execute("SELECT constructorId FROM constructors WHERE name LIKE %s ", name):
        return cur.fetchone()[0]

    # try just first part, without Engine supplier
    name = name.split('-')[0]

    if name == 'STR': name = 'Toro Rosso'
    if name == 'Red Bull Racing': name = 'Red Bull'

    if cur.execute("SELECT constructorId FROM constructors WHERE name LIKE %s OR %s LIKE name", (name, name)):
        return cur.fetchone()[0]

    return None

def _getDriverId(name, db):
    """
    Trying to find driver by name or by wiki-url
    If none found, will add new entry (with fetched DOB, Nationality from wiki)
    """
    cur = db.cursor()
    name = re.sub("(\s+)", " ", name) # strip double spaces
    urlName = name.replace(' ', '_')
    if cur.execute("SELECT driverId FROM drivers WHERE CONCAT(forename, ' ', surname) LIKE %s OR url LIKE %s", (name, '%' + urlName))  == 1:
        return cur.fetchone()[0]

    print "No entry found for %s... will create one, okay?" % name

    # try url
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.1')]
    url = 'http://en.wikipedia.org/wiki/'+urlName
    page = opener.open(url).read()
    if page:

        try:
            birthday = re.search('<span\s+class="bday">(\d{4}-\d{2}-\d{2})</span>', page).group(1)
        except Exception, e:
            birthday = '0000-00-00'

        try:
            nationality = re.search("Nationality(</a>)?</th>.+?</span>\s*<a[^>]+>([^<]+)</a></td>", page, flags=re.DOTALL|re.IGNORECASE).groups(1)[1]
        except Exception, e:
            nationality = ''

        forename, surname = name.split(" ", 1)
        driverRef = surname.lower().replace(' ', '')

        print "Inserting new driver (%s,%s,%s,%s,%s, %s)" % (driverRef, forename, surname, birthday, nationality, url)

        try:
            cur.execute("INSERT INTO drivers (driverRef, forename, surname, dob, nationality, url) "
                        "VALUES(%s, %s, %s, %s, %s, %s)", (driverRef, forename, surname, birthday, nationality, url))
        except MySQLdb.Error, e:
            print "Error inserting: ", e

        return cur.lastrowid

    return None

def _timeToMs(times):
    if times == 'No time':
        return 0
    r = map(int, re.split(r"[:.,]", times))
    if len(r) == 3:
        return (r[0]*60 + r[1]) * 1000 + r[2]
    return 0

##########################

try:
    json = json.loads("".join(sys.stdin))
except Exception, e:
    print "Invalid json."
    raise

# connect to db
db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)



for year in json.keys():
    for race in json[year].keys():
        raceId = _getRaceId(year, race, db)
        if raceId is None:
            print "Couldn't find raceId for %s-%s" % (year, race)
            break

        for eventType in json[year][race].keys():
            if not eventType.startswith('pract'):
                print "Skipping %s session" % eventType
                continue

            practiceNumber = eventType[-1]

            eventData = json[year][race][eventType]
            print "Proceeding %s-%s Session: %s (raceId=%s)" % (year, race, eventType, raceId)

            cur = db.cursor()

            cur.execute("DELETE FROM practices WHERE raceId=%s AND practiceNumber=%s", (raceId, practiceNumber))

            for row in eventData:
                driverId = _getDriverId(row['Driver'], db)
                teamId = _getTeamId(row['Team'], db)

                if driverId is None or teamId is None:
                    print "Will not import entry, unknown driverId, teamId: Driver: %s, Team: %s" % (row['Driver'], row['Team'])
                    continue

                cur.execute("INSERT INTO practices (practiceNumber, raceId, driverId, "
                            "constructorId, number, position, time, milliseconds, laps, gap) "
                            "VALUES (%s, %s, %s ,%s, %s, %s, %s, %s, %s, %s)", (practiceNumber, raceId, driverId, teamId,
                                                                            row['No'], row['Pos'],
                                                                            row['Time/Retired'], _timeToMs(row['Time/Retired']),
                                                                            row['Laps'], row['Gap']))

        print "Done!"

db.close()