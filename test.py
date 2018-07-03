import python_production_server
import numpy as np


def my_test_function(in1: np.double, in2: np.ndarray(shape=(1, 2), dtype=np.integer), in3:float) -> (str, int):
    """
    My docstring
    :param in1: Input paramater
    :return: Test string
    """
    return 'Input was: ' + str(in1), in1


if __name__ == '__main__':
    python_production_server.register_function('test_archive', my_test_function)

    python_production_server.run(port=8080)
