import networkx as nx
from networkx.drawing.layout import fruchterman_reingold_layout
import igraph as ig
import community
from plotly.plotly import plot, iplot
from plotly.graph_objs import Scatter3d, Line, Layout, Marker, Scene, XAxis, YAxis, ZAxis, Margin, Annotation, Annotations, Font, Data, Figure

from functools import reduce


class NetworkFrame:

    def __init__(self, df, node_columns):
        self.df = df
        self.node_columns = node_columns
        self.nodes = self.get_nodes()
        self.edges = self.get_edges()
        self.graph = self.get_graph()
        self.colors = self.get_colors()
        self.igraph = self.get_igraph()
        self.betweenness = nx.betweenness_centrality_source(
            self.graph, normalized=True,
            weight='weight', sources=self.nodes
        )

    def get_nodes(self):
        list_of_nodes = [list(self.df[col].unique())
                         for col in self.node_columns]
        return list(set(reduce(lambda x, y: x + y, list_of_nodes)))

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

    def get_igraph(self):
        graph = ig.Graph(directed=False)
        graph.add_vertices(self.nodes)
        graph.add_edges(self.edges)
        return graph
    
    def get_colors(self):
        parts = community.best_partition(self.graph)
        return list(parts.values())

    def draw_graph(self, colors=None):
        pos = fruchterman_reingold_layout(self.graph)
        node_sizes = [100000 * x * x + 50
                      for x in list(self.betweenness.values())]

        colors = colors if colors else self.colors

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

    def get_3d_position(self):
        layt=self.igraph.layout_fruchterman_reingold(dim=3)

        N=len(self.nodes)
        Xn=[layt[k][0] for k in range(N)]# x-coordinates of nodes
        Yn=[layt[k][1] for k in range(N)]# y-coordinates
        Zn=[layt[k][2] for k in range(N)]# z-coordinates

        # Set up edge layout
        Xe=[]
        Ye=[]
        Ze=[]

        for e in self.edges:
            nodes = (e[0], e[1])
            node_index = [self.nodes.index(node) for node in nodes]
            layout = [layt[index] for index in node_index]

            Xe+=[ pos[0] for pos in layout ] + [None]# x-coordinates of edge ends
            Ye+=[ pos[1] for pos in layout ] + [None]
            Ze+=[ pos[2] for pos in layout ] + [None]
        
        return (Xn, Yn, Zn), (Xe, Ye, Ze)

    def draw_igraph(self, title, colors=None):
        (Xn, Yn, Zn), (Xe, Ye, Ze) = self.get_3d_position()
        
        trace1=Scatter3d(x=Xe,
               y=Ye,
               z=Ze,
               mode='lines',
               line=Line(color='rgb(125,125,125)', width=1, dash=True),
               hoverinfo='none'
               )

        trace2=Scatter3d(x=Xn,
                    y=Yn,
                    z=Zn,
                    mode='markers',
                    name='callers',
                    marker=Marker(symbol='dot',
                                    size= [ 100*x +5 for x in list(self.betweenness.values())],
                                    color=self.colors,
                                    colorscale='Rainbow',
                                    opacity=0.5
                                    ),
                    text=self.nodes,
                    hoverinfo='text'
                    )

        axis=dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )
        layout = Layout(
                title=title,
                width=1000,
                height=1000,
                showlegend=False,
                scene=Scene(
                xaxis=XAxis(axis),
                yaxis=YAxis(axis),
                zaxis=ZAxis(axis),
                ),
            margin=Margin(
                t=100
            ),
            hovermode='closest',
            annotations=Annotations([
                Annotation(
                showarrow=False,
                    text="Data source: ???",
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=0.1,
                    xanchor='left',
                    yanchor='bottom',
                    font=Font(
                    size=14
                    )
                    )
                ]),    )

        data=Data([trace1, trace2])
        fig=Figure(data=data, layout=layout)

        iplot(fig, filename='Call Network')