#!/bin/bash

# Exact instructions to run ALOHA 3D visualization

echo "Setting up ALOHA environment..."

# 1. First, deactivate any current conda environment
echo "Step 1: Deactivating current environment..."
conda deactivate

# 2. Activate the aloha_env
echo "Step 2: Activating aloha_env..."
conda activate aloha_env

# 3. Verify we're using the correct Python
echo "Step 3: Verifying Python version..."
python --version

# 4. Run the scripts
echo "Step 4: Listing available environments..."
python list_aloha_envs.py

echo "Step 5: Run visualization (optional)..."
echo "To run visualization, execute: python visualize_aloha.py"