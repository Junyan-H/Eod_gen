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
    
    # Generate operator string for filename from session data
    operators = 'NA'
    if 'session_info' in session and session['session_info']:
        pack_op = session['session_info'].get('pack_operator', '').replace(' ', '-')
        support_op = session['session_info'].get('support_operator', '').replace(' ', '-')
        if pack_op and support_op:
            operators = f"{pack_op}_{support_op}"
        elif pack_op:
            operators = pack_op
        elif support_op:
            operators = support_op
    
    return EODTracker(test_mode=session['test_mode'], operators=operators)

def check_session_required():
    """Check if session information is required and redirect if missing"""
    # Skip check for session setup and static routes
    from flask import request
    if request.endpoint in ['session_setup', 'static']:
        return None
    
    # Check if we have valid session info
    session_info = session.get('session_info')
    if not session_info or not session_info.get('pack_operator'):
        flash('Please complete session setup before accessing other features.', 'warning')
        return redirect(url_for('session_setup'))

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
    tracker = EODTracker(test_mode=session['test_mode'], operators='NA')
    
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
            "date": datetime.now().strftime("%Y-%m-%d"),
            "initialized_at": tracker.format_timestamp()
        }
        
        tracker.js_handler.data["session_info"] = session_info
        tracker.js_handler.save_data()
        
        # Store session info in Flask session for filename generation
        session['session_info'] = session_info
        
        flash('Session information saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - show form
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
    
    return render_template('eod_report.html',
                         today_blockers=today_blockers,
                         session_info=session_info,
                         current_blocker=current_blocker,
                         total_minutes=total_minutes,
                         today=today)

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
    tracker = get_tracker()
    
    # Get data for the last 7 days
    from datetime import date, timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    # Collect all blockers from the last week
    all_blockers = []
    daily_stats = {}
    
    for i in range(8):  # Include today
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Try to load data for this date
        try:
            date_filename = f"eod_data_{date_str}.json"
            temp_handler = JsonHandler(date_filename)
            day_blockers = temp_handler.data.get("blockers", [])
            session_info = temp_handler.data.get("session_info")
            
            # Filter blockers for this specific date
            day_blockers = [b for b in day_blockers if b.get("start_time", "").startswith(date_str)]
            all_blockers.extend(day_blockers)
            
            # Calculate daily stats
            total_minutes = sum(b.get("duration_minutes", 0) for b in day_blockers)
            daily_stats[date_str] = {
                "date": current_date,
                "blocker_count": len(day_blockers),
                "total_minutes": total_minutes,
                "session_info": session_info,
                "efficiency": max(0, min(100, ((480 - total_minutes) / 480) * 100)) if total_minutes <= 480 else 0  # Assuming 8-hour shifts
            }
        except:
            daily_stats[date_str] = {
                "date": current_date,
                "blocker_count": 0,
                "total_minutes": 0,
                "session_info": None,
                "efficiency": 100
            }
    
    # Category analytics
    category_analytics = {}
    
    for blocker in all_blockers:
        # Category stats
        category = blocker.get("category", "other")
        if category not in category_analytics:
            category_analytics[category] = {"count": 0, "total_minutes": 0, "avg_resolution_time": 0}
        category_analytics[category]["count"] += 1
        category_analytics[category]["total_minutes"] += blocker.get("duration_minutes", 0)
    
    # Calculate averages
    for category in category_analytics:
        if category_analytics[category]["count"] > 0:
            category_analytics[category]["avg_resolution_time"] = round(
                category_analytics[category]["total_minutes"] / category_analytics[category]["count"], 1
            )
    
    # Overall metrics
    total_blockers = len(all_blockers)
    total_downtime = sum(b.get("duration_minutes", 0) for b in all_blockers)
    avg_resolution_time = round(total_downtime / total_blockers, 1) if total_blockers > 0 else 0
    
    # Most problematic categories
    top_categories = sorted(category_analytics.items(), 
                          key=lambda x: x[1]["total_minutes"], reverse=True)[:3]
    
    return render_template('manager_dashboard.html',
                         daily_stats=daily_stats,
                         category_analytics=category_analytics,
                         total_blockers=total_blockers,
                         total_downtime=total_downtime,
                         avg_resolution_time=avg_resolution_time,
                         top_categories=top_categories,
                         date_range={"start": start_date, "end": end_date})

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