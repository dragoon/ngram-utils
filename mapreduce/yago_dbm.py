"""
Creates DBPedia labels-types Shelve file of the following format:

{ LABEL: [Type1, Type2, ...], ...}

For example:

Tramore:             Town, Settlement, PopulatedPlace, Place
Tramore,_Ireland:    Town, Settlement, PopulatedPlace, Place
"""

import subprocess
import urllib
from collections import defaultdict
import shelve


TYPES_FILE = 'yago_types.nt.bz2'

dbpediadb_types = defaultdict(list)
# BZ2File module cannot process multi-stream files, so use subprocess
p = subprocess.Popen('bzcat -q ' + TYPES_FILE, shell=True, stdout=subprocess.PIPE)
for line in p.stdout:
    if '<BAD URI: Illegal character' in line:
        continue
    try:
        uri, predicate, type_uri = line.split(' ', 2)
    except:
        continue
    uri = urllib.unquote(uri.replace('<http://dbpedia.org/resource/', '')[:-1])
    type_uri = type_uri.replace('<http://dbpedia.org/class/yago/', '')[:-4]

    dbpediadb_types[uri].append(type_uri)

dbpediadb = shelve.open('yago_types.dbm')

# write canonical labels first
for uri, types in dbpediadb_types.iteritems():
    dbpediadb[uri] = types


REDIRECTS_FILE = 'redirects_transitive_en.nt.bz2'
# BZ2File module cannot process multi-stream files, so use subprocess
p = subprocess.Popen('bzcat -q ' + REDIRECTS_FILE, shell=True, stdout=subprocess.PIPE)
for line in p.stdout:
    try:
        uri_redirect, predicate, uri_canon = line.split(' ', 2)
    except:
        continue
    name_redirect = urllib.unquote(uri_redirect.replace('<http://dbpedia.org/resource/', '')[:-1])
    name_canon = urllib.unquote(uri_canon.replace('<http://dbpedia.org/resource/', '')[:-4])
    if '(disambiguation)' in name_redirect:
        continue
    # skip entities that have no types
    if name_canon not in dbpediadb_types:
        continue
    dbpediadb[name_redirect] = dbpediadb_types[name_canon]

dbpediadb.close()