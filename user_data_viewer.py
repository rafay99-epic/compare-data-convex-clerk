#!/usr/bin/env python3
"""
User Data Viewer GUI Application
Visualizes user migration data with charts, browsing, and detailed views.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd


class ScrollableFrame(ttk.Frame):
    """A scrollable frame widget using Canvas and Scrollbar."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrollbar
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)  # Linux/Unix
        self.canvas.bind("<Button-5>", self._on_mousewheel)  # Linux/Unix
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        # Windows and macOS
        if hasattr(event, 'delta') and event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # Linux/Unix
        elif hasattr(event, 'num'):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        return "break"


class UserDataViewer:
    """Main application class for User Data Viewer GUI."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("User Data Viewer - Migration Tool")
        self.root.geometry("1400x900")
        
        # Data storage
        self.linked_users: List[Dict[str, Any]] = []
        self.unmatched_users: List[Dict[str, Any]] = []
        self.sync_report: Optional[Dict[str, Any]] = None
        
        # File paths
        self.linked_users_path = ""
        self.unmatched_users_path = ""
        self.sync_report_path = ""
        
        # Selected user
        self.selected_user: Optional[Dict[str, Any]] = None
        
        # Build UI
        self.create_widgets()
        
        # Try to load default files if they exist
        self.load_default_files()
    
    def create_widgets(self):
        """Create all UI widgets."""
        # File Input Panel (Top)
        file_frame = ttk.LabelFrame(self.root, text="File Input", padding=10)
        file_frame.pack(fill="x", padx=5, pady=5)
        
        # Linked users file
        ttk.Label(file_frame, text="Linked Users (JSONL):").grid(row=0, column=0, sticky="w", padx=5)
        self.linked_users_entry = ttk.Entry(file_frame, width=60)
        self.linked_users_entry.grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_linked_users).grid(row=0, column=2, padx=5)
        
        # Unmatched users file
        ttk.Label(file_frame, text="Unmatched Users (JSONL):").grid(row=1, column=0, sticky="w", padx=5)
        self.unmatched_users_entry = ttk.Entry(file_frame, width=60)
        self.unmatched_users_entry.grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_unmatched_users).grid(row=1, column=2, padx=5)
        
        # Sync report file
        ttk.Label(file_frame, text="Sync Report (JSON):").grid(row=2, column=0, sticky="w", padx=5)
        self.sync_report_entry = ttk.Entry(file_frame, width=60)
        self.sync_report_entry.grid(row=2, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_sync_report).grid(row=2, column=2, padx=5)
        
        # Load button
        ttk.Button(file_frame, text="Load Data", command=self.load_data).grid(row=3, column=1, pady=10)
        
        # Status label
        self.status_label = ttk.Label(file_frame, text="No data loaded", foreground="gray")
        self.status_label.grid(row=3, column=2, padx=5)
        
        # Main content area
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left pane: Statistics
        stats_frame = ttk.LabelFrame(main_paned, text="Statistics", padding=10)
        main_paned.add(stats_frame, weight=1)
        self.create_stats_panel(stats_frame)
        
        # Middle pane: User Browser
        browser_frame = ttk.LabelFrame(main_paned, text="User Browser", padding=10)
        main_paned.add(browser_frame, weight=1)
        self.create_user_browser(browser_frame)
        
        # Right pane: User Detail View
        detail_frame = ttk.LabelFrame(main_paned, text="User Details", padding=10)
        main_paned.add(detail_frame, weight=1)
        self.create_detail_view(detail_frame)
    
    def create_stats_panel(self, parent):
        """Create statistics panel with charts."""
        # Scrollable frame for stats
        scroll_frame = ScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True)
        
        self.stats_content = scroll_frame.scrollable_frame
        
        # Stats text area
        self.stats_text = tk.Text(scroll_frame.scrollable_frame, wrap="word", width=40, height=15)
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Charts frame
        self.stats_charts_frame = ttk.Frame(scroll_frame.scrollable_frame)
        self.stats_charts_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_user_browser(self, parent):
        """Create user browser with search and filter."""
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, value="all", command=self.on_filter).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="Matched", variable=self.filter_var, value="matched", command=self.on_filter).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="Unmatched", variable=self.filter_var, value="unmatched", command=self.on_filter).pack(side="left", padx=5)
        
        # User list with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Treeview with scrollbars
        self.user_tree = ttk.Treeview(list_frame, columns=("email", "name", "points"), show="tree headings", height=20)
        self.user_tree.heading("#0", text="User ID")
        self.user_tree.heading("email", text="Email")
        self.user_tree.heading("name", text="Name")
        self.user_tree.heading("points", text="Points")
        self.user_tree.column("#0", width=200)
        self.user_tree.column("email", width=200)
        self.user_tree.column("name", width=150)
        self.user_tree.column("points", width=100)
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.user_tree.xview)
        self.user_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.user_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)
    
    def create_detail_view(self, parent):
        """Create detailed user view with scrollable content."""
        # Create scrollable frame
        scroll_frame = ScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True)
        
        self.detail_content = scroll_frame.scrollable_frame
        
        # User info text area with scrollbar
        info_frame = ttk.LabelFrame(scroll_frame.scrollable_frame, text="User Information", padding=10)
        info_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.detail_text = tk.Text(text_frame, wrap="word", width=50, height=15)
        detail_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side="left", fill="both", expand=True)
        detail_scrollbar.pack(side="right", fill="y")
        
        # Charts frame
        self.detail_charts_frame = ttk.LabelFrame(scroll_frame.scrollable_frame, text="Charts", padding=10)
        self.detail_charts_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def browse_linked_users(self):
        """Browse for linked users JSONL file."""
        filename = filedialog.askopenfilename(
            title="Select Linked Users File",
            filetypes=[("JSONL files", "*.jsonl"), ("All files", "*.*")]
        )
        if filename:
            self.linked_users_entry.delete(0, tk.END)
            self.linked_users_entry.insert(0, filename)
            self.linked_users_path = filename
    
    def browse_unmatched_users(self):
        """Browse for unmatched users JSONL file."""
        filename = filedialog.askopenfilename(
            title="Select Unmatched Users File",
            filetypes=[("JSONL files", "*.jsonl"), ("All files", "*.*")]
        )
        if filename:
            self.unmatched_users_entry.delete(0, tk.END)
            self.unmatched_users_entry.insert(0, filename)
            self.unmatched_users_path = filename
    
    def browse_sync_report(self):
        """Browse for sync report JSON file."""
        filename = filedialog.askopenfilename(
            title="Select Sync Report File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.sync_report_entry.delete(0, tk.END)
            self.sync_report_entry.insert(0, filename)
            self.sync_report_path = filename
    
    def load_default_files(self):
        """Try to load default files from output directory."""
        output_dir = Path("output")
        if output_dir.exists():
            linked_file = output_dir / "linked_users.jsonl"
            unmatched_file = output_dir / "unmatched_users.jsonl"
            report_file = output_dir / "sync_report.json"
            
            if linked_file.exists():
                self.linked_users_entry.insert(0, str(linked_file))
                self.linked_users_path = str(linked_file)
            
            if unmatched_file.exists():
                self.unmatched_users_entry.insert(0, str(unmatched_file))
                self.unmatched_users_path = str(unmatched_file)
            
            if report_file.exists():
                self.sync_report_entry.insert(0, str(report_file))
                self.sync_report_path = str(report_file)
    
    def load_data(self):
        """Load data from selected files."""
        try:
            # Load linked users
            self.linked_users = []
            if self.linked_users_path and os.path.exists(self.linked_users_path):
                with open(self.linked_users_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.linked_users.append(json.loads(line))
            
            # Load unmatched users
            self.unmatched_users = []
            if self.unmatched_users_path and os.path.exists(self.unmatched_users_path):
                with open(self.unmatched_users_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.unmatched_users.append(json.loads(line))
            
            # Load sync report
            self.sync_report = None
            if self.sync_report_path and os.path.exists(self.sync_report_path):
                with open(self.sync_report_path, 'r', encoding='utf-8') as f:
                    self.sync_report = json.load(f)
            
            # Update UI
            self.update_stats_panel()
            self.update_user_browser()
            self.status_label.config(text=f"Loaded: {len(self.linked_users)} linked, {len(self.unmatched_users)} unmatched", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.status_label.config(text="Error loading data", foreground="red")
    
    def update_stats_panel(self):
        """Update statistics panel with data."""
        # Clear previous content
        self.stats_text.delete(1.0, tk.END)
        
        if self.sync_report:
            stats = self.sync_report
            text = f"""SYNC REPORT SUMMARY
{'='*50}

Total Clerk Users: {stats.get('total_clerk_users', 0)}
Total Convex Users: {stats.get('total_convex_users', 0)}
Matched Users: {stats.get('matched_users', 0)}
Clerk Only: {stats.get('clerk_only', 0)}
Convex Only: {stats.get('convex_only', 0)}
Match Rate: {stats.get('match_rate_percent', 0):.2f}%

Points Records: {stats.get('total_points_records', 0)}
Referral Records: {stats.get('total_referral_records', 0)}
Mini-Game Records: {stats.get('total_mini_game_records', 0)}
"""
            self.stats_text.insert(1.0, text)
        
        # Clear previous charts
        for widget in self.stats_charts_frame.winfo_children():
            widget.destroy()
        
        # Create charts
        if self.sync_report:
            self.create_stats_charts()
    
    def create_stats_charts(self):
        """Create statistics charts."""
        if not self.sync_report:
            return
        
        stats = self.sync_report
        
        # Create figure for charts
        fig = Figure(figsize=(6, 4), dpi=100)
        
        # Pie chart: Matched vs Unmatched
        ax1 = fig.add_subplot(121)
        matched = stats.get('matched_users', 0)
        unmatched = stats.get('clerk_only', 0) + stats.get('convex_only', 0)
        if matched + unmatched > 0:
            ax1.pie([matched, unmatched], labels=['Matched', 'Unmatched'], autopct='%1.1f%%', startangle=90)
            ax1.set_title('User Match Status')
        
        # Bar chart: Total users by source
        ax2 = fig.add_subplot(122)
        clerk_total = stats.get('total_clerk_users', 0)
        convex_total = stats.get('total_convex_users', 0)
        ax2.bar(['Clerk', 'Convex'], [clerk_total, convex_total])
        ax2.set_title('Users by Source')
        ax2.set_ylabel('Count')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.stats_charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_user_browser(self):
        """Update user browser with loaded data."""
        # Clear existing items
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Combine all users
        all_users = []
        for user in self.linked_users:
            all_users.append(("matched", user))
        for user in self.unmatched_users:
            all_users.append(("unmatched", user))
        
        # Filter and add to treeview
        self.filtered_users = all_users
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and filter to user list."""
        # Get search term
        search_term = self.search_entry.get().lower()
        
        # Get filter
        filter_type = self.filter_var.get()
        
        # Clear existing items
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Filter and add users
        for user_type, user in self.filtered_users:
            # Apply type filter
            if filter_type == "matched" and user_type != "matched":
                continue
            if filter_type == "unmatched" and user_type != "unmatched":
                continue
            
            # Apply search filter
            if search_term:
                user_id = user.get('clerkId') or user.get('id', '')
                email = ""
                name = ""
                points = 0
                
                if user_type == "matched":
                    email = user.get('clerkData', {}).get('primary_email_address', '') or user.get('convexProfile', {}).get('email', '')
                    name = user.get('convexProfile', {}).get('name', '') or f"{user.get('clerkData', {}).get('first_name', '')} {user.get('clerkData', {}).get('last_name', '')}"
                    points = user.get('totalPointsEarned', 0)
                else:
                    email = user.get('data', {}).get('primary_email_address', '')
                    name = f"{user.get('data', {}).get('first_name', '')} {user.get('data', {}).get('last_name', '')}"
                
                search_text = f"{user_id} {email} {name}".lower()
                if search_term not in search_text:
                    continue
            
            # Add to treeview
            if user_type == "matched":
                user_id = user.get('clerkId', '')
                email = user.get('clerkData', {}).get('primary_email_address', '') or user.get('convexProfile', {}).get('email', '')
                name = user.get('convexProfile', {}).get('name', '') or f"{user.get('clerkData', {}).get('first_name', '')} {user.get('clerkData', {}).get('last_name', '')}"
                points = user.get('totalPointsEarned', 0)
                item = self.user_tree.insert("", "end", text=user_id[:30], values=(email[:40], name[:30], points), tags=(user_type,))
                self.user_tree.item(item, values=(email[:40], name[:30], points))
            else:
                user_id = user.get('id', '')
                email = user.get('data', {}).get('primary_email_address', '')
                name = f"{user.get('data', {}).get('first_name', '')} {user.get('data', {}).get('last_name', '')}"
                item = self.user_tree.insert("", "end", text=user_id[:30], values=(email[:40], name[:30], "N/A"), tags=(user_type,))
        
        # Tag colors
        self.user_tree.tag_configure("matched", foreground="green")
        self.user_tree.tag_configure("unmatched", foreground="orange")
    
    def on_search(self, event=None):
        """Handle search input."""
        self.apply_filters()
    
    def on_filter(self):
        """Handle filter change."""
        self.apply_filters()
    
    def on_user_select(self, event):
        """Handle user selection in treeview."""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        user_id = self.user_tree.item(item, "text")
        tags = self.user_tree.item(item, "tags")
        
        if tags and len(tags) > 0:
            user_type = tags[0]
            if user_type == "matched":
                # Find matched user
                for user in self.linked_users:
                    if user.get('clerkId', '') == user_id:
                        self.selected_user = user
                        self.update_detail_view()
                        break
            else:
                # Find unmatched user
                for user in self.unmatched_users:
                    if user.get('id', '') == user_id:
                        self.selected_user = user
                        self.update_detail_view()
                        break
    
    def update_detail_view(self):
        """Update detailed user view."""
        # Clear previous content
        self.detail_text.delete(1.0, tk.END)
        
        # Clear charts
        for widget in self.detail_charts_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_user:
            self.detail_text.insert(1.0, "No user selected")
            return
        
        # Determine if matched or unmatched
        if 'clerkId' in self.selected_user:
            # Matched user
            self.display_matched_user_details()
        else:
            # Unmatched user
            self.display_unmatched_user_details()
    
    def display_matched_user_details(self):
        """Display details for a matched user."""
        user = self.selected_user
        
        # Build text content
        text = f"""USER DETAILS - MATCHED USER
{'='*60}

CLERK ID: {user.get('clerkId', 'N/A')}
CONVEX ID: {user.get('convexId', 'N/A')}

CLERK DATA:
"""
        clerk_data = user.get('clerkData', {})
        if clerk_data:
            text += f"  First Name: {clerk_data.get('first_name', 'N/A')}\n"
            text += f"  Last Name: {clerk_data.get('last_name', 'N/A')}\n"
            text += f"  Username: {clerk_data.get('username', 'N/A')}\n"
            text += f"  Email: {clerk_data.get('primary_email_address', 'N/A')}\n"
            text += f"  Phone: {clerk_data.get('primary_phone_number', 'N/A')}\n"
        
        convex_profile = user.get('convexProfile', {})
        if convex_profile:
            text += f"\nCONVEX PROFILE:\n"
            text += f"  Name: {convex_profile.get('name', 'N/A')}\n"
            text += f"  Email: {convex_profile.get('email', 'N/A')}\n"
            text += f"  Country: {convex_profile.get('country', 'N/A')}\n"
            text += f"  Affiliate Level: {convex_profile.get('affiliateLevel', 'N/A')}\n"
            text += f"  Points Breakdown:\n"
            points_breakdown = convex_profile.get('pointsBreakdown', {})
            for key, value in points_breakdown.items():
                text += f"    {key}: {value}\n"
            text += f"  Referral Code: {convex_profile.get('referralCode', 'N/A')}\n"
        
        text += f"\nSTATISTICS:\n"
        text += f"  Total Points Earned: {user.get('totalPointsEarned', 0)}\n"
        text += f"  Total Referrals Made: {user.get('totalReferralsMade', 0)}\n"
        text += f"  Points History Entries: {len(user.get('pointsHistory', []))}\n"
        text += f"  Referrals Made: {len(user.get('referralsMade', []))}\n"
        
        referred_by = user.get('referredBy')
        if referred_by:
            text += f"  Referred By: {referred_by.get('referrerId', 'N/A')}\n"
        
        self.detail_text.insert(1.0, text)
        
        # Create charts
        self.create_user_charts(user)
    
    def display_unmatched_user_details(self):
        """Display details for an unmatched user."""
        user = self.selected_user
        
        text = f"""USER DETAILS - UNMATCHED USER
{'='*60}

SOURCE: {user.get('source', 'N/A')}
USER ID: {user.get('id', 'N/A')}
REASON: {user.get('reason', 'N/A')}

USER DATA:
"""
        user_data = user.get('data', {})
        if user_data:
            text += f"  First Name: {user_data.get('first_name', 'N/A')}\n"
            text += f"  Last Name: {user_data.get('last_name', 'N/A')}\n"
            text += f"  Username: {user_data.get('username', 'N/A')}\n"
            text += f"  Email: {user_data.get('primary_email_address', 'N/A')}\n"
            text += f"  Phone: {user_data.get('primary_phone_number', 'N/A')}\n"
        
        self.detail_text.insert(1.0, text)
    
    def create_user_charts(self, user):
        """Create charts for user details."""
        if not user or 'clerkId' not in user:
            return
        
        # Points history chart
        points_history = user.get('pointsHistory', [])
        if points_history:
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Extract data
            dates = [entry.get('createdAt', entry.get('_creationTime', 0)) for entry in points_history]
            points = [entry.get('pointsEarned', 0) for entry in points_history]
            
            # Convert timestamps to readable dates if needed
            if dates and dates[0] > 1000000000000:  # Likely milliseconds
                import datetime
                dates = [datetime.datetime.fromtimestamp(d/1000) for d in dates]
            
            ax.plot(dates, points, marker='o')
            ax.set_title('Points History Timeline')
            ax.set_xlabel('Date')
            ax.set_ylabel('Points Earned')
            ax.grid(True)
            fig.autofmt_xdate()
            
            canvas = FigureCanvasTkAgg(fig, self.detail_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = UserDataViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
