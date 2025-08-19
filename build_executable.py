#!/usr/bin/env python3
import os
import subprocess
import sys

def build_executable() -> bool:
    print("🔨 Building EOD Generator executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=eod-generator",
        "--console",
        "--clean",
        "app.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable built successfully!")
        print(f"📁 Location: {os.path.abspath('dist/eod-generator')}")
        print("\n📋 Usage instructions:")
        print("1. Navigate to the 'dist' folder")
        print("2. Run './eod-generator' (on macOS/Linux) or 'eod-generator.exe' (on Windows)")
        print("3. The data file 'eod_data.json' will be created in the same directory")
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found!")
        print("Please install it with: pip install pyinstaller")
        return False
    
    return True

if __name__ == "__main__":
    if build_executable():
        print("\n🎉 Build complete! Your executable is ready to use.")
    else:
        print("\n💥 Build failed. Please check the errors above.")
        sys.exit(1)