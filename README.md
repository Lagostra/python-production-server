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

Additional options such as adding an entire package (and then as an archive) and auto-loading from a given folder might
be added at a later stage.

## Contributions
Contributions through pull requests are very welcome. I am not an expert in either MATLAB or Numpy, so there might be
things that I have overlooked in the implementation. Make sure that you explain both what you've done and why when
making a pull request.
