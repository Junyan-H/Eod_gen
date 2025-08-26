#!/usr/bin/env python3
"""
Production server script with proper configuration
"""
import os
import sys
from pathlib import Path

def main():
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    
    # Check for required environment variables
    if not os.environ.get('SECRET_KEY'):
        print("ERROR: SECRET_KEY environment variable must be set in production")
        print("Example: export SECRET_KEY='your-secure-random-key-here'")
        sys.exit(1)
    
    # Add parent directory to path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    try:
        from src.flask_app import app
        
        print("=" * 60)
        print("EOD Generator - Production Server")
        print("=" * 60)
        print("Environment: Production")
        print("Debug Mode: OFF")
        print(f"URL: http://{app.config['HOST']}:{app.config['PORT']}")
        print("=" * 60)
        print("For production deployment, consider using:")
        print("  - Gunicorn: gunicorn -w 4 -b 0.0.0.0:5001 src.flask_app:app")
        print("  - uWSGI: uwsgi --http :5001 --module src.flask_app:app")
        print("=" * 60)
        
        app.run(debug=False, 
               host=app.config['HOST'], 
               port=app.config['PORT'],
               use_reloader=False)
               
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProduction server stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()