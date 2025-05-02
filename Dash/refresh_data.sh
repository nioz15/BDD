#!/bin/bash

# Define the virtual environment Python interpreter
VENV_PYTHON="/home/ubuntu/BDD/Dash/venv/bin/python3"

# Run the open_search.py script
sudo -u www-data $VENV_PYTHON /home/ubuntu/BDD/Dash/open_search.py

# Run the fetch_and_update.py script
sudo -u www-data $VENV_PYTHON /home/ubuntu/BDD/Dash/fetch_and_update.py

# Restart the automation-dashboard service
sudo systemctl restart automation-dashboard.service
