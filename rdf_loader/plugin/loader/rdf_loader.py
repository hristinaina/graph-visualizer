from rdflib import Graph
from plugin.core.services.loader import BaseLoader
from plugin.core.models import Vertex
from plugin.core.models import Graph as G


class RdfLoader(BaseLoader):
    def __init__(self) -> None:
        self.id_counter = 0
        self.graph = None

    def create_vertex(self, node, graph):
        for vertex in graph.vertices:
            if vertex.attributes["name"] == node:
                return vertex

        self.id_counter += 1
        v = Vertex(self.id_counter)
        v.attributes["name"] = node
        self.graph.insert_vertex(v)
        return v

    def populate_graph(self, nodes):
        (subject, predicate, object) = nodes
        first_vertex = self.create_vertex(subject, self.graph)
        second_vertex = self.create_vertex(object, self.graph)
        self.graph.insert_edge(first_vertex, second_vertex, True, predicate)

    def load_file(self, file_path):
        g = Graph()
        g.parse(file_path)
        for row in g:
            self.populate_graph(row)

    def make_graph(self, file_path, name):
        self.graph = G(name)
        self.load_file(file_path)
        return self.graph
