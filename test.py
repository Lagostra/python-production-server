import python_production_server


if __name__ == '__main__':
    python_production_server.autoload_package('autoload')
    python_production_server.run(port=8080)
