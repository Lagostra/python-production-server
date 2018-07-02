import flask
import sys
import inspect
import uuid
import numpy as np

_archives = {}
_type_map = {
    str: 'char',
    float: 'double',
    int: 'int32',
    bool: 'logical',
    'float64': 'double',
    'int8': 'int8',
    'int16': 'int16',
    'int32': 'int32',
    'int64': 'int64',
    'uint8': 'uint8',
    'uint16': 'uint16',
    'uint32': 'uint32',
    'uint64': 'uint64',
    np.int64: 'int64',
    np.int32: 'int32',
    np.int16: 'int16',
    np.int8: 'int8',
    np.uint64: 'uint64',
    np.uint32: 'uint32',
    np.uint16: 'uint16',
    np.uint8: 'uint8',
    np.bool_: 'logical',
    np.float64: 'double',
    np.float32: 'single'
}

_reverse_type_map = {
    'char': str,
    'double': np.double,
    'single': np.float32,
    'int8': np.int8,
    'int16': np.int16,
    'int32': np.int32,
    'int64': np.int64,
    'uint8': np.uint8,
    'uint16': np.uint16,
    'uint32': np.uint32,
    'uint64': np.uint64,
    'logical': np.bool_,
}

_app = flask.Flask(__name__)


def register_function(archive, func):
    if archive not in _archives:
        _archives[archive] = {
            'uuid': archive[:12] + '_' + uuid.uuid4().hex,
            'functions': {}
        }
    _archives[archive]['functions'][func.__name__] = func


def _evaluate_type(annotation):
    if type(annotation) == np.ndarray:
        typ = _type_map[annotation.dtype.__str__()]
        size = annotation.shape
    else:
        typ = _type_map[annotation]
        size = [1, 1]

    if typ == 'char':
        size = [1, 'X']
    return typ, size


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

            out_type = _evaluate_type(func.__annotations__['return'])
            arch_response['functions'][func_name] = {
                'signatures': [{
                    'help': func.__doc__,
                    'inputs': [],
                    'outputs': [
                        {
                            'mwsize': out_type[1],
                            'mwtype': out_type[0],
                            'name': 'out'
                        }
                    ]
                }]
            }

            for par_name in list(inspect.signature(func).parameters):
                typ, size = _evaluate_type(func.__annotations__[par_name])
                arch_response['functions'][func.__name__]['signatures'][0]['inputs'].append({
                    'mwsize': size,
                    'mwtype': typ,
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
