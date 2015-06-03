#!/usr/bin/env python3
from flask.ext.script import Manager

from kkaas import app

manager = Manager(app)

if __name__ == "__main__":
    manager.run()
