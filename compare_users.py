#!/usr/bin/env python3
"""
User Data Migration and Comparison Tool
Compares Clerk user data (CSV) with Convex user data (JSONL) and generates
comprehensive merged user profiles with all associated history.
"""

import json
import csv
import os
from collections import defaultdict
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys


class UserDataComparer:
    """Main class for comparing and merging user data from Clerk and Convex."""
    
    def __init__(self, clerk_csv_path: str, convex_snapshot_dir: str, output_dir: str = "output"):
        self.clerk_csv_path = clerk_csv_path
        self.convex_snapshot_dir = Path(convex_snapshot_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.clerk_users: Dict[str, Dict[str, Any]] = {}
        self.convex_users: Dict[str, Dict[str, Any]] = {}
        self.points_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.referral_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.referred_by: Dict[str, Optional[Dict[str, Any]]] = {}
        self.mini_game_progress: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "total_clerk_users": 0,
            "total_convex_users": 0,
            "matched_users": 0,
            "clerk_only": 0,
            "convex_only": 0,
            "total_points_records": 0,
            "total_referral_records": 0,
            "total_mini_game_records": 0,
        }
    
    def load_clerk_data(self):
        """Load Clerk user data from CSV file."""
        print("Loading Clerk user data...")
        try:
            with open(self.clerk_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user_id = row.get('id', '').strip()
                    if user_id:
                        # Convert empty strings to None for consistency
                        cleaned_row = {k: (v.strip() if v.strip() else None) for k, v in row.items()}
                        self.clerk_users[user_id] = cleaned_row
                        self.stats["total_clerk_users"] += 1
        except Exception as e:
            print(f"Error loading Clerk data: {e}")
            sys.exit(1)
        print(f"Loaded {self.stats['total_clerk_users']} Clerk users")
    
    def load_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load and parse a JSONL file, handling empty lines and malformed JSON."""
        records = []
        if not file_path.exists():
            return records
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Skipping malformed JSON on line {line_num} of {file_path.name}: {e}")
                        continue
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        
        return records
    
    def load_convex_users(self):
        """Load Convex user data from JSONL file."""
        print("Loading Convex user data...")
        users_file = self.convex_snapshot_dir / "users" / "documents.jsonl"
        records = self.load_jsonl_file(users_file)
        
        for record in records:
            user_id = record.get('userId', '').strip()
            if user_id:
                self.convex_users[user_id] = record
                self.stats["total_convex_users"] += 1
        print(f"Loaded {self.stats['total_convex_users']} Convex users")
    
    def load_points_history(self):
        """Load points history and index by userId."""
        print("Loading points history...")
        points_file = self.convex_snapshot_dir / "pointsHistory" / "documents.jsonl"
        records = self.load_jsonl_file(points_file)
        
        for record in records:
            user_id = record.get('userId', '').strip()
            if user_id:
                self.points_history[user_id].append(record)
                self.stats["total_points_records"] += 1
        
        print(f"Loaded {self.stats['total_points_records']} points history records for {len(self.points_history)} users")
    
    def load_referral_history(self):
        """Load referral history and index by referrerId and referredId."""
        print("Loading referral history...")
        referral_file = self.convex_snapshot_dir / "referralHistory" / "documents.jsonl"
        records = self.load_jsonl_file(referral_file)
        
        for record in records:
            referrer_id = record.get('referrerId', '').strip()
            referred_id = record.get('referredId', '').strip()
            
            if referrer_id:
                self.referral_history[referrer_id].append(record)
                self.stats["total_referral_records"] += 1
            
            # Track who referred each user (store only the first/most relevant one)
            if referred_id and referred_id not in self.referred_by:
                self.referred_by[referred_id] = record
        
        print(f"Loaded {self.stats['total_referral_records']} referral records for {len(self.referral_history)} referrers")
    
    def load_mini_game_progress(self):
        """Load mini-game progress and index by userId."""
        print("Loading mini-game progress...")
        mini_game_file = self.convex_snapshot_dir / "userMiniGameProgress" / "documents.jsonl"
        records = self.load_jsonl_file(mini_game_file)
        
        for record in records:
            user_id = record.get('userId', '').strip()
            if user_id:
                self.mini_game_progress[user_id].append(record)
                self.stats["total_mini_game_records"] += 1
        
        print(f"Loaded {self.stats['total_mini_game_records']} mini-game records for {len(self.mini_game_progress)} users")
    
    def match_users(self):
        """Match users between Clerk and Convex systems."""
        print("\nMatching users...")
        matched_user_ids = set()
        
        # Find matches
        for clerk_id in self.clerk_users.keys():
            if clerk_id in self.convex_users:
                matched_user_ids.add(clerk_id)
        
        self.stats["matched_users"] = len(matched_user_ids)
        self.stats["clerk_only"] = len(self.clerk_users) - len(matched_user_ids)
        self.stats["convex_only"] = len(self.convex_users) - len(matched_user_ids)
        
        # Calculate match rate
        total_unique_users = len(set(self.clerk_users.keys()) | set(self.convex_users.keys()))
        if total_unique_users > 0:
            match_rate = (self.stats["matched_users"] / total_unique_users) * 100
        else:
            match_rate = 0.0
        
        print(f"Matched: {self.stats['matched_users']} users")
        print(f"Clerk only: {self.stats['clerk_only']} users")
        print(f"Convex only: {self.stats['convex_only']} users")
        print(f"Match rate: {match_rate:.2f}%")
        
        return matched_user_ids
    
    def create_linked_user_record(self, user_id: str) -> Dict[str, Any]:
        """Create a comprehensive linked user record with all associated data."""
        clerk_data = self.clerk_users.get(user_id, {})
        convex_profile = self.convex_users.get(user_id, {})
        
        # Get all related data
        points_hist = self.points_history.get(user_id, [])
        referrals_made = self.referral_history.get(user_id, [])
        referred_by_record = self.referred_by.get(user_id)
        mini_game_records = self.mini_game_progress.get(user_id, [])
        
        # Sort points history by creation time
        points_hist_sorted = sorted(points_hist, key=lambda x: x.get('_creationTime', 0))
        
        # Sort referral history by creation time
        referrals_made_sorted = sorted(referrals_made, key=lambda x: x.get('_creationTime', 0))
        
        linked_record = {
            "clerkId": user_id,
            "convexId": convex_profile.get('_id') if convex_profile else None,
            "clerkData": clerk_data,
            "convexProfile": convex_profile if convex_profile else None,
            "pointsHistory": points_hist_sorted,
            "referralsMade": referrals_made_sorted,
            "referredBy": referred_by_record,
            "miniGameProgress": mini_game_records,
            # Metadata
            "totalPointsEarned": sum(item.get('pointsEarned', 0) for item in points_hist),
            "totalReferralsMade": len(referrals_made),
            "hasClerkData": bool(clerk_data),
            "hasConvexData": bool(convex_profile),
        }
        
        return linked_record
    
    def generate_linked_users_file(self, matched_user_ids: set):
        """Generate the linked_users.jsonl file with all matched users."""
        print("\nGenerating linked_users.jsonl...")
        output_file = self.output_dir / "linked_users.jsonl"
        
        linked_count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for user_id in sorted(matched_user_ids):
                linked_record = self.create_linked_user_record(user_id)
                f.write(json.dumps(linked_record, ensure_ascii=False) + '\n')
                linked_count += 1
        
        print(f"Wrote {linked_count} linked user records to {output_file}")
    
    def generate_unmatched_users_file(self, matched_user_ids: set):
        """Generate the unmatched_users.jsonl file with users from only one system."""
        print("\nGenerating unmatched_users.jsonl...")
        output_file = self.output_dir / "unmatched_users.jsonl"
        
        unmatched_count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            # Clerk-only users
            for user_id in sorted(self.clerk_users.keys()):
                if user_id not in matched_user_ids:
                    unmatched_record = {
                        "source": "clerk",
                        "id": user_id,
                        "data": self.clerk_users[user_id],
                        "reason": "missing_in_convex"
                    }
                    f.write(json.dumps(unmatched_record, ensure_ascii=False) + '\n')
                    unmatched_count += 1
            
            # Convex-only users
            for user_id in sorted(self.convex_users.keys()):
                if user_id not in matched_user_ids:
                    unmatched_record = {
                        "source": "convex",
                        "id": user_id,
                        "data": self.convex_users[user_id],
                        "reason": "missing_in_clerk"
                    }
                    f.write(json.dumps(unmatched_record, ensure_ascii=False) + '\n')
                    unmatched_count += 1
        
        print(f"Wrote {unmatched_count} unmatched user records to {output_file}")
    
    def generate_sync_report(self):
        """Generate the sync_report.json file with summary statistics."""
        print("\nGenerating sync_report.json...")
        output_file = self.output_dir / "sync_report.json"
        
        total_unique_users = len(set(self.clerk_users.keys()) | set(self.convex_users.keys()))
        match_rate = (self.stats["matched_users"] / total_unique_users * 100) if total_unique_users > 0 else 0.0
        
        report = {
            **self.stats,
            "match_rate_percent": round(match_rate, 2),
            "total_unique_users": total_unique_users,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Wrote sync report to {output_file}")
        return report
    
    def run(self):
        """Execute the full comparison and migration process."""
        print("=" * 60)
        print("User Data Migration and Comparison Tool")
        print("=" * 60)
        
        # Load all data
        self.load_clerk_data()
        self.load_convex_users()
        self.load_points_history()
        self.load_referral_history()
        self.load_mini_game_progress()
        
        # Match users
        matched_user_ids = self.match_users()
        
        # Generate output files
        self.generate_linked_users_file(matched_user_ids)
        self.generate_unmatched_users_file(matched_user_ids)
        report = self.generate_sync_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Total Clerk users: {report['total_clerk_users']}")
        print(f"Total Convex users: {report['total_convex_users']}")
        print(f"Matched users: {report['matched_users']}")
        print(f"Clerk-only users: {report['clerk_only']}")
        print(f"Convex-only users: {report['convex_only']}")
        print(f"Match rate: {report['match_rate_percent']}%")
        print(f"\nOutput files written to: {self.output_dir}/")
        print("  - linked_users.jsonl")
        print("  - unmatched_users.jsonl")
        print("  - sync_report.json")
        print("=" * 60)


def main():
    """Main entry point."""
    # Default paths
    script_dir = Path(__file__).parent
    clerk_csv = script_dir / "ins_2zQQjKKXdf536Mz8OXAmkRUqmUa (1).csv"
    convex_snapshot = script_dir / "snapshot_agreeable-frog-992_1767312048617181600"
    
    # Check if files exist
    if not clerk_csv.exists():
        print(f"Error: Clerk CSV file not found: {clerk_csv}")
        sys.exit(1)
    
    if not convex_snapshot.exists():
        print(f"Error: Convex snapshot directory not found: {convex_snapshot}")
        sys.exit(1)
    
    # Create comparer and run
    comparer = UserDataComparer(
        clerk_csv_path=str(clerk_csv),
        convex_snapshot_dir=str(convex_snapshot),
        output_dir="output"
    )
    comparer.run()


if __name__ == "__main__":
    main()
