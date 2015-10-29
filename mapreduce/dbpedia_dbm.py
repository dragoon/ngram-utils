"""
Creates DBPedia labels-types file of the following format:

{ LABEL: [Type1, Type2, ...], ...}

For example:

Tramore:             Town, Settlement, PopulatedPlace, Place
Tramore,_Ireland:    Town, Settlement, PopulatedPlace, Place
"""
import codecs

import subprocess
import urllib
from collections import defaultdict


TYPES_FILE = 'instance_types_en.nt.bz2'
EXCLUDES = {'Agent', 'TimePeriod', 'PersonFunction', 'Year'}

dbpediadb = codecs.open('dbpedia_types.txt', 'w', 'utf-8')

typed_entities = defaultdict(list)
# BZ2File module cannot process multi-stream files, so use subprocess
p = subprocess.Popen('bzcat -q ' + TYPES_FILE, shell=True, stdout=subprocess.PIPE)
for line in p.stdout:
    if '<BAD URI: Illegal character' in line:
        continue
    try:
        uri, predicate, type_uri = line.split(' ', 2)
    except:
        continue
    if '<http://schema.org/Person>' in type_uri:
        type_uri = '<http://dbpedia.org/ontology/Person>   '
    if 'http://dbpedia.org/ontology/' not in type_uri:
        continue
    if 'http://dbpedia.org/ontology/Wikidata' in type_uri:
        continue
    if 'http://dbpedia.org/ontology/Location' in type_uri:
        continue
    uri = urllib.unquote(uri.replace('<http://dbpedia.org/resource/', '')[:-1])
    type_uri = type_uri.replace('<http://dbpedia.org/ontology/', '')[:-4]
    if type_uri in EXCLUDES:
        continue

    typed_entities[uri].append(type_uri)
    dbpediadb.write(uri.decode('utf-8') + '\t' + type_uri + '\n')


dbpedia_redirects = codecs.open('dbpedia_redirects.txt', 'w', 'utf-8')
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
    if name_canon in typed_entities:
        for type_uri in typed_entities[name_canon]:
            dbpediadb.write(name_redirect.decode('utf-8') + '\t' + type_uri + '\n')
    dbpedia_redirects.write(name_redirect.decode('utf-8') + '\t' + name_canon.decode('utf-8') +'\n')

dbpediadb.close()
dbpedia_redirects.close()
