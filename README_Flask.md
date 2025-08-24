# EOD Generator - Flask Web Application

This is the web-based version of the EOD (End of Day) Generator tool, converted from the original command-line interface to a modern Flask web application with a professional interface.

## Features

- **Web-based Interface**: Modern, responsive web interface using Bootstrap 5
- **Session Management**: Set up and manage session information (pack operators, location, equipment details)
- **Blocker Tracking**: Start, manage, and end blockers with real-time duration tracking
- **Ticket Management**: Associate ticket numbers and links with blockers
- **Notes**: Add detailed notes to blockers with timestamps
- **EOD Reports**: Generate comprehensive end-of-day reports with all session and blocker details
- **Test Mode**: Toggle between production and test data modes
- **Print Support**: Print-optimized EOD reports
- **Auto-save**: All data is automatically saved to JSON files

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation**:
   ```bash
   pip show flask
   ```

## Running the Application

### Method 1: Using the run script (Recommended)
```bash
python3 run_flask.py
```

### Method 2: Direct Flask execution
```bash
python3 flask_app.py
```

The application will start on **http://localhost:5001**

## File Structure

```
Eod_gen/
├── flask_app.py              # Main Flask application
├── run_flask.py              # Simple startup script
├── app.py                    # Original CLI classes (JsonHandler, EODTracker)
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── dashboard.html       # Main dashboard
│   ├── session_setup.html   # Session configuration
│   └── eod_report.html      # EOD report display
├── static/                   # Static assets
│   ├── css/
│   │   └── styles.css       # Custom styling
│   └── js/
│       └── scripts.js       # JavaScript functionality
└── eod_data_YYYY-MM-DD.json # Data files (auto-generated)
```

## Using the Web Interface

### 1. Dashboard
- **Main View**: Shows current blocker status and today's summary
- **Start Blocker**: Enter description and start tracking a new blocker
- **End Blocker**: Stop the current active blocker
- **Quick Actions**: Add tickets and notes to active blockers

### 2. Session Setup
- Configure session information including:
  - Pack and Support Operators
  - Location and Pack Numbers
  - Equipment details (Key, Glove #, Dongle #, Phone ID)

### 3. EOD Report
- Comprehensive end-of-day report showing:
  - Session information
  - All blockers with duration, tickets, and notes
  - Total time blocked and statistics
  - Print-optimized format

### 4. Features
- **Auto-refresh**: Current blocker duration updates automatically
- **Test Mode**: Toggle to use test data without affecting production
- **Data Persistence**: All data saved to date-specific JSON files
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Data Management

- **Auto-save**: All changes are automatically saved
- **Daily Files**: New JSON file created for each day
- **Data Recovery**: Application recovers active sessions on restart
- **Clear Data**: Option to clear all data (requires confirmation)

## Navigation

- **Dashboard**: Main working interface
- **Session**: Configure session details
- **EOD Report**: View comprehensive reports
- **Test Mode**: Toggle test/production modes

## Keyboard Shortcuts

- **Ctrl/Cmd + Enter**: Submit active form
- **Escape**: Close modals
- **Auto-focus**: First input field automatically focused

## API Endpoints

The Flask app provides these main routes:
- `GET /` - Dashboard
- `GET/POST /session` - Session setup
- `POST /start_blocker` - Start new blocker
- `POST /end_blocker` - End current blocker
- `POST /add_ticket` - Add ticket to current blocker
- `POST /add_note` - Add note to current blocker
- `GET /eod_report` - Display EOD report
- `POST /clear_data` - Clear all data
- `GET /toggle_test_mode` - Toggle test mode

## Original CLI Version

The original command-line interface is still available in `app.py`. To use it:

```bash
python3 app.py
```

## Technical Details

- **Flask 2.0.3**: Web framework
- **Bootstrap 5.1.3**: Frontend framework
- **Font Awesome 6.0.0**: Icons
- **JSON Storage**: File-based data persistence
- **Session Management**: Flask sessions for user state
- **Responsive Design**: Mobile-friendly interface

## Troubleshooting

1. **Port Already in Use**: The app uses port 5001. If it's busy, modify the port in `flask_app.py`
2. **Import Errors**: Ensure Flask is installed: `pip install flask`
3. **Template Errors**: Verify the `templates/` directory exists with all HTML files
4. **Static Files**: Ensure `static/css/` and `static/js/` directories exist

## Security Notes

- Change the secret key in production (`app.secret_key`)
- Use HTTPS in production environments
- Consider using a proper WSGI server (gunicorn, uwsgi) for production

## Migration from CLI

All existing data files are compatible between the CLI and web versions. The Flask app uses the same `JsonHandler` and `EODTracker` classes from the original `app.py`.