import flask
import string
import random
import sys

_archives = {}
_type_map = {
    str: 'char',
    float: 'double',
    int: 'int32',
    bool: 'logical'
}

_app = flask.Flask(__name__)


def register_function(archive, func):
    if archive not in _archives:
        _archives[archive] = {
            'uuid': archive + '_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
            'functions': []
        }
    _archives[archive]['functions'].append(func)


@_app.route('/api/discovery')
def _discovery():
    response = {
        'discoverySchemaVersion': '1.0.0',
        'archives': {}
    }

    vi = sys.version_info
    py_version = str(vi[0]) + '.' + str(vi[1]) + '.' + str(vi[2])
    for archive_key, archive in _archives.items():
        arch_response = {
            'archiveSchemaVersion': '1.0.0',
            'archiveUuid': archive['uuid'],
            'functions': {},
            'matlabRuntimeVersion': py_version
        }

        for func in archive['functions']:
            assert len(func.__annotations__), 'All functions must be annotated!'
            assert 'return' in func.__annotations__, 'Return type must be annotated!'

            arch_response['functions'][func.__name__] = {
                'signatures': [{
                    'inputs': [],
                    'outputs': [
                        {
                            'mwsize': [],
                            'mwtype': _type_map[func.__annotations__['return']],
                            'name': 'out'
                        }
                    ]
                }]
            }

            for name, typ in func.__annotations__.items():
                if name == 'return':
                    continue

                arch_response['functions'][func.__name__]['signatures'][0]['inputs'].append({
                    'mwsize': [],
                    'mwtype': _type_map[typ],
                    'name': name
                })

        response['archives'][archive_key] = arch_response

    return flask.jsonify(response)


def run():
    _app.run('0.0.0.0', 8080)
