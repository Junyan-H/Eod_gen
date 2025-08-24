#!/usr/bin/env python3
"""
Simple script to run the Flask EOD Generator application
"""
import os
import sys

if __name__ == '__main__':
    # Add current directory to path so we can import our modules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        from flask_app import app
        print("Starting EOD Generator Flask Application...")
        print("Access the application at: http://localhost:5001")
        print("Press Ctrl+C to stop the server")
        app.run(debug=True, host='0.0.0.0', port=5001)
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