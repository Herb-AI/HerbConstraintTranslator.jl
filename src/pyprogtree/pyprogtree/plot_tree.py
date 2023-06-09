import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from pyprogtree.grammar import *
import random

def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    """
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        """
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        """

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def plot_tree(g, parent, rule=None, show_rules=True, show_types=False, show_node_index=False, show_empty_nodes=False, show_lambda_string=None, save_fig=False):
    """
    :param g: Grammar
    :param parent: Array(0..N-2) of var int representing the parent of each node. (Node N-1 is assumed to be the root node)
    :param rule: Array(0..N-1) of var int representing the rule of each node
    :param show_rules: boolean indicating whether the rule name of the nodes should be shown
    :param show_types: boolean indicating whether the rule type of the nodes should be shown
    :param show_node_index: boolean indicating if the the node index should be shown INSTEAD of the content of the node
    :param show_empty_nodes: boolean indicating whether nodes with the empty rule should be shown
    :param show_lambda_string: lambda: n -> string. (for debugging purposes)
    :param save_fig: boolean indicating whether the plot should be saved in the 'figures/' folder
    """
    N = len(parent) + 1
    labels = None
    if rule is not None:
        for r in enumerate(rule):
            if r[1] is None:
                raise Exception(f"Cannot plot a tree: 'rule[{r[0]}]' is undecided")
        labels = {n: (show_lambda_string(n) if not show_lambda_string is None else "") +
                     show_node_index * f"[{n}] " +
                     show_types * f"{g.TYPE_NAMES[g.TYPES[rule[n].value()]]}: " +
                     show_rules * g.RULE_NAMES[rule[n].value()] for n in range(N)}
        for n in range(N):
            if g.RULE_NAMES[rule[n].value()] == "":
                del labels[n]

    edges = [e for e in enumerate(parent.value())]
    for e in edges:
        if e[1] is None:
            raise Exception(f"Cannot plot a tree: 'parent[{e[0]}]' is undecided")

    if not show_empty_nodes and rule is not None:
        edges = list(filter(lambda e: g.TYPE_NAMES[g.TYPES[rule[e[0]].value()]] != "", edges))

    G=nx.Graph()
    G.add_edges_from(edges[::-1])
    pos = hierarchy_pos(G, N-1) #we assume node N-1 is the root

    nx.draw(G, pos=pos, with_labels=labels is not None, labels=labels, node_color="white")
    if save_fig:
        plt.savefig("figures/figure" + str(np.random.rand()).replace(".", "")) #to manually verify trees
    plt.show()
