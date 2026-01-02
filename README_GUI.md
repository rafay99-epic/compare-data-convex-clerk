# User Data Viewer GUI

A desktop GUI application for visualizing user migration data with charts, browsing, and detailed views.

## Features

- **File Input**: Load JSONL files (linked_users.jsonl, unmatched_users.jsonl) and JSON files (sync_report.json)
- **Statistics Panel**: View sync statistics with interactive charts (pie charts, bar charts)
- **User Browser**: Search and filter through users with proper scrolling support for large datasets
- **User Detail View**: View detailed user information, points history charts, and referral data
- **Proper Scrolling**: All scrollable components use proper scrollbar binding for smooth scrolling with large datasets

## Setup

1. Set up the virtual environment:
   ```bash
   ./setup_env.sh
   ```

   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   source venv/bin/activate  # If not already activated
   python user_data_viewer.py
   ```

## Usage

1. **Load Data Files**:
   - Click "Browse" buttons to select:
     - Linked Users JSONL file (output/linked_users.jsonl)
     - Unmatched Users JSONL file (output/unmatched_users.jsonl)
     - Sync Report JSON file (output/sync_report.json)
   - Click "Load Data" to parse and display the data

2. **View Statistics**:
   - Statistics panel shows sync report summary
   - Charts display user match status and distribution

3. **Browse Users**:
   - Use the search box to filter users by email, ID, or name
   - Use filter radio buttons to show All, Matched, or Unmatched users
   - Click on a user in the list to view details
   - **Scrolling**: The user list supports smooth scrolling with mouse wheel and scrollbar

4. **View User Details**:
   - Select a user from the browser to see detailed information
   - View points history timeline chart
   - See all user data, referrals, and related information
   - **Scrolling**: Detail view supports scrolling for long content

## Scrolling Features

All scrollable components are properly configured:
- **User Browser List**: Uses `ttk.Treeview` with both vertical and horizontal scrollbars
- **Statistics Panel**: Uses `ScrollableFrame` with Canvas + Scrollbar
- **User Detail View**: Uses `ScrollableFrame` and `Text` widget with scrollbars
- **Mouse Wheel Support**: Mouse wheel scrolling works on all scrollable components
- **Keyboard Navigation**: Arrow keys and Page Up/Down work in Treeview

## Requirements

- Python 3.7+
- matplotlib >= 3.7.0
- pandas >= 2.0.0
- tkinter (usually included with Python)

## Notes

- The GUI automatically tries to load default files from the `output/` directory on startup
- All scrolling is tested and works with large datasets (2000+ users)
- Charts are generated using matplotlib and embedded in the GUI
