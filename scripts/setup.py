#!/usr/bin/env python3
"""
Setup script for EOD Generator project
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"  ✓ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {description}")
        print(f"    Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("EOD Generator - Project Setup")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = True
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        success = False
    
    # Install Node.js dependencies (if package.json exists in config)
    config_dir = project_root / 'config'
    if (config_dir / 'package.json').exists():
        os.chdir(config_dir)
        if not run_command("npm install", "Installing Node.js dependencies"):
            success = False
        os.chdir(project_root)
    
    # Compile TypeScript
    if (config_dir / 'package.json').exists():
        os.chdir(config_dir)
        if not run_command("npm run build", "Compiling TypeScript"):
            success = False
        os.chdir(project_root)
    
    # Create data directories
    data_dirs = [
        'data/production',
        'data/test'
    ]
    
    for dir_path in data_dirs:
        dir_full_path = project_root / dir_path
        dir_full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created directory: {dir_path}")
    
    print("=" * 60)
    if success:
        print("Setup completed successfully!")
        print("\nTo start development:")
        print("  python3 scripts/dev.py")
        print("\nTo start production:")
        print("  export SECRET_KEY='your-secret-key'")
        print("  python3 scripts/prod.py")
        print("\nTo develop with TypeScript:")
        print("  cd config && npm run dev")
    else:
        print("Setup completed with errors. Please check the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()