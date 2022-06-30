from deadCode.dead_code_elimination import elimination
from deltaNFG.generate_deltaNFG import NFG
from deadCode.dead_code_detection import get_graph, revived_code
from testing.all_tests import run_tests

# Put the name of the repository for which you want to detect dead code here.
repository_name = "Example"

NFG(repository_name)  # Creates all delta-NFGs for each affected file of each commit

run_tests()  # Tests the implementation with the Example repository

revived_variables, dead_variables = revived_code(repository_name, 1)  # Find revived or dead variables
revived_code, dead_code = revived_code(repository_name, 2)  # Find revived or dead pieces of code

elimination(repository_name, dead_variables)  # Eliminate dead variables

# Print warnings for revived variables and pieces of code
for var in revived_variables:
    graph = get_graph(repository_name, var[0], var[2])
    print("WARNING! Revived variable (was unused):", graph.nodes[var[1]]["label"], "in file", var[2])

for line in revived_code:
    graph = get_graph(repository_name, line[0], line[2])
    print("WARNING! Revived code (was unreachable):", graph.nodes[line[1]]["label"], "in file", line[2])
