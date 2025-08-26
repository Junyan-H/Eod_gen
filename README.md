# EOD Generator - End of Day Report Tool

A comprehensive Flask web application for standardizing and automating operators' end-of-day reports while providing management with objective performance metrics.

## Features

### Operator Interface
- **Web Dashboard**: Modern, responsive Bootstrap 5 interface for operators
- **CLI Interface**: Original command-line tool (preserved)
- **Session Management**: Track operators, location, and equipment details
- **Blocker Tracking**: Start, manage, and end blockers with real-time duration tracking
- **Category System**: Classify blockers by type (Software, Connectivity, Hardware, Other)
- **Ticket Integration**: Associate support tickets and links with blockers
- **Notes System**: Add timestamped notes to blockers for detailed documentation
- **EOD Reports**: Generate comprehensive, print-friendly daily reports
- **Test Mode**: Toggle between production and test data environments

### Manager Dashboard ✨
- **Performance Analytics**: 7-day performance overview and trending
- **Efficiency Metrics**: Automated calculation using formula: `(8hrs - breaks - downtime) / 8hrs * 100%`
- **Category Analysis**: Visual breakdown of operational pain points by issue type
- **Daily Performance Tracking**: Operator efficiency, incident counts, and resolution times
- **Problem Area Identification**: Ranking of most time-consuming issue categories
- **Performance Insights**: Automated recommendations based on historical data
- **Print-Friendly Reports**: Clean layouts for management reporting

## Project Structure

```
Eod_gen/
├── src/                          # Source code (main application)
│   ├── flask_app.py             # Main Flask web application
│   ├── app.py                   # Original CLI application & core classes
│   └── run_flask.py             # Flask startup script with configuration
├── config/                       # Configuration & build files
│   ├── __init__.py             # Python package init
│   ├── app_config.py          # Flask configuration classes (dev/prod)
│   ├── package.json           # Node.js dependencies for TypeScript
│   └── tsconfig.json          # TypeScript compiler configuration
├── data/                        # Data storage (JSON files)
│   ├── production/            # Production EOD data files
│   │   └── eod_data_2025-08-24.json
│   └── test/                  # Test data files
│       ├── eod_data.json
│       ├── eod_data_2025-08-19.json
│       └── test_data.json
├── scripts/                     # Development & utility scripts
│   ├── build_executable.py   # Build standalone executable
│   ├── dev.py                # Development server launcher
│   ├── prod.py               # Production server launcher
│   └── setup.py              # Project setup script
├── static/                      # Frontend assets
│   ├── css/styles.css         # Custom styling
│   ├── js/
│   │   ├── dist/              # Compiled TypeScript output
│   │   ├── legacy/            # Original JavaScript (archived)
│   │   └── scripts.js         # Current JavaScript
│   └── ts/scripts.ts          # TypeScript source code
├── templates/                   # Jinja2 HTML templates
│   ├── base.html             # Base template with navigation
│   ├── dashboard.html        # Operator dashboard
│   ├── eod_report.html       # EOD report display
│   ├── manager_dashboard.html # Manager analytics dashboard
│   └── session_setup.html    # Session configuration
├── docs/                       # Documentation
├── node_modules/               # Node.js dependencies (auto-generated)
├── Makefile                    # Command shortcuts
├── package.json               # Root package.json
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── README_Flask.md           # Flask-specific documentation
```

## Installation & Setup

### Prerequisites
- Python 3.6+
- Node.js 16+ (for TypeScript development)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/Junyan-H/Eod_gen.git
cd Eod_gen

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for TypeScript development)
npm install

# Compile TypeScript (optional - for frontend development)
npx tsc --project config/tsconfig.json

# Start the Flask application
python3 src/run_flask.py
```

Access the application at **http://localhost:5001**

### Alternative Start Methods
```bash
# Using development script
python3 scripts/dev.py

# Using production script  
python3 scripts/prod.py

# Direct CLI mode (original interface)
python3 src/app.py
```

## Usage

### Web Interface
1. **Operator Dashboard**: Main interface for blocker management with category selection
2. **Manager Dashboard**: Analytics view with performance metrics and trends *(http://localhost:5001/manager)*
3. **Session Setup**: Configure session information and equipment details
4. **EOD Reports**: Generate comprehensive, print-friendly daily reports with category breakdowns
5. **Test Mode**: Toggle between production and test data environments

### Command Line Interface
```bash
# Run original CLI version
python3 src/app.py
```

## Development

### TypeScript Development
```bash
# Watch mode (auto-compile TypeScript)
npm run build:watch

# Development mode (TypeScript + Flask)
npm run dev

# Clean build
npm run clean && npm run build
```

### Project Scripts
```bash
# Development server
npm run dev

# Production build
npm run build:prod

# Run tests
npm run test

# Clean project
npm run clean:all
```

## Architecture

### Backend (Python/Flask)
- **Flask 2.0.3**: Web framework
- **JsonHandler**: Data persistence layer
- **EODTracker**: Core business logic
- **Session management**: Flask sessions

### Frontend (TypeScript/JavaScript)
- **TypeScript 5.0**: Type-safe development
- **Bootstrap 5.1.3**: UI framework
- **Font Awesome 6.0**: Icons
- **Custom CSS**: Application styling

### Data Storage
- **JSON files**: File-based persistence
- **Date-based**: Automatic daily file creation
- **Test/Production**: Separate data environments

## API Reference

### Main Routes
- `GET /` - Operator Dashboard
- `GET /manager` - Manager Analytics Dashboard  
- `GET|POST /session` - Session management
- `POST /start_blocker` - Start new blocker with category
- `POST /end_blocker` - End current blocker
- `POST /add_ticket` - Add ticket to blocker
- `POST /add_note` - Add note to blocker
- `GET /eod_report` - EOD report with category breakdown
- `POST /clear_data` - Clear all data
- `GET /toggle_test_mode` - Toggle test mode

### Key Enhancements ✨
- **Blocker Categorization**: Software, Connectivity, Hardware, Other
- **Manager Analytics**: 7-day performance tracking and efficiency metrics
- **Category Analytics**: Visual breakdown of operational pain points
- **Performance Insights**: Automated recommendations based on data trends

## Configuration

### Environment Variables
```bash
# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=true

# Application settings
EOD_DATA_DIR=./data/production
EOD_TEST_DIR=./data/test
```

### TypeScript Configuration
See `config/tsconfig.json` for TypeScript compiler options.

### File Organization
The project follows a clean, organized structure:
- **No duplicate files**: All duplicates have been removed
- **src/**: Contains all Python application code
- **config/**: Configuration files for both Python and TypeScript
- **data/**: Separated production and test data environments
- **static/**: Frontend assets with TypeScript compilation support
- **scripts/**: Development utilities and build scripts

### Data File Structure
```json
{
  "blockers": [
    {
      "description": "Issue description",
      "category": "software|connectivity|hardware|other",
      "start_time": "2025-08-26 10:30:00",
      "end_time": "2025-08-26 11:15:00", 
      "duration_minutes": 45,
      "tickets": [
        {
          "number": "TICKET-123",
          "link": "LINK: https://support.example.com/ticket/123"
        }
      ],
      "notes": [
        {
          "content": "Detailed troubleshooting notes",
          "timestamp": "2025-08-26 10:35:00"
        }
      ]
    }
  ],
  "current_blocker": null,
  "last_updated": "2025-08-26 11:15:00",
  "session_info": {
    "pack_operator": "Operator Name",
    "support_operator": "Support Name", 
    "location": "Site Location",
    "pack_number": "Pack123",
    "key_used": "Key456",
    "glove_number": "Glove789",
    "dongle_number": "Dongle012",
    "phone_id": "Phone345",
    "date": "2025-08-26",
    "initialized_at": "2025-08-26 08:00:00"
  }
}
```

## Testing

### Manual Testing
1. Start application: `python3 src/run_flask.py`
2. Enable test mode in web interface
3. Test blocker workflow
4. Generate EOD report

### Data Validation
- Test data stored in `data/test/`
- Production data in `data/production/`
- Automatic session recovery

## Features Detail

### Session Management
Track detailed session information:
- Pack and Support Operators
- Location and Pack Numbers
- Equipment details (Keys, Gloves, Dongles, Phone IDs)
- Automatic date tracking

### Blocker Management
- **Start/End**: Track blocker duration automatically
- **Tickets**: Associate multiple tickets with links
- **Notes**: Add timestamped detailed notes
- **Categories**: Organize different types of blockers

### Reports
- **Daily Summary**: All blockers for current date
- **Detailed Breakdown**: Full ticket and note information
- **Print Optimized**: Clean printing layouts
- **Export Ready**: Structured data for external systems

## Deployment

### Development
```bash
python3 src/run_flask.py
```

### Production
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn --bind 0.0.0.0:5001 src.flask_app:app

# Or using Flask built-in (development only)
python3 src/run_flask.py
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python3", "src/run_flask.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper TypeScript types
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Use TypeScript for frontend development
- Follow existing code patterns
- Update documentation
- Test both CLI and web interfaces

## License

[Add your license here]

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Change port in src/flask_app.py or src/run_flask.py
app.run(port=5002)  # Use different port
```

**TypeScript Compilation Errors**
```bash
npm run clean
npm run build
```

**Data File Issues**
- Check `data/` directory permissions
- Verify JSON file format
- Use test mode for debugging

**Template Not Found**
- Verify `templates/` directory structure
- Check Flask template path configuration

## Support

For issues and questions:
1. Check this documentation
2. Review error logs
3. Test in safe mode
4. Submit issue with reproduction steps

---

**Built with care for efficient end-of-day reporting**