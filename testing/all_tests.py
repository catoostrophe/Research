from testing.testing_detection import *
from testing.testing_elimination import *


def run_tests():
    test_dead_variables()
    test_revived_variables()
    test_dead_functions()
    test_revived_functions()
    test_dead_variable_elimination()
    print("All tests have passed!")
