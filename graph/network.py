import networkx as nx
import community
from networkx.drawing.layout import fruchterman_reingold_layout
from functools import reduce


class NetworkFrame:

    def __init__(self, df, node_columns):
        self.df = df
        self.node_columns = node_columns
        self.nodes = self.get_nodes()
        self.edges = self.get_edges()
        self.graph = self.get_graph()
        self.betweenness = nx.betweenness_centrality_source(
            self.graph, normalized=True,
            weight='weight', sources=self.nodes
        )

    def get_nodes(self):
        list_of_nodes = [list(self.df[col].unique())
                         for col in self.node_columns]
        return set(reduce(lambda x, y: x + y, list_of_nodes))

    def get_edges(self):
        edges = []
        for i, record in self.df.iterrows():
            edge = [record[col] for col in self.node_columns]
            edges.append((edge[0], edge[1]))
        return edges

    def get_graph(self):
        G = nx.Graph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.edges)
        return G

    def draw_graph(self, colors=None):
        pos = fruchterman_reingold_layout(self.graph)
        node_sizes = [100000 * x * x + 50
                      for x in list(self.betweenness.values())]

        if not colors:
            parts = community.best_partition(self.graph)
            colors = list(parts.values())

        nx.draw_networkx_nodes(
            self.graph, pos, node_size=node_sizes, node_color=colors,
            alpha=0.5, line_color=None
        )
        nx.draw_networkx_edges(
            self.graph, pos,
            alpha=0.05, style='solid'
        )
        nx.draw_networkx_labels(
            self.graph, pos,
            {node: node for node in self.nodes},
            font_size=8
        )
