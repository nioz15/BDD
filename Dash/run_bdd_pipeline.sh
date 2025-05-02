#!/bin/bash

source ~/BDD/Dash/venv/bin/activate

# Define the virtual environment Python interpreter
VENV_PYTHON="/home/ubuntu/BDD/Dash/venv/bin/python3"

# Define paths to the scripts
XRAY_EXTRACTOR="/home/ubuntu/BDD/Dash/xray/xray_extractor_v2.sh"
BDD_CONVERTER="/home/ubuntu/BDD/Dash/xray/bdd_converter.py"

# Run the xray_extractor script
echo "Running xray_extractor_v2.sh..."
sudo -u www-data $XRAY_EXTRACTOR

if [ $? -ne 0 ]; then
  echo "Error running xray_extractor_v2.sh. Exiting."
  exit 1
fi

# Run the BDD converter script
echo "Running bdd_converter.py..."
sudo -u www-data $VENV_PYTHON $BDD_CONVERTER

if [ $? -ne 0 ]; then
  echo "Error running bdd_converter.py. Exiting."
  exit 1
fi

echo "Pipeline completed successfully."

# Restart the automation-dashboard service
sudo systemctl restart automation-dashboard.service
