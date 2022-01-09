#Library For Python Data Science
import pandas as pd

#Library For Enable Verbose
from tqdm import tqdm

#Library For Read JSON file
import json

#Library For Math Operation
import numpy as np

#Library For Create Graph
import networkx as nx

#Library For Visualization
import matplotlib.pyplot as plt
# %matplotlib inline

#Library For Interactive Visualization
from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, EdgesAndLinkedNodes, NodesAndLinkedEdges
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap
from networkx.algorithms import community
from bokeh.plotting import curdoc
from bokeh.layouts import column


df = pd.read_csv("arxiv.csv")

df_title = df[['title']].drop_duplicates().reset_index(drop=True)
df_title.head()

df_cleaned_authors_list = df[['cleaned_authors_list']].drop_duplicates().reset_index(drop=True)
df_cleaned_authors_list.head()

df_category_list = df[['category_list']].drop_duplicates().reset_index(drop=True)
df_category_list.head()


G1 = nx.from_pandas_edgelist(df, 'title', 'cleaned_authors_list')
G2 = nx.from_pandas_edgelist(df, 'title', 'category_list')
G = nx.compose(G1,G2)

# G.nodes['C. Balázs']["Author"] ='C. Balázs'

# G.nodes['C. Balázs']

for i, j in G.nodes(data=True):
  if i in df_title.values:
    G.nodes[i]["Title"] = i
  elif i in df_cleaned_authors_list.values:
    G.nodes[i]["Author"] = i
  elif i in df_category_list.values:
    G.nodes[i]["Category"] = i

degrees = dict(nx.degree(G))
nx.set_node_attributes(G, name='degree', values=degrees)

number_to_adjust_by = 5
adjusted_node_size = dict([(node, degree+number_to_adjust_by) for node, degree in nx.degree(G)])
nx.set_node_attributes(G, name='adjusted_node_size', values=adjusted_node_size)

communities = community.greedy_modularity_communities(G)

# Create empty dictionaries
modularity_class = {}
modularity_color = {}
#Loop through each community in the network
for community_number, community in enumerate(communities):
  # print(community)
    #For each member of the community, add their community number and a distinct color
  i = community_number % len(Spectral8)
  for name in community: 
      modularity_class[name] = community_number
      modularity_color[name] = Spectral8[i]

nx.set_node_attributes(G, modularity_class, 'modularity_class')
nx.set_node_attributes(G, modularity_color, 'modularity_color')

from bokeh.models import EdgesAndLinkedNodes, NodesAndLinkedEdges

#Choose colors for node and edge highlighting
node_highlight_color = 'white'
edge_highlight_color = 'black'

#Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
size_by_this_attribute = 'adjusted_node_size'
color_by_this_attribute = 'modularity_color'

#Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
color_palette = Blues8

#Choose a title!
title = 'Paper Please'

#Establish which categories will appear when hovering over each node
HOVER_TOOLTIPS = [
       ("Title", "@Title"),
       ("Author", "@Author"),
       ("Category", "@Category"),
        ("Degree", "@degree"),
         ("Modularity Class", "@modularity_class"),
        ("Modularity Color", "$color[swatch]:modularity_color"),
]

#Create a plot — set dimensions, toolbar, and title
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
            x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

#Create a network graph object
# https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

#Set node sizes and colors according to node degree (color as category from attribute)
network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
#Set node highlight colors
network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

#Set edge opacity and width
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)
#Set edge highlight colors
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

    #Highlight nodes and edges
network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = NodesAndLinkedEdges()

plot.renderers.append(network_graph)

#show(plot)
save(plot, filename="myapp.html")

curdoc().add_root(plot)


