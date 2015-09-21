from __future__ import division
from collections import defaultdict
import networkx as nx
from kilogram import NgramService


class SemanticGraph:
    G = None
    candidates = None
    uri_fragment_counts = None

    def __init__(self, candidates):
        self.G = nx.DiGraph()
        self.candidates = candidates
        for i, cand_i in enumerate(candidates):
            """
            :type cand_i: CandidateEntity
            """
            for j, cand_j in enumerate(candidates):
                if i != j:
                    for uri_i in cand_i.candidates.keys():
                        for uri_j in cand_j.candidates.keys():
                            if not self.G.has_edge(uri_i, uri_j):
                                weight = NgramService.get_wiki_edge_weight(uri_i, uri_j)
                                if weight > 0:
                                    self.G.add_edge(uri_i, uri_j, {'w': weight})
        self.uri_fragment_counts = defaultdict(lambda: 0)
        for cand in candidates:
            # immediately prune nodes without connections
            for uri in cand.candidates.keys():
                if self.G.has_node(uri):
                    self.uri_fragment_counts[uri] += 1
                else:
                    del cand.candidates[uri]

    def _calculate_scores(self, candidate):
        total = 0
        scores = {}
        # pre-compute numerators and denominator
        for uri in candidate.candidates.keys():
            w = self.uri_fragment_counts[uri]/(len(self.candidates)-1)
            scores[uri] = (self.G.degree(uri) or 0)*w
            total += scores[uri]
        for uri in scores.keys():
            scores[uri] /= total
        return scores

    def do_iterative_removal(self):
        while True:
            candidate = max(self.candidates, key=lambda x: len(x.candidates))
            if len(candidate.candidates) < 10:
                break
            scores = self._calculate_scores(candidate)
            min_uri = min(scores.items(), key=lambda x: x[1])[0]
            cur_avg_deg = 2*self.G.number_of_edges()/self.G.number_of_nodes()

            G_star = self.G.copy()
            G_star.remove_node(min_uri)
            avg_deg = 2*G_star.number_of_edges()/G_star.number_of_nodes()
            if avg_deg > cur_avg_deg:
                del candidate.candidates[min_uri]
                self.G = G_star

    def do_linking(self):
        for candidate in self.candidates:
            scores = self._calculate_scores(candidate)
            max_uri = max(scores.items(), key=lambda x: x[1])[0]
            candidate.true_entity = max_uri

