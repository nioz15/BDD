#!/bin/bash
source ~/BDD/Dash/venv/bin/activate
gunicorn --workers 3 --bind 0.0.0.0:8000 run_dash:app
