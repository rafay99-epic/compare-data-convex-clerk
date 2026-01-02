# Data Explorer - Migration Tool & Data Visualization

A comprehensive desktop application for data migration analysis and general-purpose data exploration. Built with Python and tkinter, featuring interactive charts, data visualization, and a professional UI.

## Features

### Migration Tool Tab
- **User Data Comparison**: Compare and link user data from Clerk (CSV) and Convex (JSONL)
- **Statistics Visualization**: View sync statistics with pie charts and bar charts
- **User Browser**: Search and filter through users with proper scrolling support
- **Detailed User Views**: View complete user profiles, points history, and referral data
- **Charts**: Points history timeline charts and statistics visualizations

### Data Explorer Tab
- **Multi-Format Support**: Load CSV, JSON, and JSONL files
- **Data Overview**: Comprehensive statistics including shape, data types, null counts, numeric stats, and categorical value counts
- **Interactive Charts**: Multiple chart types with both Matplotlib and Plotly support:
  - Line charts
  - Bar charts
  - Pie/Donut charts
  - Histograms
  - Scatter plots
  - Correlation heatmaps
- **Data Table Viewer**: Scrollable table view with search functionality
- **Chart Library Selection**: Choose between Matplotlib (embedded) and Plotly (interactive browser-based)

## Installation

### Prerequisites
- Python 3.7 or higher
- macOS (for building .app bundle) or any platform (for running from source)

### Setup from Source

1. **Clone or navigate to the repository:**
   ```bash
   cd compare-data-convex-clerk
   ```

2. **Set up virtual environment:**
   ```bash
   ./setup_env.sh
   ```
   
   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   source venv/bin/activate  # If not already activated
   python -m app.main
   # Or: python app/main.py
   ```

## Building macOS Application Bundle

### Option 1: Using PyInstaller

```bash
./build/build_pyinstaller.sh
```

The application bundle will be created in `dist/Data Explorer.app`

### Option 2: Using py2app

```bash
./build/build_py2app.sh
```

The application bundle will be created in `dist/Data Explorer.app`

### Post-Build Steps

1. **Move to Applications:**
   ```bash
   cp -r "dist/Data Explorer.app" /Applications/
   ```

2. **Code Signing (Optional):**
   For distribution, you may want to code sign the application:
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "dist/Data Explorer.app"
   ```

3. **Create DMG (Optional):**
   ```bash
   hdiutil create -volname "Data Explorer" -srcfolder "dist/Data Explorer.app" -ov -format UDZO "Data Explorer.dmg"
   ```

## Usage

### Migration Tool

1. **Load Data Files:**
   - Click "Browse" to select:
     - Linked Users JSONL file (output/linked_users.jsonl)
     - Unmatched Users JSONL file (output/unmatched_users.jsonl)
     - Sync Report JSON file (output/sync_report.json)
   - Click "Load Data" to parse and display

2. **View Statistics:**
   - Statistics panel shows sync report summary
   - Charts display user match status and distribution

3. **Browse Users:**
   - Use search box to filter by email, ID, or name
   - Filter by: All, Matched, or Unmatched
   - Click on a user to view details
   - Scrollable list supports mouse wheel and scrollbar

4. **View User Details:**
   - Select a user to see complete information
   - View points history timeline chart
   - See referrals and related data

### Data Explorer

1. **Load Data:**
   - Click "Browse" to select CSV, JSON, or JSONL file
   - Click "Load Data" to parse and analyze

2. **View Overview:**
   - Go to "Overview" tab to see data statistics
   - View shape, columns, data types, null counts
   - See numeric statistics and categorical value counts

3. **Generate Charts:**
   - Go to "Charts" tab
   - Select chart type (Line, Bar, Pie, Histogram, Scatter, Heatmap)
   - Choose library (Matplotlib for embedded, Plotly for interactive)
   - Select columns for X and Y axes
   - Click "Generate Chart"

4. **View Data Table:**
   - Go to "Data Table" tab
   - Scroll through data with mouse wheel or scrollbars
   - Use search to filter data

## Project Structure

```
compare-data-convex-clerk/
├── app/
│   ├── main.py                 # Main entry point
│   ├── main_window.py          # Main window with tabs
│   ├── modules/
│   │   ├── file_loader.py      # File loading utilities
│   │   ├── chart_engine.py     # Chart generation (matplotlib + plotly)
│   │   ├── data_processor.py   # Data processing utilities
│   │   └── ui_components.py    # Reusable UI components
│   ├── tabs/
│   │   ├── migration_tool/
│   │   │   └── migration_tab.py
│   │   └── data_explorer/
│   │       └── explorer_tab.py
│   └── utils/
│       └── scrollable_frame.py # ScrollableFrame component
├── build/
│   ├── build_pyinstaller.sh    # PyInstaller build script
│   └── build_py2app.sh         # py2app build script
├── output/                     # Data files (generated by compare_users.py)
├── compare_users.py            # User data comparison script
├── requirements.txt            # Python dependencies
├── setup.py                    # py2app setup file
└── README.md                   # This file
```

## Dependencies

- `matplotlib>=3.7.0` - Static charts and visualizations
- `pandas>=2.0.0` - Data manipulation and analysis
- `plotly>=5.17.0` - Interactive charts with animations
- `kaleido>=0.2.1` - Plotly static export
- `numpy>=1.24.0` - Numerical operations
- `pyinstaller>=6.0` - Building .app bundles (optional)
- `py2app>=0.28` - Alternative build method (optional)

## Scrolling Support

All scrollable components use proper scrollbar binding:
- **Treeview**: Vertical and horizontal scrollbars
- **Text Widgets**: Vertical scrollbars
- **ScrollableFrame**: Canvas-based scrolling with mouse wheel support
- Tested with large datasets (2000+ users, 1000+ data rows)

## Notes

- The application automatically tries to load default files from the `output/` directory
- Plotly charts open in your default web browser for full interactivity
- Matplotlib charts are embedded directly in the application
- Large datasets are automatically limited in the table view (first 1000 rows) for performance

## License

See LICENSE file for details.
