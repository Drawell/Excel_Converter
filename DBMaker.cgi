#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__) + '/ExelConverter'))

from wsgiref.handlers import CGIHandler

from DBMaker import app

app.debug = True
CGIHandler().run(app)
