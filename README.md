# Python Production Server

A package that allows easy hosting of Python functions as REST API endpoints with a schema similar to the one used by
MATLAB Production Server. It is meant to be able to function as a drop-in replacement for the MATLAB Production Server Web API, 
allowing software that relies on this API to execute Python code with no modifications.

## Usage
To use the package, simply `import python_production_server`, and call `python_production_server.register_function` with
the function and an archive name. (The archive name corresponds to the exported MATLAB .ctf archive.) The server can
then be started with the `run` function. Note that this starts a *Flask* development server. For production deployment,
other solutions should be considered. (I have not yet looked into options for this - it might require code changes...)

Functions that are added, must be annotated (see 
[https://www.python.org/dev/peps/pep-3107/](https://www.python.org/dev/peps/pep-3107/)), so that the server
knows the types of parameters and return values. Numpy types are used (although I may have overlooked some types - feel
free to make a pull request to add them!).

The finished code may look something like this:

```python
import python_production_server
import numpy as np

def multiply(x: np.double, y: np.double) -> np.double:
    return x * y


python_production_server.register_function('basic_arithmetics', multiply)
python_production_server.run(port=8080)
```

If an array type is desired, then annotate the parameter with an np.ndarray with the correct shape and dtype. If any
dimensions are unknown, a 0 can be used. (As an effect, zero-sized dimensions are not supported.) For example, a
function that transposes an array might look like this:

```python
def transpose(x: np.ndarray(shape=(0, 0), dtype=np.double)) -> np.ndarray(shape=(0, 0), dtype=np.double):
    return x.T
```

In addition to registering single functions, you can also register a module, adding all functions inside the module.
The last option is to define an autoload package, from which all modules will be loaded. Only the first level will be
scanned; modules inside packages inside of the specified package will not be added. Note that only the module name will
be used as archive name; not the containing package. As such, there will be conflicts if registering multiple modules
with the same name, that in turn contain functions with the same name. In this case, only the last registered of these
functions will be accessible.

## Contributions
Contributions through pull requests are very welcome. I am not an expert in either MATLAB or Numpy, so there might be
things that I have overlooked in the implementation. Make sure that you explain both what you've done and why when
making a pull request.
