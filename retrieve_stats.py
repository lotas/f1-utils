__author__ = "Yaraslau Kurmyza"
__license__ = "GPL"
__email__ = "lotask@gmail.com"

"""
Retrieve times from F1.com website

Times of interest: 
  * practice 1, 2, 3  
  ** qualifying
  ** race

Invoke:
python retrieve_stats YEAR GPNAME EVENT
  GPNAME i.e. Spain, Monaco, etc
  EVENT "practice 1", "practice 2", "practice 3", "qualifying", "race", "all"

Returns json-string
 {
   year:
   {
      gpname:
      {
        event: [results-array],
        ...
      }
   }
 }

Dependencies:
    BeautifulSoup: 
        #easy_install beautifulsoup4
        or
        #apt-get install python-beautifulsoup


"""

import re
import sys
import urllib
import pickle
import json
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag
from BeautifulSoup import NavigableString

from pprint import pprint


if len(sys.argv) < 3:
    print "Not enough arguments."
    print sys.argv[0], " year gp-name [type]"
    print ""
    print "\t   year: i.e. 2013"
    print "\tgp-name: i.e. Monaco"
    print "\t   type: practice 1|practice 2|practice 3|qualifying|race|all default 'all'"
    print ""
    exit(1)



def _absUrl(url):
    """
    Makes absolute url if needed
    """
    return url if url.startswith('http:') else ("http://www.formula1.com" + url)    

def _fmtNode(node):
    """
    Parsing table rows, node could be simple text or another list of nodes (<a>text</a>)
    we need only text part here
    """
    if type(node) == list and len(node) > 0:
        if isinstance(node[0], Tag):
            return unicode(node[0].string)
        else:
            return unicode(node[0])

    return unicode(node)

def findGpUrl(year, gpname):
    """
    finds all links with 'gpname' within them
    and returns first one found
    """
    soup = BeautifulSoup(urllib.urlopen("http://www.formula1.com/results/season/%s/" % year ))    
    eventLink = [a.parent['href'] for a in soup.findAll("a", text=re.compile(gpname))]

    if len(eventLink) == 0:
        print "No GP found for year=%s and gpname=%s" % (year, gpname)
        sys.exit(1)

    return eventLink[0]

def parseGpEvent(gpUrl, eventType):
    """
    parse times for specific gp
    eventType: practice X|qualifying|race

    gp url is a race results url, for past events
    """

    soup = BeautifulSoup(urllib.urlopen(_absUrl(gpUrl)))

    # adjust url for different types
    if eventType != 'race':
        links = [a.parent['href'] for a in soup.findAll('a', text=re.compile(eventType.upper()))]
        if len(links) == 0:
            print "Event type: %s not found for GP %s" % (eventType, gpUrl)
            return

        soup = BeautifulSoup(urllib.urlopen(_absUrl(links[0])))

    # find table with results
    # there seems to be only one table with rows at the moment
    table = soup.findAll("tr")

    hdr = [_fmtNode(x.contents) for x in table[0].contents if isinstance(x, Tag)]

    lns = []
    for row in table[1::]:
        tds = [_fmtNode(x.contents) for x in row.contents if isinstance(x, Tag)]

        # datarow = dict(zip(hdr, tds))
        lns.append(dict(zip(hdr, tds)))

    return lns

  

year = sys.argv[1]
gpname = sys.argv[2]
rtype = sys.argv[3] if len(sys.argv) == 4 else 'all'


if rtype == 'all':
    rtype = ['practice 1', 'practice 2', 'practice 3', 'qualifying', 'race']
else:
    rtype = [rtype]

gpUrl = findGpUrl(year, gpname)

events = {}
for eventType in rtype:
    events[eventType] = parseGpEvent(gpUrl, eventType)

data = {}
data[year] = {}
data[year][gpname] = events

print json.dumps(data)

