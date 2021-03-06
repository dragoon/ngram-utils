import zmq
import codecs
from kilogram import ListPacker

index_map = {}
values = []
j = 0

for line in codecs.open('wikipedia_pagelinks.tsv', 'r', 'utf-8'):
    try:
        label, value = line.strip().split('\t')
    except:
        continue
    index_map[label] = j
    values.append(zip(*ListPacker.unpack(value))[0])
    if not j % 10000:
        print j
    j += 1


def uri_map(item):
    res = []
    uri = item.decode('utf-8')
    i = index_map[uri]
    direct_neighbors = set(values[i])
    for neighbor in direct_neighbors:
        # might be a neighbor that does not exist, since we pre-filter pages
        try:
            neighbor_uris = values[index_map[neighbor]]
        except KeyError:
            continue
        count = len(direct_neighbors.intersection(neighbor_uris))
        if count > 0:
            res.append(neighbor+','+str(count))

    return uri.encode('utf-8')+'\t'+' '.join(res).encode('utf-8')

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("ipc:///tmp/wikipedia_edges")

while True:
    #  Wait for next request from client
    uri = socket.recv().strip()
    socket.send(uri_map(uri))
