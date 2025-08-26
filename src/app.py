#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta
import sys
from typing import Dict, List, Optional, Any, Union

'''
json handler
'''
class JsonHandler:
    def __init__(self, filename: Optional[str] = None, operators: str = 'NA') -> None:
        if filename is None:
            # Create date-specific filename
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"{operators}_eod_data_{today}.json"
        self.filename = filename
        self.data = self.load_data()

    '''
    loads the json file
    '''
    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return self.get_default_data()
        return self.get_default_data()

    '''
    parser
    '''
    def get_default_data(self) -> Dict[str, Any]:
        return {
            "blockers": [],
            "current_blocker": None,
            "last_updated": None,
            "session_info": None
        }
    '''
    writes to file
    '''
    def save_data(self) -> None:
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
'''
status tracker
'''
class StatusTracker:
    def __init__(self, test_mode: bool = False) -> None:
        if test_mode:
            print("TEST MODE ACTIVATED")
            self.js_handler = JsonHandler("data/test/test_data.json")
        else:
            self.js_handler = JsonHandler()

        '''
        Generates a status report:
        three status types: break, collecting, blocker
        '''


'''
eod runner
'''
class EODTracker:
    def __init__(self, test_mode: bool = False, operators: str = 'NA') -> None:
        self.operators = operators
        if test_mode:
            print("TEST MODE ACTIVATED")
            self.js_handler = JsonHandler("data/test/test_data.json", operators)
        else:
            self.js_handler = JsonHandler(operators=operators)

        self.check_recovery()
    
    def _format_ticket_list(self, tickets: List[Union[str, Dict[str, str]]]) -> List[str]:
        """Helper method to format ticket display consistently."""
        return [t["number"] if isinstance(t, dict) else str(t) for t in tickets]

    '''
    initialization prompt for session info :pack info etc
    '''
    def prompt_session_info(self) -> None:
        print("\n" + "="*60)
        print("SESSION INITIALIZATION")
        print("="*60)
        print("Please provide the following information (if none put NA):")

        pack_operator = input("Pack Operator: ").strip()
        support_operator = input("Support Operator: ").strip()
        location = input("Location: ").strip()
        pack_number = input("Pack Numbers: ").strip()
        key_used = input("Key Used: ").strip()
        glove_number = input("Glove #: ").strip()
        dongle_number = input("Dongle #: ").strip()
        phone_id = input("Phone ID: ").strip()

        session_info = {
            "pack_operator": pack_operator,
            "support_operator": support_operator,
            "location": location,
            "pack_number": pack_number,
            "key_used": key_used,
            "glove_number": glove_number,
            "dongle_number": dongle_number,
            "phone_id": phone_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "initialized_at": self.format_timestamp()
        }
        
        self.js_handler.data["session_info"] = session_info
        self.js_handler.save_data()
        
        print("\nSession information saved!")


    '''
    add ticket numbers to current blocker
    '''
    def add_ticket(self) -> None:
        if not self.js_handler.data.get("current_blocker"):
            print("No active blocker. Start a blocker first to add tickets.")
            return
        
        current = self.js_handler.data["current_blocker"]
        
        # Initialize tickets list for current blocker if it doesn't exist
        if "tickets" not in current:
            current["tickets"] = []
        
        # Show existing tickets if any
        if current["tickets"]:
            ticket_list = self._format_ticket_list(current["tickets"])
            print(f"Current tickets: {', '.join(ticket_list)}")
        
        ticket = input("Enter ticket number: ").strip()
        if ticket:

            # ticket link
            ticket_link ="LINK :" +  input("Enter ticket link: ").strip()
            if ticket_link:
                # Add ticket object to current blocker's tickets
                ticket_obj = {"number": ticket, "link": ticket_link}
                current["tickets"].append(ticket_obj)

                self.js_handler.save_data()
                print(f"Ticket {ticket} added to current blocker!")
                ticket_list = self._format_ticket_list(current["tickets"])
                print(f"All tickets for this blocker: {', '.join(ticket_list)}")

            else:
                print("Ticket link cannot be empty.")
        else:
            print("Ticket number cannot be empty.")


    '''
    add notes to current blocker
    '''
    def add_note(self) -> None:
        if not self.js_handler.data.get("current_blocker"):
            print("No active blocker. Start a blocker first to add notes.")
            return
        
        print("\n" + "="*50)
        print("ADD NOTE TO CURRENT BLOCKER")
        print("="*50)
        current = self.js_handler.data["current_blocker"]
        print(f"Current blocker: {current['description']}")
        print("Enter your note (press Enter twice to finish):")
        
        lines = []
        while True:
            line = input()
            if line == "" and len(lines) > 0:
                break
            lines.append(line)
        
        if not lines or all(line.strip() == "" for line in lines):
            print("Note cannot be empty. No note added.")
            return
        
        note_content = "\n".join(lines).strip()
        
        # Add note to current blocker
        if "notes" not in self.js_handler.data["current_blocker"]:
            self.js_handler.data["current_blocker"]["notes"] = []
        
        note = {
            "content": note_content,
            "timestamp": self.format_timestamp()
        }
        
        self.js_handler.data["current_blocker"]["notes"].append(note)
        self.js_handler.save_data()
        
        print(f"\nNote added to current blocker at {note['timestamp']}")
        print(f"Preview: {note_content[:50]}{'...' if len(note_content) > 50 else ''}")

    '''
    recovery
    '''
    def check_recovery(self) -> None:
        # Check for session initialization first
        if not self.js_handler.data.get("session_info"):
            # Skip session info prompt for web interface
            pass
        else:
            session = self.js_handler.data["session_info"]
            today = datetime.now().strftime("%Y-%m-%d")
            if session.get("date") != today:
                print(f"New day detected. Previous session was {session.get('date')}")
                # Skip session info prompt for web interface
        
        # Check for blocker recovery
        if self.js_handler.data.get("current_blocker"):
            print(f"Recovered session with active blocker: '{self.js_handler.data['current_blocker']['description']}'")
            print(f"   Started at: {self.js_handler.data['current_blocker']['start_time']}")


    '''
    timestamps
    '''
    def format_timestamp(self, dt: Optional[datetime] = None) -> str:
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def parse_timestamp(self, ts_string: str) -> datetime:
        return datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S")



    '''
    blocker report
    '''
    def start_blocker(self, description: str, category: str = "other", prompt_for_ticket: bool = True) -> bool:
        if self.js_handler.data.get("current_blocker"):
            print("A blocker is already active. Please end it first.")
            return False
        
        # Create blocker first
        current_blocker = {
            "description": description,
            "category": category,
            "start_time": self.format_timestamp(),
            "tickets": []
        }
        self.js_handler.data["current_blocker"] = current_blocker
        self.js_handler.data["last_updated"] = self.format_timestamp()
        self.js_handler.save_data()
        
        print(f"Started '{category}' blocker: '{description}' at {current_blocker['start_time']}")
        
        # Ask if they want to add a ticket number (only in CLI mode)
        if prompt_for_ticket:
            ticket_response = input("Do you want to add a ticket number for this blocker? (y/n): ").strip().lower()
            if ticket_response in ['y', 'yes']:
                self.add_ticket()
        return True

    '''
    resolving blockers
    '''
    def end_current_blocker(self) -> bool:
        current = self.js_handler.data.get("current_blocker")
        if not current:
            print("No active blocker to end.")
            return False
        
        end_time = self.format_timestamp()
        start_dt = self.parse_timestamp(current["start_time"])
        end_dt = self.parse_timestamp(end_time)
        duration = end_dt - start_dt
        
        completed_blocker = {
            "description": current["description"],
            "category": current.get("category", "other"),
            "start_time": current["start_time"],
            "end_time": end_time,
            "duration_minutes": int(duration.total_seconds() / 60),
            "tickets": current.get("tickets", []),
            "notes": current.get("notes", [])
        }
        
        self.js_handler.data["blockers"].append(completed_blocker)
        self.js_handler.data["current_blocker"] = None
        self.js_handler.data["last_updated"] = self.format_timestamp()
        self.js_handler.save_data()
        
        hours = completed_blocker["duration_minutes"] // 60
        minutes = completed_blocker["duration_minutes"] % 60
        
        print(f"Ended blocker: '{current['description']}'")
        print(f"   Duration: {hours}h {minutes}m ({completed_blocker['duration_minutes']} minutes)")
        return True

    '''
    summary view of todays blocker
    '''
    def view_today_summary(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        today_blockers = [b for b in self.js_handler.data["blockers"] if b["start_time"].startswith(today)]
        
        print(f"\nToday's Summary ({today})")
        print("=" * 40)
        
        if not today_blockers and not self.js_handler.data.get("current_blocker"):
            print("No blockers recorded today.")
            return
        
        total_minutes = 0
        
        for i, blocker in enumerate(today_blockers, 1):
            hours = blocker["duration_minutes"] // 60
            minutes = blocker["duration_minutes"] % 60
            print(f"{i}. {blocker['description']}")
            print(f"   {blocker['start_time']} → {blocker['end_time']} ({hours}h {minutes}m)")
            
            # Show tickets if any
            tickets = blocker.get("tickets", [])
            if tickets:
                ticket_list = self._format_ticket_list(tickets)
                print(f"   Tickets: {', '.join(ticket_list)}")
            
            # Show notes if any
            notes = blocker.get("notes", [])
            if notes:
                print(f"   Notes ({len(notes)}):")
                for j, note in enumerate(notes, 1):
                    note_preview = note["content"][:60] + "..." if len(note["content"]) > 60 else note["content"]
                    print(f"      {j}. {note_preview} ({note['timestamp']})")
            
            total_minutes += blocker["duration_minutes"]
        
        if self.js_handler.data.get("current_blocker"):
            current = self.js_handler.data["current_blocker"]
            start_dt = self.parse_timestamp(current["start_time"])
            current_duration = datetime.now() - start_dt
            current_minutes = int(current_duration.total_seconds() / 60)
            
            print(f"= ACTIVE: {current['description']}")
            print(f"   Started: {current['start_time']} (running {current_minutes} minutes)")
            # Show tickets if any
            tickets = current.get("tickets", [])
            if tickets:
                ticket_list = self._format_ticket_list(tickets)
                print(f"   Tickets: {', '.join(ticket_list)}")
            
            # Show notes if any
            notes = current.get("notes", [])
            if notes:
                print(f"   Notes ({len(notes)}):")
                for j, note in enumerate(notes, 1):
                    note_preview = note["content"][:60] + "..." if len(note["content"]) > 60 else note["content"]
                    print(f"      {j}. {note_preview} ({note['timestamp']})")
            
            total_minutes += current_minutes
        
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60
        
        print(f"\nTotal blocker time today: {total_hours}h {remaining_minutes}m ({total_minutes} minutes)")


    '''
    end of day generator
    '''
    def generate_eod_report(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Safely get blockers and filter out null/invalid entries
        blockers_data = self.js_handler.data.get("blockers", [])
        if not isinstance(blockers_data, list):
            blockers_data = []
        
        today_blockers = []
        for b in blockers_data:
            if b and isinstance(b, dict) and b.get("start_time"):
                if b["start_time"].startswith(today):
                    today_blockers.append(b)
        
        print(f"\nEnd of Day Report - {today}")
        print("=" * 50)
        
        # Display session info at the start
        session_info = self.js_handler.data.get("session_info")
        if session_info:
            print("\nSession Information:")
            print(f"  Pack Number: {session_info.get('pack_number', 'N/A')}")
            print(f"  Key Used: {session_info.get('key_used', 'N/A')}")
            print(f"  Glove #: {session_info.get('glove_number', 'N/A')}")
            print(f"  Dongle #: {session_info.get('dongle_number', 'N/A')}")
            print(f"  Phone ID: {session_info.get('phone_id', 'N/A')}")
            print(f"  Session Date: {session_info.get('date', 'N/A')}")
            print()
        
        if not today_blockers:
            print("No blockers encountered today!")
            return
        
        total_minutes = sum(b["duration_minutes"] for b in today_blockers)
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60
        
        print(f"Blockers encountered: {len(today_blockers)}")
        print(f"Total time blocked: {total_hours}h {remaining_minutes}m")
        print("\nDetailed breakdown:")
        
        for i, blocker in enumerate(today_blockers, 1):
            hours = blocker["duration_minutes"] // 60
            minutes = blocker["duration_minutes"] % 60
            print(f"  {i}. {blocker['description']}")
            print(f"     Time: {blocker['start_time']} → {blocker['end_time']}")
            print(f"     Duration: {hours}h {minutes}m")
            
            # Show tickets if any
            tickets = blocker.get("tickets", [])
            if tickets:
                ticket_list = []
                for t in tickets:
                    if isinstance(t, dict):
                        ticket_list.append(f"{t['number']} ({t.get('link', 'no link')})")
                    else:
                        ticket_list.append(str(t))
                print(f"     Tickets: {', '.join(ticket_list)}")
            
            # Show notes if any
            notes = blocker.get("notes", [])
            if notes:
                print(f"     Notes ({len(notes)}):")
                for j, note in enumerate(notes, 1):
                    # Show timestamp first, then note content
                    print(f"       {j}. [{note['timestamp']}] {note['content']}")
            
            print()  # Add blank line between blockers for readability
        
        if self.js_handler.data.get("current_blocker"):
            print(f"\nWarning: Active blocker still running: '{self.js_handler.data['current_blocker']['description']}'")
    '''
    reset
    '''
    def clear_all_data(self) -> None:
        confirm = input("Are you sure you want to clear ALL data? This cannot be undone. (type 'YES' to confirm): ")
        if confirm == "YES":
            self.js_handler.data = self.js_handler.get_default_data()
            self.js_handler.save_data()
            print("All data cleared successfully.")
        else:
            print("Clear operation cancelled.")



    '''
    menue interface
    '''
    def show_menu(self) -> None:
        print("\n" + "="*50)
        print("EOD GENERATOR - End of Day Report Tool")
        print("="*50)
        print("1. Start new blocker")
        print("2. End current blocker")
        print("3. View today's summary")
        print("4. Generate EOD report")
        print("5. Clear all data")
        print("6. Exit")
        
        # Show notes and tickets options only if there's an active blocker
        if self.js_handler.data.get("current_blocker"):
            print("7. Add note to current blocker")
            print("8. Add ticket to current blocker")
        
        print("-" * 50)
    
    def run(self) -> None:
        print("EOD Generator Started")
        print(f"Data file: {self.js_handler.filename}")
        
        while True:
            self.show_menu()
            max_choice = 8 if self.js_handler.data.get("current_blocker") else 6
            choice = input(f"Select an option (1-{max_choice}): ").strip()
            
            if choice == "1":
                if self.js_handler.data.get("current_blocker"):
                    print("A blocker is already active:")
                    current = self.js_handler.data["current_blocker"]
                    print(f"   '{current['description']}' started at {current['start_time']}")
                    print("   Please end it first before starting a new one.")
                else:
                    description = input("Enter blocker description: ").strip()
                    if description:
                        print("\nSelect blocker category:")
                        print("1. Software")
                        print("2. Connectivity")
                        print("3. Hardware")
                        print("4. Other")
                        
                        category_choice = input("Enter category (1-4): ").strip()
                        categories = {"1": "software", "2": "connectivity", "3": "hardware", "4": "other"}
                        category = categories.get(category_choice, "other")
                        
                        self.start_blocker(description, category)
                    else:
                        print("Description cannot be empty.")
            
            elif choice == "2":
                self.end_current_blocker()
            
            elif choice == "3":
                self.view_today_summary()
            
            elif choice == "4":
                self.generate_eod_report()
            
            elif choice == "5":
                self.clear_all_data()
            
            elif choice == "6":
                if self.js_handler.data.get("current_blocker"):
                    print("Warning: You have an active blocker. It will be preserved for next session.")
                print("Goodbye! Your data has been saved.")
                break
            
            elif choice == "7" and self.js_handler.data.get("current_blocker"):
                self.add_note()
            
            elif choice == "8" and self.js_handler.data.get("current_blocker"):
                self.add_ticket()
            
            else:
                max_choice = 8 if self.js_handler.data.get("current_blocker") else 6
                print(f"Invalid choice. Please select 1-{max_choice}.")

if __name__ == "__main__":
    try:
        test_input = input('test mode? (y/n): ').strip().lower()
        test_mode = test_input == 'y'
        
        tracker = EODTracker(test_mode=test_mode)
        tracker.run()
    except KeyboardInterrupt:
        print("Session interrupted. Your data has been saved.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)




