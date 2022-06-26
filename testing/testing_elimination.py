from deadCode.dead_code_elimination import elimination
from deadCode.dead_code_detection import revived_code


def test_dead_variable_elimination():
    """
    Testing whether the function "elimination" truly eliminates the dead variable
    """

    # Getting the dead variable
    repository_name = "Example"
    dead_variables = revived_code(repository_name, 1)[1]

    to_delete = "int deadVariable2 = 20;"  # Line to be deleted
    path_to_file = "./subjects/Example/Example/Program.cs"

    # Check whether the line is there
    with open(path_to_file, "r") as f:
        lines_before = [line.strip("\n").strip() for line in f.readlines()]
        assert to_delete in lines_before

    # Eliminate it
    elimination(repository_name, dead_variables)

    # Check if it is eliminated
    with open(path_to_file, "r") as f:
        contents = f.readlines()
        lines_after = [line.strip("\n").strip() for line in contents]
        assert to_delete not in lines_after

    # Check if no other line has been deleted
    lines_before.remove(to_delete)
    assert lines_before == lines_after

    # Reinsert the deleted line
    contents.insert(16, "            int deadVariable2 = 20;\n")
    with open(path_to_file, "w") as f:
        contents = "".join(contents)
        f.write(contents)
        assert to_delete in contents