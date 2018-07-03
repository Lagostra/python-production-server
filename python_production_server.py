import flask
import sys
import inspect
import uuid
import numpy as np
import collections

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


def _iterify(x):
    if isinstance(x, collections.Sequence) and type(x) != str:
        return x
    return (x,)


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

            arch_response['functions'][func_name] = {
                'signatures': [{
                    'help': func.__doc__,
                    'inputs': [],
                    'outputs': []
                }]
            }

            for i, output in enumerate(_iterify(func.__annotations__['return'])):
                typ, size = _evaluate_type(output)
                arch_response['functions'][func.__name__]['signatures'][0]['outputs'].append({
                    'mwsize': size,
                    'mwtype': typ,
                    'name': 'out' + str(i+1)
                })

            for par_name in list(inspect.signature(func).parameters):
                typ, size = _evaluate_type(func.__annotations__[par_name])
                arch_response['functions'][func.__name__]['signatures'][0]['inputs'].append({
                    'mwsize': size,
                    'mwtype': typ,
                    'name': par_name
                })

        response['archives'][archive_key] = arch_response

    return flask.jsonify(response)


def _execute_function(func, params, n_arg_out=-1, mode='small', nan_format='string', inf_format='string'):
    for i, par_name in enumerate(list(inspect.signature(func).parameters)):
        params[i] = func.__annotations__[par_name](params[i])

    result = list(_iterify(func(*params)))
    result = list(map(lambda x: list(_iterify(x)), result))
    if n_arg_out != -1:
        result = result[:n_arg_out]
    if mode == 'small' and nan_format == 'string' and inf_format == 'string':
        return result


def _sync_request(archive_name, function_name, request_body):
    params = request_body['rhs']
    n_arg_out = request_body['nargout'] if 'nargout' in request_body else -1
    inf_format = 'string'
    nan_format = 'string'
    output_mode = 'small'
    if 'outputFormat' in request_body:
        if 'nanInfFormat' in request_body['outputFormat']:
            nan_format = inf_format = request_body['outputFormat']['nanInfFormat']
        if 'mode' in request_body['outputFormat']:
            output_mode = request_body['outputFormat']['mode']

    func = _archives[archive_name]['functions'][function_name]
    result = _execute_function(func, params, n_arg_out, output_mode, nan_format, inf_format)

    return flask.jsonify({'lhs': result})


def _async_request(archive_name, function_name, request_body):
    func = _archives[archive_name]['functions'][function_name]
    # TODO Implement asynchronous requests
    return 'Asynchronous requests not yet implemented'


@_app.route('/<archive_name>/<function_name>', methods=['POST'])
def _call_request(archive_name, function_name):
    mode = flask.request.args.get('mode', False)
    if mode and mode == 'async':
        return _async_request(archive_name, function_name, flask.json.loads(flask.request.data))
    else:
        return _sync_request(archive_name, function_name, flask.json.loads(flask.request.data))


def run(ip='0.0.0.0', port='8080'):
    _app.run(ip, port)
