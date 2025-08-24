#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Import the existing classes from app.py
from app import JsonHandler, EODTracker

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

def get_tracker():
    """Get or create an EODTracker instance for this session"""
    if 'test_mode' not in session:
        session['test_mode'] = False
    return EODTracker(test_mode=session['test_mode'])

@app.route('/')
def dashboard():
    """Main dashboard showing current status and today's summary"""
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
    tracker = get_tracker()
    
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
    
    if not description:
        flash('Blocker description cannot be empty.', 'error')
        return redirect(url_for('dashboard'))
    
    if tracker.js_handler.data.get("current_blocker"):
        flash('A blocker is already active. Please end it first.', 'error')
        return redirect(url_for('dashboard'))
    
    success = tracker.start_blocker(description)
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

@app.route('/toggle_test_mode')
def toggle_test_mode():
    """Toggle test mode"""
    session['test_mode'] = not session.get('test_mode', False)
    mode = "enabled" if session['test_mode'] else "disabled"
    flash(f'Test mode {mode}', 'info')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)