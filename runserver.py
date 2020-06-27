#!/usr/bin/env python3

import sys
from pprint import pprint

import sys; print(sys.executable)

def show(obj):
    '''Show the dump of the properties of the object.'''
    pprint(vars(obj))

if sys.flags.interactive:
    from app import *
    print('Loading Flask App in console mode. Use show(<obj)> to introspect.')
elif __name__ == '__main__':
    from app import app
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
