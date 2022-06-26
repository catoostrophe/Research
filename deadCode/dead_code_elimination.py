from deadCode.dead_util import *


def elimination(repository_name, dead_var):
    """
    Eliminates dead variables
    :param repository_name: Name of the repository
    :param dead_var: list of dead variables, containing commit SHA, node in its graph,
                     and the dot file of the delta-NFG
    """

    to_delete = dict()  # Key: path to file, Value: lines of code to be deleted

    for var in dead_var:
        # Information we get from the variable
        commit = var[0]
        node = var[1]
        dot = var[2]

        # Construct graph to get the cluster and line span of each node
        graph = get_graph(repository_name, commit, dot)

        # Get node label
        label = graph.nodes[node]["label"]

        # Get the folder in which the variable is in
        cluster = graph.nodes[node]["cluster"]
        cluster_split = cluster.split('.')
        folder = cluster_split[0].replace('"', '')

        # Get the line span
        span = graph.nodes[node]["span"]
        span_split = span.split('-')
        span1 = int(span_split[0].replace('"', ''))
        span2 = int(span_split[1].replace('"', ''))
        line_span = range(span1 + 1, span2 + 2)

        # Get filename
        filename = var[2].replace(".dot", '')
        path_to_file = '.\subjects\{}\{}\{}'.format(repository_name, folder, filename)

        if path_to_file not in to_delete.keys():
            to_delete[path_to_file] = []

        # Find all lines to be deleted
        with open(path_to_file) as file:
            for num, line in enumerate(file, 1):
                if num in line_span and label.replace('"', '') in line.strip():
                    to_delete[path_to_file].append(line.strip())

    # Delete lines, eliminating dead variables
    for path_to_file in to_delete:
        for to_be_removed in to_delete[path_to_file]:
            with open(path_to_file, "r") as f:
                lines = f.readlines()
            with open(path_to_file, "w") as f:
                for line in lines:
                    if line.strip("\n").strip() != to_be_removed:
                        f.write(line)
                    else:
                        print("ELIMINATING LINE:", to_be_removed, "in file", path_to_file)
