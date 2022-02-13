#!/bin/sh

set -e

python3 app.py init-config

flask db upgrade
flask run --host=0.0.0.0
