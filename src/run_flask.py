#!/usr/bin/env python3
"""
Simple script to run the Flask EOD Generator application
"""
import os
import sys
from pathlib import Path

if __name__ == '__main__':
    # Add parent directory to path for imports
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    try:
        from src.flask_app import app

        # there is prod and dev
        config = app.config
        
        print("Starting EOD Generator Flask Application...")
        # running dev
        print(f"Environment: {config.get('ENV', 'development')}")
        print(f"Access the application at: http://{config['HOST']}:{config['PORT']}")
        print("Press Ctrl+C to stop the server")
        
        app.run(debug=config['DEBUG'], 
               host=config['HOST'], 
               port=config['PORT'])
               
    except ImportError as e:
        print(f"Error importing Flask application: {e}")
        print("Make sure Flask is installed: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down Flask application...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Flask application: {e}")
        sys.exit(1)