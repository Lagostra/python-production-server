import python_production_server


def my_test_function(in1: float) -> str:
    return 'Input was: ' + str(in1)

if __name__ == '__main__':
    python_production_server.register_function('test_archive', my_test_function)

    python_production_server.run()