from deltaNFG.Util.get_commits import get_commits
import os
import networkx as nx
from deltaNFG.Util.equivalence_util import Eq_Utils
from deltaNFG.Util.pygraph_util import get_context_from_nxgraph


def bfs(graph, start):
    """
    Breadth-first search algorithm that only visits green and black nodes and edges
    :param graph: delta-NFG
    :param start: starting node
    :return: set of reachable nodes
    """

    visited, queue = dict(), [start]
    while queue:
        vertex = queue.pop(0)
        if vertex not in visited and (
                'color' not in graph.nodes[vertex].keys() or not graph.nodes[vertex]['color'] == "red"):
            visited[vertex] = len(visited)
            queue.extend(set(graph[vertex]) - set(visited))
    return visited


def get_commits_nr(subject_name):
    """
    Sort commits by oldest first
    :param subject_name: repository name
    :return: dictionary with as keys the numbers, and values the commit SHAs
    """

    # All actual commits, sorted by date
    all_commits = get_commits('./subjects/%s' % subject_name, './temp')

    # Commits for which delta-NFGs are created
    true_commits = [x[1] for x in os.walk(".\data\delta-NFGs\{}".format(subject_name))][0]

    # Sorted commits for which delta-NFGs are created
    commits = [commit for commit in all_commits if commit in true_commits]

    # Create dictionary
    i = 1
    commits_nr = dict()
    for commit in commits:
        commits_nr[i] = commit
        i += 1

    return commits_nr


def equivalent_nodes(G1, node1, G2, node2):
    """
    Check whether two nodes of different graphs are equivalent
    :param G1: graph 1
    :param node1: node 1
    :param G2: graph 2
    :param node2: node 2
    :return: True if nodes are equivalent, False otherwise
    """

    eq_utils = Eq_Utils(100, 100)

    cluster1 = nx.get_node_attributes(G1, "cluster")
    cluster2 = nx.get_node_attributes(G2, "cluster")
    label1 = nx.get_node_attributes(G1, "label")
    label2 = nx.get_node_attributes(G2, "label")

    # Check whether node labels are the same
    try:
        equivalent = eq_utils.node_label_eq(label1[node1], label2[node2])
        # equivalent = eq_utils.node_eq(G1, node1, G2, node2)
    except KeyError:
        equivalent = node1 not in label1.keys() \
                     and node2 not in label2.keys()

    # Check whether node contexts are the same
    try:
        equivalent = equivalent \
                     and eq_utils.context_eq(cluster1[node1], cluster2[node2])
    except KeyError:
        equivalent = equivalent \
                     and node1 not in cluster1.keys() \
                     and node2 not in cluster2.keys()

    return equivalent


def get_all_graphs(subject_name):
    """
    Gets all the delta-NFGs from a specified subject name
    :param subject_name: name of the repository for which we get the graphs
    :return: dictionary with as keys a tuple of the commit and the name of the file,
    and the values are the associated graphs
    """

    pdgs = dict()  # Key: tuple (commit, dotfile), value: graph G
    path_to_directory = '.\data\delta-NFGs\{}'.format(subject_name)

    for commit in os.listdir(path_to_directory):
        path_to_commit = os.path.join(path_to_directory, commit)

        for dotfile in os.listdir(path_to_commit):
            path_to_dot = os.path.join(path_to_commit, dotfile)
            G = nx.DiGraph(nx.nx_pydot.read_dot(path_to_dot))  # Get the graph

            # Remove empty node
            if '\\n' in G.nodes():
                G.remove_node('\\n')

            pdgs[(commit, dotfile)] = G

    return pdgs


def get_graph(subject_name, sp_commit, sp_dot):
    """
    Get a graph with specified commit name and .dot file
    :param subject_name: name of the repository
    :param sp_commit: commit SHA
    :param sp_dot: name of the .dot file
    :return: delta-NFG
    """

    path_to_directory = '.\data\delta-NFGs\{}'.format(subject_name)
    for commit in os.listdir(path_to_directory):
        if commit == sp_commit:
            path_to_commit = os.path.join(path_to_directory, commit)

            for dot in os.listdir(path_to_commit):
                if dot == sp_dot:
                    path_to_dot = os.path.join(path_to_commit, dot)
                    G = nx.DiGraph(nx.nx_pydot.read_dot(path_to_dot))

                    # Remove empty node
                    if '\\n' in G.nodes():
                        G.remove_node('\\n')

                    return G
    return None


def get_entry_exit_node(G):
    """
    Get the entry and exit nodes of the delta-NFG G
    :param G: delta-NFG
    :return: entry and exit nodes
    """

    contexts = get_context_from_nxgraph(G)
    entry, exit = None, None

    # Get the entry and exit nodes of the main method
    for context in contexts.values():
        if "Main" in context:
            entry, exit = find_entry_and_exit(context, G)

    # If main method does not exist, get nodes from a random context of a node in the biggest connected component
    if entry is None:
        G2 = G.copy()
        for edge in G2.edges():
            if G2.edges[edge]["style"] == "dotted":
                G.remove_edge(edge[0], edge[1])

        big_connected_comp = max(nx.connected_components(nx.Graph(G)), key=len)
        entry, exit = find_entry_and_exit(contexts[list(big_connected_comp)[0]], G)

    return entry, exit


def find_entry_and_exit(context, graph):
    """
    Find the entry and exit node of a given context of a delta-NFG
    :param context: Context of node, typically a method
    :param graph: delta-NFG
    :return: entry and exit nodes
    """

    entry = None
    exit = None

    labels = nx.get_node_attributes(graph, "label")
    clusters = nx.get_node_attributes(graph, "cluster")

    # Get the entry and exit node of a given context
    for node in graph.nodes():
        if node in labels.keys() and node in clusters.keys():
            if 'Entry' in labels[node] and clusters[node] == context:
                entry = node
            elif 'Exit' in labels[node] and clusters[node] == context:
                exit = node

    return entry, exit
