import python_production_server
import numpy as np


def multiply(x: np.double, y: np.double) -> np.double:
    return x * y


if __name__ == '__main__':
    python_production_server.register_function('basic_arithmetics', multiply)
    python_production_server.run(port=8080)
