from deadCode.dead_util import *


def unreachable_code(G):
    """
    Detect unreachable code from delta-NFG G
    :param G: delta-NFG
    :return: set of nodes which are unreachable
    """

    entry, exit = get_entry_exit_node(G)
    reachable = bfs(G, entry)
    return set(G.nodes()) - set(reachable)


def unused_variables(G):
    """
    Detect unused variables of given delta-NFG G
    :param G: delta-NFG
    :return: array of nodes whose labels are unused variables
    """

    labels = nx.get_node_attributes(G, "label")

    # Get all variables in the delta-NFG
    variables = []
    for vertex in G:
        try:
            label_split = labels[vertex].split(" ")
            if label_split[2] == "=":
                variables.append(vertex)
        except IndexError:
            pass

    # Find all used variables
    used_variables = []
    for variable in variables:
        out_ = G.out_edges(variable, data="style", default="pink")

        for edge in out_:
            if edge[2] == "dashed":
                used_variables.append(variable)
            elif edge[2] == "solid":
                out_node = edge[1]
                label_split = labels[variable].split(" ")
                if label_split[1] in labels[out_node]:
                    used_variables.append(variable)

    unused = set(variables) - set(used_variables)
    return unused


def revived_code(subject_name, dead_code_type):
    """
    Detect revived code by checking if the dead piece of code is revived in the newest commit
    :param graphs: list of all delta-NFGs
    :param subject_name: name of the repository
    :param dead_code_type: type of dead code. 1 is unused variables, 2 is unreachable code.
    :return: list of revived variables, and a list of revived code
    """

    # Initialisation
    dead = set()
    revived = set()
    still_dead = set()

    # Get all sorted commits
    commits = get_commits_nr(subject_name)

    # Gets all delta-NFGs of specified repository_name
    graphs = get_all_graphs(subject_name)

    # Loop through each graph and find dead code
    # Store information in lists with 3-tuples (commit, node, dotfile)
    for info in graphs:
        G = graphs[info]  # delta-NFG
        commit = info[0]  # commit SHA
        commit_nr = [k for k, v in commits.items() if v == commit][0]  # commit number, sorted by oldest
        dot = info[1]  # filename

        if dead_code_type == 1:
            dead_code = unused_variables(G)
        elif dead_code_type == 2:
            dead_code = unreachable_code(G)
        else:
            print("Invalid dead code type")
            return

        colors = nx.get_node_attributes(G, "color")

        # For each dead variable, save its filename and commit in new array
        for code in dead_code:
            if code not in colors or not colors[code] == "red" or commit_nr == 1:
                actual_commit = commit
            else:
                commit_nr -= 1
                actual_commit = commits[commit_nr]
                new_G = get_graph(subject_name, actual_commit, dot)
                for node in new_G:
                    if equivalent_nodes(new_G, node, G, code):
                        code = node
                        break

            dead.add((actual_commit, code, dot))

    # Get the SHA of the newest commit
    newest_commit_nr = max(commits.keys())
    newest_commit = commits[newest_commit_nr]

    # For each dead code, check if revived
    for dead_ in dead:
        dead_commit = dead_[0]
        dead_node = dead_[1]
        dot = dead_[2]

        # Create graphs
        dead_graph = get_graph(subject_name, dead_commit, dot)
        newest_graph = get_graph(subject_name, newest_commit, dot)

        while newest_graph is None:
            newest_commit_nr -= 1
            newest_commit = commits[newest_commit_nr]
            newest_graph = get_graph(subject_name, newest_commit, dot)

        colors = nx.get_node_attributes(newest_graph, "color")

        # If the dead variable is in the newest commit, it cannot be revived
        if not newest_commit == dead_commit:
            for node in newest_graph:

                # Find node in newest delta-NFG that is equivalent to the dead variable
                # If there is none, the dead variable was removed
                if equivalent_nodes(newest_graph, node, dead_graph, dead_node) and (
                        node not in colors or not colors[node] == "red"):

                    # Check if node is still dead, if it is not, it is revived
                    if (newest_commit, node, dot) in dead:
                        still_dead.add((newest_commit, node, dot))
                    else:
                        revived.add((newest_commit, node, dot))
                    continue
        else:
            still_dead.add(dead_)

    return list(revived), list(still_dead)
