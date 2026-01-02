"""Migration Tool Tab - User data migration visualization."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import os
import datetime

from app.utils.scrollable_frame import ScrollableFrame
from app.modules.file_loader import FileLoader
from app.modules.theme import Theme
from app.modules.ui_components import Card, StatCard
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style as mpl_style

# Use a modern matplotlib style
try:
    mpl_style.use('seaborn-v0_8-darkgrid')
except:
    try:
        mpl_style.use('seaborn-darkgrid')
    except:
        mpl_style.use('default')


class MigrationToolTab:
    """Tab for migration tool functionality."""
    
    def __init__(self, parent, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.theme_colors = theme_manager.get_current_theme()
        self.frame = ttk.Frame(parent, padding=20)
        
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
        
        # Load default files if they exist
        self.load_default_files()
    
    def update_theme(self, theme_colors: dict):
        """Update theme colors for all components."""
        self.theme_colors = theme_colors
        
        # Update text widget colors
        if hasattr(self, 'stats_text'):
            self.stats_text.config(bg=theme_colors['BG_PRIMARY'], fg=theme_colors['TEXT_PRIMARY'])
        if hasattr(self, 'detail_text'):
            self.detail_text.config(bg=theme_colors['BG_PRIMARY'], fg=theme_colors['TEXT_PRIMARY'])
        
        # Update status label
        if hasattr(self, 'status_label'):
            current_text = self.status_label.cget('text')
            if '✓' in current_text:
                self.status_label.config(foreground=theme_colors['SUCCESS'])
            elif '✗' in current_text:
                self.status_label.config(foreground=theme_colors['ERROR'])
            else:
                self.status_label.config(foreground=theme_colors['TEXT_SECONDARY'])
        
        # Recreate charts with new theme if data is loaded
        if self.sync_report:
            for widget in self.stats_charts_frame.winfo_children():
                widget.destroy()
            self.create_stats_charts()
        
        if self.selected_user and 'clerkId' in self.selected_user:
            for widget in self.detail_charts_frame.winfo_children():
                widget.destroy()
            self.create_user_charts(self.selected_user)
    
    def create_widgets(self):
        """Create all UI widgets for the migration tool tab."""
        # File Input Section - Modern card design
        file_card = Card(self.frame, title="Load Migration Data", padding=20, theme_colors=self.theme_colors)
        file_card.pack(fill="x", pady=(0, 20))
        
        # File inputs in a grid
        file_grid = ttk.Frame(file_card.content_frame)
        file_grid.pack(fill="x")
        
        # Linked users
        row1 = ttk.Frame(file_grid)
        row1.pack(fill="x", pady=8)
        ttk.Label(row1, text="Linked Users", width=18, anchor='w').pack(side='left', padx=(0, 10))
        self.linked_users_entry = ttk.Entry(row1, width=60)
        self.linked_users_entry.pack(side='left', fill="x", expand=True, padx=(0, 10))
        ttk.Button(row1, text="Browse", command=self.browse_linked_users, style='Secondary.TButton').pack(side='left')
        
        # Unmatched users
        row2 = ttk.Frame(file_grid)
        row2.pack(fill="x", pady=8)
        ttk.Label(row2, text="Unmatched Users", width=18, anchor='w').pack(side='left', padx=(0, 10))
        self.unmatched_users_entry = ttk.Entry(row2, width=60)
        self.unmatched_users_entry.pack(side='left', fill="x", expand=True, padx=(0, 10))
        ttk.Button(row2, text="Browse", command=self.browse_unmatched_users, style='Secondary.TButton').pack(side='left')
        
        # Sync report
        row3 = ttk.Frame(file_grid)
        row3.pack(fill="x", pady=8)
        ttk.Label(row3, text="Sync Report", width=18, anchor='w').pack(side='left', padx=(0, 10))
        self.sync_report_entry = ttk.Entry(row3, width=60)
        self.sync_report_entry.pack(side='left', fill="x", expand=True, padx=(0, 10))
        ttk.Button(row3, text="Browse", command=self.browse_sync_report, style='Secondary.TButton').pack(side='left')
        
        # Load button and status
        button_row = ttk.Frame(file_card.content_frame)
        button_row.pack(fill="x", pady=(15, 0))
        ttk.Button(button_row, text="Load Data", command=self.load_data, style='Primary.TButton').pack(side='left')
        self.status_label = ttk.Label(button_row, text="No data loaded", style='Subheading.TLabel')
        self.status_label.pack(side='left', padx=(20, 0))
        
        # Stats Cards Row - Full width horizontal (4 cards, no scrollbar)
        self.stats_cards_frame = ttk.Frame(self.frame)
        self.stats_cards_frame.pack(fill="x", pady=(0, 20))
        
        # Main content area - Two columns (Browser left, Details right)
        content_paned = ttk.PanedWindow(self.frame, orient="horizontal")
        content_paned.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left: User Browser
        browser_container = ttk.Frame(content_paned)
        content_paned.add(browser_container, weight=1)
        self.create_user_browser(browser_container)
        
        # Right: User Details
        detail_container = ttk.Frame(content_paned)
        content_paned.add(detail_container, weight=1)
        self.create_detail_view(detail_container)
        
        # Summary & Charts Section - Full width at bottom
        summary_card = Card(self.frame, title="Summary & Visualizations", padding=20, theme_colors=self.theme_colors)
        summary_card.pack(fill="both", expand=True)
        
        # Create summary and charts in this card
        summary_container = ttk.Frame(summary_card.content_frame)
        summary_container.pack(fill="both", expand=True)
        
        # Summary text (left side)
        summary_left = ttk.Frame(summary_container)
        summary_left.pack(side='left', fill="both", expand=True, padx=(0, 15))
        
        text_frame = ttk.Frame(summary_left)
        text_frame.pack(fill="both", expand=True)
        
        self.stats_text = tk.Text(
            text_frame,
            wrap="word",
            width=50,
            height=20,
            font=("SF Mono", 11),
            bg=self.theme_colors['BG_PRIMARY'],
            fg=self.theme_colors['TEXT_PRIMARY'],
            relief='flat',
            padx=15,
            pady=15,
            borderwidth=0
        )
        stats_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scrollbar.pack(side="right", fill="y")
        
        # Charts (right side)
        charts_frame = ttk.Frame(summary_container)
        charts_frame.pack(side='left', fill="both", expand=True)
        self.stats_charts_frame = charts_frame
    
    def create_user_browser(self, parent):
        """Create user browser with modern design."""
        browser_card = Card(parent, title="Browse Users", padding=15, theme_colors=self.theme_colors)
        browser_card.pack(fill="both", expand=True)
        
        # Search and filter controls
        controls_frame = ttk.Frame(browser_card.content_frame)
        controls_frame.pack(fill="x", pady=(0, 15))
        
        # Search
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(search_frame, text="Search", width=10).pack(side='left', padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filter
        filter_frame = ttk.Frame(controls_frame)
        filter_frame.pack(fill="x")
        ttk.Label(filter_frame, text="Filter", width=10).pack(side='left', padx=(0, 10))
        self.filter_var = tk.StringVar(value="all")
        filter_btn_frame = ttk.Frame(filter_frame)
        filter_btn_frame.pack(side='left', fill="x", expand=True)
        ttk.Radiobutton(filter_btn_frame, text="All", variable=self.filter_var, value="all", command=self.on_filter).pack(side='left', padx=(0, 15))
        ttk.Radiobutton(filter_btn_frame, text="Matched", variable=self.filter_var, value="matched", command=self.on_filter).pack(side='left', padx=(0, 15))
        ttk.Radiobutton(filter_btn_frame, text="Unmatched", variable=self.filter_var, value="unmatched", command=self.on_filter).pack(side='left')
        
        # User list
        list_container = ttk.Frame(browser_card.content_frame)
        list_container.pack(fill="both", expand=True)
        
        # Treeview
        tree_frame = ttk.Frame(list_container)
        tree_frame.pack(fill="both", expand=True)
        
        self.user_tree = ttk.Treeview(
            tree_frame,
            columns=("email", "name", "points"),
            show="headings",
            height=35
        )
        self.user_tree.heading("#0", text="User ID")
        self.user_tree.heading("email", text="Email")
        self.user_tree.heading("name", text="Name")
        self.user_tree.heading("points", text="Points")
        self.user_tree.column("#0", width=250, anchor='w')
        self.user_tree.column("email", width=300, anchor='w')
        self.user_tree.column("name", width=220, anchor='w')
        self.user_tree.column("points", width=100, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.user_tree.xview)
        self.user_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.user_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)
    
    def create_detail_view(self, parent):
        """Create detailed user view."""
        detail_card = Card(parent, title="User Details", padding=15, theme_colors=self.theme_colors)
        detail_card.pack(fill="both", expand=True)
        
        scroll_frame = ScrollableFrame(detail_card.content_frame)
        scroll_frame.pack(fill="both", expand=True)
        
        # User info card
        info_card = Card(scroll_frame.scrollable_frame, title="User Information", padding=15, theme_colors=self.theme_colors)
        info_card.pack(fill="x", pady=(0, 15))
        
        text_frame = ttk.Frame(info_card.content_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.detail_text = tk.Text(
            text_frame,
            wrap="word",
            width=60,
            height=25,
            font=("SF Mono", 11),
            bg=self.theme_colors['BG_PRIMARY'],
            fg=self.theme_colors['TEXT_PRIMARY'],
            relief='flat',
            padx=15,
            pady=15,
            borderwidth=0
        )
        detail_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side="left", fill="both", expand=True)
        detail_scrollbar.pack(side="right", fill="y")
        
        # Charts card
        charts_card = Card(scroll_frame.scrollable_frame, title="Points History", padding=15, theme_colors=self.theme_colors)
        charts_card.pack(fill="both", expand=True)
        self.detail_charts_frame = charts_card.content_frame
    
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
            for file_path, entry in [
                (output_dir / "linked_users.jsonl", self.linked_users_entry),
                (output_dir / "unmatched_users.jsonl", self.unmatched_users_entry),
                (output_dir / "sync_report.json", self.sync_report_entry)
            ]:
                if file_path.exists():
                    entry.insert(0, str(file_path))
                    if "linked" in str(file_path):
                        self.linked_users_path = str(file_path)
                    elif "unmatched" in str(file_path):
                        self.unmatched_users_path = str(file_path)
                    else:
                        self.sync_report_path = str(file_path)
    
    def load_data(self):
        """Load data from selected files."""
        try:
            self.linked_users = []
            if self.linked_users_path and os.path.exists(self.linked_users_path):
                self.linked_users = FileLoader.load_jsonl(self.linked_users_path)
            
            self.unmatched_users = []
            if self.unmatched_users_path and os.path.exists(self.unmatched_users_path):
                self.unmatched_users = FileLoader.load_jsonl(self.unmatched_users_path)
            
            self.sync_report = None
            if self.sync_report_path and os.path.exists(self.sync_report_path):
                self.sync_report = FileLoader.load_json(self.sync_report_path)
            
            self.update_stats_cards()
            self.update_summary_and_charts()
            self.update_user_browser()
            self.status_label.config(
                text=f"✓ Loaded: {len(self.linked_users)} linked, {len(self.unmatched_users)} unmatched",
                foreground=self.theme_colors['SUCCESS']
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.status_label.config(text="✗ Error loading data", foreground=self.theme_colors['ERROR'])
    
    def update_stats_cards(self):
        """Update stats cards row."""
        # Clear existing cards
        for widget in self.stats_cards_frame.winfo_children():
            widget.destroy()
        
        if self.sync_report:
            stats = self.sync_report
            # Create 4 stat cards in a horizontal row
            StatCard(
                self.stats_cards_frame,
                "Total Users",
                f"{stats.get('total_clerk_users', 0):,}",
                self.theme_colors['PRIMARY'],
                theme_colors=self.theme_colors
            ).pack(side='left', padx=(0, 15), fill='x', expand=True)
            
            StatCard(
                self.stats_cards_frame,
                "Matched",
                f"{stats.get('matched_users', 0):,}",
                self.theme_colors['SUCCESS'],
                theme_colors=self.theme_colors
            ).pack(side='left', padx=(0, 15), fill='x', expand=True)
            
            StatCard(
                self.stats_cards_frame,
                "Unmatched",
                f"{stats.get('clerk_only', 0) + stats.get('convex_only', 0):,}",
                self.theme_colors['WARNING'],
                theme_colors=self.theme_colors
            ).pack(side='left', padx=(0, 15), fill='x', expand=True)
            
            StatCard(
                self.stats_cards_frame,
                "Match Rate",
                f"{stats.get('match_rate_percent', 0):.1f}%",
                self.theme_colors['INFO'],
                theme_colors=self.theme_colors
            ).pack(side='left', fill='x', expand=True)
    
    def update_summary_and_charts(self):
        """Update summary text and charts."""
        # Update text
        self.stats_text.delete(1.0, tk.END)
        if self.sync_report:
            stats = self.sync_report
            text = f"""SYNC REPORT SUMMARY
{'='*70}

Total Clerk Users: {stats.get('total_clerk_users', 0):,}
Total Convex Users: {stats.get('total_convex_users', 0):,}
Matched Users: {stats.get('matched_users', 0):,}
Clerk Only: {stats.get('clerk_only', 0):,}
Convex Only: {stats.get('convex_only', 0):,}
Match Rate: {stats.get('match_rate_percent', 0):.2f}%

Points Records: {stats.get('total_points_records', 0):,}
Referral Records: {stats.get('total_referral_records', 0):,}
Mini-Game Records: {stats.get('total_mini_game_records', 0):,}
"""
            self.stats_text.insert(1.0, text)
        
        # Clear and update charts
        for widget in self.stats_charts_frame.winfo_children():
            widget.destroy()
        
        if self.sync_report:
            self.create_stats_charts()
    
    def create_stats_charts(self):
        """Create statistics charts."""
        if not self.sync_report:
            return
        
        stats = self.sync_report
        fig = Figure(figsize=(10, 5), dpi=100, facecolor=self.theme_colors['BG_PRIMARY'])
        
        # Pie chart
        ax1 = fig.add_subplot(121, facecolor=self.theme_colors['BG_PRIMARY'])
        matched = stats.get('matched_users', 0)
        unmatched = stats.get('clerk_only', 0) + stats.get('convex_only', 0)
        if matched + unmatched > 0:
            colors = [self.theme_colors['SUCCESS'], self.theme_colors['WARNING']]
            ax1.pie([matched, unmatched], labels=['Matched', 'Unmatched'], autopct='%1.1f%%', startangle=90, colors=colors)
            ax1.set_title('User Match Status', fontsize=13, fontweight='bold', color=self.theme_colors['TEXT_PRIMARY'], pad=15)
        
        # Bar chart
        ax2 = fig.add_subplot(122, facecolor=self.theme_colors['BG_PRIMARY'])
        clerk_total = stats.get('total_clerk_users', 0)
        convex_total = stats.get('total_convex_users', 0)
        bars = ax2.bar(['Clerk', 'Convex'], [clerk_total, convex_total], color=[self.theme_colors['PRIMARY'], self.theme_colors['INFO']])
        ax2.set_title('Users by Source', fontsize=13, fontweight='bold', color=self.theme_colors['TEXT_PRIMARY'], pad=15)
        ax2.set_ylabel('Count', color=self.theme_colors['TEXT_PRIMARY'])
        ax2.tick_params(colors=self.theme_colors['TEXT_PRIMARY'])
        ax2.spines['bottom'].set_color(self.theme_colors['BORDER'])
        ax2.spines['top'].set_color(self.theme_colors['BORDER'])
        ax2.spines['right'].set_color(self.theme_colors['BORDER'])
        ax2.spines['left'].set_color(self.theme_colors['BORDER'])
        
        fig.tight_layout(pad=3.0)
        
        canvas = FigureCanvasTkAgg(fig, self.stats_charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_user_browser(self):
        """Update user browser with loaded data."""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        all_users = []
        for user in self.linked_users:
            all_users.append(("matched", user))
        for user in self.unmatched_users:
            all_users.append(("unmatched", user))
        
        self.filtered_users = all_users
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and filter to user list."""
        search_term = self.search_entry.get().lower()
        filter_type = self.filter_var.get()
        
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        for user_type, user in self.filtered_users:
            if filter_type == "matched" and user_type != "matched":
                continue
            if filter_type == "unmatched" and user_type != "unmatched":
                continue
            
            if search_term:
                user_id = user.get('clerkId') or user.get('id', '')
                email = ""
                name = ""
                
                if user_type == "matched":
                    email = user.get('clerkData', {}).get('primary_email_address', '') or user.get('convexProfile', {}).get('email', '')
                    name = user.get('convexProfile', {}).get('name', '') or f"{user.get('clerkData', {}).get('first_name', '')} {user.get('clerkData', {}).get('last_name', '')}"
                else:
                    email = user.get('data', {}).get('primary_email_address', '')
                    name = f"{user.get('data', {}).get('first_name', '')} {user.get('data', {}).get('last_name', '')}"
                
                search_text = f"{user_id} {email} {name}".lower()
                if search_term not in search_text:
                    continue
            
            if user_type == "matched":
                user_id = user.get('clerkId', '')
                email = user.get('clerkData', {}).get('primary_email_address', '') or user.get('convexProfile', {}).get('email', '')
                name = user.get('convexProfile', {}).get('name', '') or f"{user.get('clerkData', {}).get('first_name', '')} {user.get('clerkData', {}).get('last_name', '')}"
                points = user.get('totalPointsEarned', 0)
                self.user_tree.insert("", "end", text=user_id[:45], values=(email[:50], name[:40], f"{points:,.0f}"), tags=(user_type,))
            else:
                user_id = user.get('id', '')
                email = user.get('data', {}).get('primary_email_address', '')
                name = f"{user.get('data', {}).get('first_name', '')} {user.get('data', {}).get('last_name', '')}"
                self.user_tree.insert("", "end", text=user_id[:45], values=(email[:50], name[:40], "N/A"), tags=(user_type,))
        
        self.user_tree.tag_configure("matched", foreground=self.theme_colors['SUCCESS'])
        self.user_tree.tag_configure("unmatched", foreground=self.theme_colors['WARNING'])
    
    def on_search(self, event=None):
        self.apply_filters()
    
    def on_filter(self):
        self.apply_filters()
    
    def on_user_select(self, event):
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        user_id = self.user_tree.item(item, "text")
        tags = self.user_tree.item(item, "tags")
        
        if tags and len(tags) > 0:
            user_type = tags[0]
            if user_type == "matched":
                for user in self.linked_users:
                    if user.get('clerkId', '') == user_id:
                        self.selected_user = user
                        self.update_detail_view()
                        break
            else:
                for user in self.unmatched_users:
                    if user.get('id', '') == user_id:
                        self.selected_user = user
                        self.update_detail_view()
                        break
    
    def update_detail_view(self):
        self.detail_text.delete(1.0, tk.END)
        
        for widget in self.detail_charts_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_user:
            self.detail_text.insert(1.0, "No user selected")
            return
        
        if 'clerkId' in self.selected_user:
            self.display_matched_user_details()
        else:
            self.display_unmatched_user_details()
    
    def display_matched_user_details(self):
        user = self.selected_user
        text = f"""USER DETAILS - MATCHED USER
{'='*70}

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
        text += f"  Total Points Earned: {user.get('totalPointsEarned', 0):,.0f}\n"
        text += f"  Total Referrals Made: {user.get('totalReferralsMade', 0)}\n"
        text += f"  Points History Entries: {len(user.get('pointsHistory', []))}\n"
        text += f"  Referrals Made: {len(user.get('referralsMade', []))}\n"
        
        referred_by = user.get('referredBy')
        if referred_by:
            text += f"  Referred By: {referred_by.get('referrerId', 'N/A')}\n"
        
        self.detail_text.insert(1.0, text)
        self.create_user_charts(user)
    
    def display_unmatched_user_details(self):
        user = self.selected_user
        text = f"""USER DETAILS - UNMATCHED USER
{'='*70}

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
        if not user or 'clerkId' not in user:
            return
        
        points_history = user.get('pointsHistory', [])
        if points_history:
            fig = Figure(figsize=(10, 5), dpi=100, facecolor=self.theme_colors['BG_PRIMARY'])
            ax = fig.add_subplot(111, facecolor=self.theme_colors['BG_PRIMARY'])
            
            dates = [entry.get('createdAt', entry.get('_creationTime', 0)) for entry in points_history]
            points = [entry.get('pointsEarned', 0) for entry in points_history]
            
            if dates and dates[0] > 1000000000000:
                dates = [datetime.datetime.fromtimestamp(d/1000) for d in dates]
            
            ax.plot(dates, points, marker='o', linewidth=2.5, color=self.theme_colors['PRIMARY'], markersize=8)
            ax.set_title('Points History Timeline', fontsize=14, fontweight='bold', color=self.theme_colors['TEXT_PRIMARY'], pad=15)
            ax.set_xlabel('Date', color=self.theme_colors['TEXT_PRIMARY'], fontsize=11)
            ax.set_ylabel('Points Earned', color=self.theme_colors['TEXT_PRIMARY'], fontsize=11)
            ax.grid(True, alpha=0.2, color=self.theme_colors['BORDER'])
            ax.tick_params(colors=self.theme_colors['TEXT_PRIMARY'])
            ax.spines['bottom'].set_color(self.theme_colors['BORDER'])
            ax.spines['top'].set_color(self.theme_colors['BORDER'])
            ax.spines['right'].set_color(self.theme_colors['BORDER'])
            ax.spines['left'].set_color(self.theme_colors['BORDER'])
            fig.autofmt_xdate()
            
            canvas = FigureCanvasTkAgg(fig, self.detail_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
