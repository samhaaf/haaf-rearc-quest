import traceback
import os


def catch_as_reject(function):

    def wrapped(resolve, reject):
        try:
            function(resolve, reject)
        except Exception as err:
            reject({
                'traceback': traceback.format_exc(),
                'error': str(err)
            })

    return wrapped


def get_environ(key):
    val = os.environ.get(key, '""')
    if val[0] == val[-1] == '"':
        val = val[1:-1]
    return val
