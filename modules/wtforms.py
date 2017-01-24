#!/usr/bin/env python
from app import app

from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
