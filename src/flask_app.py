#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Import configuration and core classes
from config.app_config import get_config
from app import JsonHandler, EODTracker

# Initialize Flask app with configuration
config_class = get_config()
app = Flask(__name__, 
           template_folder=str(Path(__file__).parent.parent / 'templates'),
           static_folder=str(Path(__file__).parent.parent / 'static'))
app.config.from_object(config_class)

def get_tracker():
    """Get or create an EODTracker instance for this session"""
    if 'test_mode' not in session:
        session['test_mode'] = False
    
    # Get session info for filename generation
    session_info = session.get('session_info')
    
    return EODTracker(test_mode=session['test_mode'], session_info=session_info)

def check_session_required():
    """Check if session information is required and redirect if missing"""
    # Skip check for session setup and static routes
    from flask import request
    if request.endpoint in ['session_setup', 'static']:
        return None
    
    # Check if we have valid session info
    session_info = session.get('session_info')
    if not session_info:
        flash('Please complete session setup before accessing other features.', 'warning')
        return redirect(url_for('session_setup'))
    
    # Validate required fields - pack_operator is mandatory
    required_fields = ['pack_operator',]
    for field in required_fields:
        if not session_info.get(field) or session_info.get(field).strip() == '':
            flash('Session information is incomplete. Please complete all required fields.', 'warning')
            return redirect(url_for('session_setup'))
    
    return None

@app.route('/')
def dashboard():
    """Main dashboard showing current status and today's summary"""
    # Check if session setup is required
    session_check = check_session_required()
    if session_check:
        return session_check
    
    tracker = get_tracker()
    
    # Get today's data
    today = datetime.now().strftime("%Y-%m-%d")
    today_blockers = [b for b in tracker.js_handler.data["blockers"] if b["start_time"].startswith(today)]

    
    current_blocker = tracker.js_handler.data.get("current_blocker")
    session_info = tracker.js_handler.data.get("session_info")
    
    # Calculate current blocker duration if active
    current_duration = 0
    if current_blocker:
        start_dt = tracker.parse_timestamp(current_blocker["start_time"])
        current_duration = int((datetime.now() - start_dt).total_seconds() / 60)
    
    # Calculate total time
    total_minutes = sum(b["duration_minutes"] for b in today_blockers)
    if current_blocker:
        total_minutes += current_duration
    
    return render_template('dashboard.html', 
                         current_blocker=current_blocker,
                         current_duration=current_duration,
                         today_blockers=today_blockers,
                         session_info=session_info,
                         total_minutes=total_minutes,
                         today=today)

@app.route('/session', methods=['GET', 'POST'])
def session_setup():
    """Session information setup"""
    # Create tracker without operator-specific filename for session setup
    if 'test_mode' not in session:
        session['test_mode'] = False

    
    if request.method == 'POST':
        session_info = {
            "pack_operator": request.form.get('pack_operator', '').strip(),
            "support_operator": request.form.get('support_operator', '').strip(),
            "location": request.form.get('location', '').strip(),
            "pack_number": request.form.get('pack_number', '').strip(),
            "key_used": request.form.get('key_used', '').strip(),
            "glove_number": request.form.get('glove_number', '').strip(),
            "dongle_number": request.form.get('dongle_number', '').strip(),
            "phone_id": request.form.get('phone_id', '').strip(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        # Store session info in Flask session first for filename generation
        session['session_info'] = session_info
        
        # Create tracker with session info and save
        tracker = EODTracker(test_mode=session['test_mode'], session_info=session_info)
        tracker.js_handler.data["session_info"] = session_info
        tracker.js_handler.save_data()
        
        flash('Session information saved successfully!', 'success')
        return redirect(url_for('dashboard'))

    # GET request - show form
    # Try to get existing session info from Flask session or create empty tracker
    existing_session = session.get('session_info')
    tracker = EODTracker(test_mode=session['test_mode'], session_info=existing_session)
    session_info = tracker.js_handler.data.get("session_info", {})
    return render_template('session_setup.html', session_info=session_info)

@app.route('/start_blocker', methods=['POST'])
def start_blocker():
    """Start a new blocker"""
    tracker = get_tracker()
    description = request.form.get('description', '').strip()

    tracker_category = request.form.get('category', '').strip()

    if not description:
        flash('Blocker description cannot be empty.', 'error')
        return redirect(url_for('dashboard'))



    if tracker.js_handler.data.get("current_blocker"):
        flash('A blocker is already active. Please end it first.', 'error')
        return redirect(url_for('dashboard'))
    
    success = tracker.start_blocker(description, category= tracker_category, prompt_for_ticket=False)

    if success:
        flash(f'Started blocker: {description}', 'success')
    else:
        flash('Failed to start blocker.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/end_blocker', methods=['POST'])
def end_blocker():
    """End the current blocker"""
    # Check if session setup is required

    
    tracker = get_tracker()
    
    if tracker.end_current_blocker():
        flash('Blocker ended successfully!', 'success')
    else:
        flash('No active blocker to end.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    """Add a ticket to the current blocker"""
    tracker = get_tracker()
    ticket_number = request.form.get('ticket_number', '').strip()
    ticket_link = request.form.get('ticket_link', '').strip()

    
    if not tracker.js_handler.data.get("current_blocker"):
        flash('No active blocker. Start a blocker first.', 'error')
        return redirect(url_for('dashboard'))
    
    if not ticket_number:
        flash('Ticket number cannot be empty.', 'error')
        return redirect(url_for('dashboard'))
    
    current = tracker.js_handler.data["current_blocker"]
    if "tickets" not in current:
        current["tickets"] = []
    
    ticket_obj = {"number": ticket_number, "link": f"LINK: {ticket_link}" if ticket_link else ""}
    current["tickets"].append(ticket_obj)
    tracker.js_handler.save_data()
    
    flash(f'Ticket {ticket_number} added to current blocker!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_note', methods=['POST'])
def add_note():
    """Add a note to the current blocker"""
    tracker = get_tracker()
    note_content = request.form.get('note_content', '').strip()
    
    if not tracker.js_handler.data.get("current_blocker"):
        flash('No active blocker. Start a blocker first.', 'error')
        return redirect(url_for('dashboard'))
    
    if not note_content:
        flash('Note cannot be empty.', 'error')
        return redirect(url_for('dashboard'))
    
    if "notes" not in tracker.js_handler.data["current_blocker"]:
        tracker.js_handler.data["current_blocker"]["notes"] = []
    
    note = {
        "content": note_content,
        "timestamp": tracker.format_timestamp()
    }
    
    tracker.js_handler.data["current_blocker"]["notes"].append(note)
    tracker.js_handler.save_data()
    
    flash('Note added to current blocker!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/eod_report')
def eod_report():
    """Generate and display EOD report"""
    # Check if session setup is required
    session_check = check_session_required()
    if session_check:
        return session_check
    
    tracker = get_tracker()
    
    today = datetime.now().strftime("%Y-%m-%d")
    blockers_data = tracker.js_handler.data.get("blockers", [])
    
    if not isinstance(blockers_data, list):
        blockers_data = []
    
    today_blockers = []
    for b in blockers_data:
        if b and isinstance(b, dict) and b.get("start_time"):
            if b["start_time"].startswith(today):
                today_blockers.append(b)
    
    session_info = tracker.js_handler.data.get("session_info")
    current_blocker = tracker.js_handler.data.get("current_blocker")
    
    total_minutes = sum(b["duration_minutes"] for b in today_blockers)
    
    # Calculate category stats for EOD report
    category_stats = {}
    for blocker in today_blockers:
        category = blocker.get("category", "other")
        if category not in category_stats:
            category_stats[category] = {"count": 0, "total_minutes": 0}
        category_stats[category]["count"] += 1
        category_stats[category]["total_minutes"] += blocker.get("duration_minutes", 0)
    
    return render_template('eod_report.html',
                         today_blockers=today_blockers,
                         session_info=session_info,
                         current_blocker=current_blocker,
                         total_minutes=total_minutes,
                         today=today,
                         category_stats=category_stats)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear all data"""
    tracker = get_tracker()
    confirm = request.form.get('confirm', '').strip()
    
    if confirm == "YES":
        tracker.js_handler.data = tracker.js_handler.get_default_data()
        tracker.js_handler.save_data()
        flash('All data cleared successfully.', 'success')
    else:
        flash('Clear operation cancelled.', 'info')
    
    return redirect(url_for('dashboard'))

@app.route('/manager')
def manager_dashboard():
    """Manager dashboard with analytics and performance metrics"""
    import glob
    from datetime import date, timedelta
    
    # Get data for the last 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    # Determine base directory for file search
    base_dir = "data/test" if session.get('test_mode', False) else "data/production"
    
    # Collect all blockers from the last week
    all_blockers = []
    daily_stats = {}
    
    for i in range(8):  # Include today
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Find all JSON files for this date using glob pattern
        pattern = os.path.join(base_dir, f"*_eod_data_{date_str}.json")
        matching_files = glob.glob(pattern)
        
        day_blockers = []
        session_info_list = []
        
        # Load data from all matching files for this date
        for file_path in matching_files:
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    file_blockers = file_data.get("blockers", [])
                    file_session = file_data.get("session_info")
                    
                    # Filter blockers for this specific date
                    date_blockers = [b for b in file_blockers if b.get("start_time", "").startswith(date_str)]
                    day_blockers.extend(date_blockers)
                    
                    if file_session:
                        session_info_list.append(file_session)
                        
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        # Extend all blockers with today's findings
        all_blockers.extend(day_blockers)
        
        # Use the first session info found, or None
        session_info = session_info_list[0] if session_info_list else None
        
        # Calculate daily stats
        total_minutes = sum(b.get("duration_minutes", 0) for b in day_blockers)
        daily_stats[date_str] = {
            "date": current_date,
            "blocker_count": len(day_blockers),
            "total_minutes": total_minutes,
            "session_info": session_info,
            "efficiency": max(0, min(100, ((480 - total_minutes) / 480) * 100)) if total_minutes <= 480 else 0,  # Assuming 8-hour shifts
            "operators_count": len(matching_files)  # Number of operators active this day
        }
    
    # Category analytics
    category_analytics = {}
    operator_analytics = {}
    operator_daily_performance = {}
    
    # Process all files again for detailed operator analytics
    for i in range(8):  # Re-scan for detailed analytics
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        pattern = os.path.join(base_dir, f"*_eod_data_{date_str}.json")
        matching_files = glob.glob(pattern)
        
        for file_path in matching_files:
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    file_blockers = file_data.get("blockers", [])
                    file_session = file_data.get("session_info")
                    
                    # Extract operator info from filename
                    filename = os.path.basename(file_path)
                    operator_location = filename.split('_eod_data_')[0]
                    operator_parts = operator_location.split('_')
                    operator_name = operator_parts[0] if operator_parts else "unknown"
                    location = operator_parts[1] if len(operator_parts) > 1 else "unknown"
                    
                    # Filter blockers for this specific date
                    date_blockers = [b for b in file_blockers if b.get("start_time", "").startswith(date_str)]
                    
                    # Initialize operator analytics if not exists
                    if operator_location not in operator_analytics:
                        operator_analytics[operator_location] = {
                            "operator_name": operator_name.replace('-', ' ').title(),
                            "location": location.replace('-', ' ').title(),
                            "total_blockers": 0,
                            "total_minutes": 0,
                            "avg_resolution_time": 0,
                            "efficiency_score": 100,
                            "categories": {},
                            "active_days": 0,
                            "daily_performance": []
                        }
                    
                    # Initialize daily performance tracking
                    if operator_location not in operator_daily_performance:
                        operator_daily_performance[operator_location] = {}
                    
                    # Calculate daily metrics for this operator
                    day_minutes = sum(b.get("duration_minutes", 0) for b in date_blockers)
                    day_blockers_count = len(date_blockers)
                    day_efficiency = max(0, min(100, ((480 - day_minutes) / 480) * 100)) if day_minutes <= 480 else 0
                    
                    # Store daily performance
                    operator_daily_performance[operator_location][date_str] = {
                        "date": current_date,
                        "blockers_count": day_blockers_count,
                        "total_minutes": day_minutes,
                        "efficiency": round(day_efficiency, 1)
                    }
                    
                    # Update operator totals
                    if day_blockers_count > 0:
                        operator_analytics[operator_location]["active_days"] += 1
                    
                    operator_analytics[operator_location]["total_blockers"] += day_blockers_count
                    operator_analytics[operator_location]["total_minutes"] += day_minutes
                    
                    # Track categories for this operator
                    for blocker in date_blockers:
                        category = blocker.get("category", "other")
                        if category not in operator_analytics[operator_location]["categories"]:
                            operator_analytics[operator_location]["categories"][category] = 0
                        operator_analytics[operator_location]["categories"][category] += 1
                        
            except (json.JSONDecodeError, FileNotFoundError):
                continue
    
    # Calculate operator averages and efficiency scores
    for operator_id, analytics in operator_analytics.items():
        if analytics["total_blockers"] > 0:
            analytics["avg_resolution_time"] = round(
                analytics["total_minutes"] / analytics["total_blockers"], 1
            )
        
        # Calculate overall efficiency (average of daily efficiencies)
        daily_perfs = operator_daily_performance.get(operator_id, {})
        if daily_perfs:
            total_efficiency = sum(day["efficiency"] for day in daily_perfs.values())
            analytics["efficiency_score"] = round(total_efficiency / len(daily_perfs), 1)
            
            # Add daily performance list for charts
            analytics["daily_performance"] = [
                daily_perfs.get(f"{(start_date + timedelta(days=j)).strftime('%Y-%m-%d')}", 
                               {"date": start_date + timedelta(days=j), "blockers_count": 0, "total_minutes": 0, "efficiency": 100})
                for j in range(8)
            ]
    
    # Category analytics (existing logic)
    for blocker in all_blockers:
        category = blocker.get("category", "other")
        if category not in category_analytics:
            category_analytics[category] = {"count": 0, "total_minutes": 0, "avg_resolution_time": 0}
        category_analytics[category]["count"] += 1
        category_analytics[category]["total_minutes"] += blocker.get("duration_minutes", 0)
    
    # Calculate category averages
    for category in category_analytics:
        if category_analytics[category]["count"] > 0:
            category_analytics[category]["avg_resolution_time"] = round(
                category_analytics[category]["total_minutes"] / category_analytics[category]["count"], 1
            )
    
    # Get unique operators and total files
    unique_operators = set(operator_analytics.keys())
    total_files_scanned = sum(len(glob.glob(os.path.join(base_dir, f"*_eod_data_{(start_date + timedelta(days=j)).strftime('%Y-%m-%d')}.json"))) for j in range(8))
    
    # Overall metrics
    total_blockers = len(all_blockers)
    total_downtime = sum(b.get("duration_minutes", 0) for b in all_blockers)
    avg_resolution_time = round(total_downtime / total_blockers, 1) if total_blockers > 0 else 0
    
    # Most problematic categories
    top_categories = sorted(category_analytics.items(), 
                          key=lambda x: x[1]["total_minutes"], reverse=True)[:3]
    
    # Filter operators who worked today (or most recent day with data)
    today_str = end_date.strftime("%Y-%m-%d")
    active_today_operators = {}
    
    # Find operators who worked today, or if no one worked today, find the most recent day
    for check_days in range(3):  # Check today and up to 2 days back
        check_date = (end_date - timedelta(days=check_days)).strftime("%Y-%m-%d")
        pattern = os.path.join(base_dir, f"*_eod_data_{check_date}.json")
        matching_files = glob.glob(pattern)
        
        if matching_files:  # Found operators for this day
            for file_path in matching_files:
                filename = os.path.basename(file_path)
                operator_location = filename.split('_eod_data_')[0]
                if operator_location in operator_analytics:
                    active_today_operators[operator_location] = operator_analytics[operator_location]
            break  # Use this day's operators
    
    # If no active operators found, fall back to all operators
    if not active_today_operators:
        active_today_operators = operator_analytics
    
    # Sort active operators by efficiency score for better display
    sorted_operators = sorted(active_today_operators.items(), key=lambda x: x[1]["efficiency_score"], reverse=True)
    
    # Performance trends - overall daily efficiency trend
    daily_trend = []
    for i in range(8):
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_data = daily_stats.get(date_str, {})
        daily_trend.append({
            "date": date_str,
            "efficiency": daily_data.get("efficiency", 100),
            "blockers": daily_data.get("blocker_count", 0),
            "operators": daily_data.get("operators_count", 0)
        })
    
    # Determine which day's operators we're showing
    active_operators_date = end_date.strftime("%Y-%m-%d")
    for check_days in range(3):
        check_date = (end_date - timedelta(days=check_days)).strftime("%Y-%m-%d")
        pattern = os.path.join(base_dir, f"*_eod_data_{check_date}.json")
        if glob.glob(pattern):
            active_operators_date = check_date
            break
    
    return render_template('manager_dashboard.html',
                         daily_stats=daily_stats,
                         category_analytics=category_analytics,
                         operator_analytics=dict(sorted_operators),
                         daily_trend=daily_trend,
                         total_blockers=total_blockers,
                         total_downtime=total_downtime,
                         avg_resolution_time=avg_resolution_time,
                         top_categories=top_categories,
                         date_range={"start": start_date, "end": end_date},
                         unique_operators=list(unique_operators),
                         total_files_scanned=total_files_scanned,
                         active_operators_date=active_operators_date,
                         showing_today_operators=active_operators_date == today_str)

@app.route('/toggle_test_mode')
def toggle_test_mode():
    """Toggle test mode"""
    session['test_mode'] = not session.get('test_mode', False)
    mode = "enabled" if session['test_mode'] else "disabled"
    flash(f'Test mode {mode}', 'info')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], 
           host=app.config['HOST'], 
           port=app.config['PORT'])