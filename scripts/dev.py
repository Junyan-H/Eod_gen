#!/usr/bin/env python3
"""
Development server script with hot reload and debugging
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Add parent directory to path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    try:
        from src.flask_app import app
        
        print("=" * 60)
        print("EOD Generator - Development Server")
        print("=" * 60)
        print("Environment: Development")
        print("Debug Mode: ON")
        print("Hot Reload: ON")
        print(f"URL: http://localhost:{app.config['PORT']}")
        print("-" * 60)
        print("TypeScript compilation: Run 'npm run build:watch' in another terminal")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        app.run(debug=True, 
               host=app.config['HOST'], 
               port=app.config['PORT'],
               use_reloader=True)
               
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        print("  npm install")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDevelopment server stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()