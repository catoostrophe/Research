from deadCode.dead_code_detection import *


def test_revived_functions():
    """
    Check whether the function reports the correct revived nodes
    """

    # Get revived nodes
    repository_name = "Example"
    revived_functions = revived_code(repository_name, 2)[0]

    assert len(revived_functions) == 3

    # These should be the labels of the nodes that are revived
    correct_labels = [
        '"return 21;"',
        '"Entry Example.Program.dead_function()"',
        '"Exit Example.Program.dead_function()"'
    ]

    for var in revived_functions:
        commit = var[0]
        node = var[1]
        dot = var[2]

        # Construct graph to get the cluster and line span of each node
        graph = get_graph(repository_name, commit, dot)

        # Get node label
        label = graph.nodes[node]["label"]

        assert label in correct_labels
        correct_labels.remove(label)  # Remove it so no other node can use the label


def test_dead_functions():
    """
    Check whether the function reports the correct number of dead nodes
    """

    repository_name = "Example"
    dead_functions = revived_code(repository_name, 2)[1]

    assert len(dead_functions) == 0


def test_revived_variables():
    """
    Check if the function returns the correct revived variables
    """

    repository_name = "Example"
    revived_variables = revived_code(repository_name, 1)[0]

    assert len(revived_variables) == 1

    # Information we get from the variable
    var = revived_variables[0]
    commit = var[0]
    node = var[1]
    dot = var[2]

    # Construct graph to get the cluster and line span of each node
    graph = get_graph(repository_name, commit, dot)

    # Get node label
    label = graph.nodes[node]["label"]

    assert label == '"int deadVariable = 10"'


def test_dead_variables():
    """
    Check if the function returns the correct dead variables
    """

    repository_name = "Example"
    dead_variables = revived_code(repository_name, 1)[1]

    assert len(dead_variables) == 1

    # Information we get from the variable
    var = dead_variables[0]
    commit = var[0]
    node = var[1]
    dot = var[2]

    # Construct graph to get the cluster and line span of each node
    graph = get_graph(repository_name, commit, dot)

    # Get node label
    label = graph.nodes[node]["label"]

    assert label == '"int deadVariable2 = 20"'
