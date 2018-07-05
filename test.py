import python_production_server
import numpy as np


def multiply(x: np.double, y: np.double) -> np.double:
    return x * y


def dot_product(x: np.ndarray(shape=(1,), dtype=np.double), y: np.ndarray(shape=(1,), dtype=np.double)) \
                                                            -> np.double:
    return x * y


def transpose(x: np.ndarray(shape=(0, 0), dtype=np.double)) -> np.ndarray(shape=(0, 0), dtype=np.double):
    return x.T


if __name__ == '__main__':
    python_production_server.register_function('basic_arithmetics', multiply)
    python_production_server.register_function('basic_arithmetics', dot_product)
    python_production_server.register_function('basic_arithmetics', transpose)
    python_production_server.run(port=8080)
