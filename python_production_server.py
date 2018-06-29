import flask
import string
import random
import sys
import inspect
import uuid

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
            'uuid': archive[:12] + '_' + uuid.uuid4().hex,
            'functions': {}
        }
    _archives[archive]['functions'][func.__name__] = func


@_app.route('/api/discovery', methods=['GET'])
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

        for func_name, func in archive['functions'].items():
            assert len(func.__annotations__), 'All functions must be annotated!'
            assert 'return' in func.__annotations__, 'Return type must be annotated!'

            arch_response['functions'][func_name] = {
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

            for par_name in list(inspect.signature(func).parameters):
                arch_response['functions'][func.__name__]['signatures'][0]['inputs'].append({
                    'mwsize': [],
                    'mwtype': _type_map[func.__annotations__[par_name]],
                    'name': par_name
                })

        response['archives'][archive_key] = arch_response

    return flask.jsonify(response)


def _sync_request(archive_name, function_name, request):
    params = flask.json.loads(request.form['rhs'])
    func = _archives[archive_name]['functions'][function_name]

    for i, par_name in enumerate(list(inspect.signature(func).parameters)):
        params[i] = func.__annotations__[par_name](params[i])

    result = func(*params)

    return flask.jsonify({'lhs': result})


def _async_request(archive_name, function_name, request):
    func = _archives[archive_name]['functions'][function_name]
    # TODO Implement asynchronous requests
    return 'Asynchronous requests not yet implemented'


@_app.route('/<archive_name>/<function_name>', methods=['POST'])
def _call_function(archive_name, function_name):
    mode = flask.request.args.get('mode', False)
    if mode and mode == 'async':
        return _async_request(archive_name, function_name, flask.request)
    else:
        return _sync_request(archive_name, function_name, flask.request)



def run(ip='0.0.0.0', port='8080'):
    _app.run(ip, port)
