"""
Scratch org inventory management and tracking.

This module helps maintain awareness of DevHub scratch org capacity
and ensures we have sufficient resources for evaluations.
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from sfbench.utils.sfdx import (
    get_connected_devhubs,
    get_devhub_limits,
    get_scratch_org_limits,
    run_sfdx,
    parse_json_output
)


class ScratchOrgInventory:
    """Tracks scratch org inventory across all DevHubs."""
    
    def __init__(self, target_daily_capacity: int = 160):
        """
        Initialize inventory tracker.
        
        Args:
            target_daily_capacity: Target daily scratch org capacity (default: 160)
        """
        self.target_daily_capacity = target_daily_capacity
        self.inventory_file = Path(__file__).parent.parent.parent / "_internal" / "scratch_org_inventory.json"
        self.inventory_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_all_devhub_capacity(self) -> Dict[str, Dict[str, int]]:
        """
        Get total capacity across all DevHubs.
        
        Returns:
            Dict mapping DevHub alias to capacity info:
            {
                'alias': {
                    'daily_max': int,
                    'daily_remaining': int,
                    'active_max': int,
                    'active_remaining': int,
                    'username': str
                }
            }
        """
        # Always try direct query first (more reliable)
        devhubs = []
        try:
            from sfbench.utils.sfdx import run_sfdx, parse_json_output
            exit_code, stdout, stderr = run_sfdx("sf org list", timeout=30)
            if exit_code == 0:
                data = parse_json_output(stdout)
                result = data.get('result', {})
                # Get from devHubs list
                devhubs_list = result.get('devHubs', [])
                # Get from nonScratchOrgs with isDevHub flag
                non_scratch = result.get('nonScratchOrgs', [])
                devhubs_list.extend([o for o in non_scratch if o.get('isDevHub', False)])
                
                # Convert to expected format - include all DevHubs, not just "Connected"
                for org in devhubs_list:
                    status = org.get('connectedStatus', '')
                    alias = org.get('alias') or org.get('username', '')
                    if alias:  # Only add if we have an alias/username
                        devhubs.append({
                            'alias': alias,
                            'username': org.get('username', alias),
                            'orgId': org.get('orgId', ''),
                            'isDefault': org.get('isDefaultDevHubUsername', False),
                            'connectedStatus': status
                        })
        except Exception as e:
            # Fallback to get_connected_devhubs if direct query fails
            devhubs = get_connected_devhubs()
        
        # If still no DevHubs, try the helper function
        if not devhubs:
            devhubs = get_connected_devhubs()
        
        capacity = {}
        
        for hub in devhubs:
            alias = hub.get('alias') or hub.get('username', '')
            if not alias:
                continue
            
            # Get limits for this DevHub
            limits = get_devhub_limits(alias)
            if not limits or not limits.get('daily_max'):
                # Fallback: try get_scratch_org_limits
                try:
                    limits_data = get_scratch_org_limits(alias)
                    if limits_data:
                        limits = {
                            'daily_max': limits_data.get('dailyScratchOrgs', {}).get('Max', 0),
                            'daily_remaining': limits_data.get('dailyScratchOrgs', {}).get('Remaining', 0),
                            'active_max': limits_data.get('activeScratchOrgs', {}).get('Max', 0),
                            'active_remaining': limits_data.get('activeScratchOrgs', {}).get('Remaining', 0)
                        }
                except Exception:
                    # If we can't get limits, use conservative defaults
                    limits = {
                        'daily_max': 80,  # Enterprise Edition default
                        'daily_remaining': 80,
                        'active_max': 40,
                        'active_remaining': 40
                    }
            
            capacity[alias] = {
                'daily_max': limits.get('daily_max', 0),
                'daily_remaining': limits.get('daily_remaining', 0),
                'active_max': limits.get('active_max', 0),
                'active_remaining': limits.get('active_remaining', 0),
                'username': hub.get('username', alias)
            }
        
        return capacity
    
    def get_total_capacity(self) -> Dict[str, int]:
        """
        Get total capacity across all DevHubs.
        
        Returns:
            {
                'total_daily_max': int,
                'total_daily_remaining': int,
                'total_active_max': int,
                'total_active_remaining': int,
                'devhub_count': int
            }
        """
        capacity = self.get_all_devhub_capacity()
        
        total_daily_max = sum(hub.get('daily_max', 0) for hub in capacity.values())
        total_daily_remaining = sum(hub.get('daily_remaining', 0) for hub in capacity.values())
        total_active_max = sum(hub.get('active_max', 0) for hub in capacity.values())
        total_active_remaining = sum(hub.get('active_remaining', 0) for hub in capacity.values())
        
        return {
            'total_daily_max': total_daily_max,
            'total_daily_remaining': total_daily_remaining,
            'total_active_max': total_active_max,
            'total_active_remaining': total_active_remaining,
            'devhub_count': len(capacity)
        }
    
    def check_sufficient_capacity(self, required_daily: int = 12) -> Tuple[bool, str, Dict[str, int]]:
        """
        Check if we have sufficient capacity for evaluations.
        
        Args:
            required_daily: Required daily scratch orgs (default: 12 for full evaluation)
        
        Returns:
            (has_sufficient, message, capacity_info)
        """
        total = self.get_total_capacity()
        
        has_sufficient = total['total_daily_remaining'] >= required_daily
        
        if has_sufficient:
            message = (
                f"✅ Sufficient capacity: {total['total_daily_remaining']} daily scratch orgs available "
                f"(across {total['devhub_count']} DevHub{'s' if total['devhub_count'] != 1 else ''})"
            )
        else:
            message = (
                f"❌ Insufficient capacity: Need {required_daily} daily scratch orgs, "
                f"have {total['total_daily_remaining']} available "
                f"(across {total['devhub_count']} DevHub{'s' if total['devhub_count'] != 1 else ''})"
            )
        
        # Check if we meet target
        if total['total_daily_remaining'] < self.target_daily_capacity:
            if has_sufficient:
                message += f"\n⚠️  Below target capacity of {self.target_daily_capacity} daily scratch orgs"
        
        return has_sufficient, message, total
    
    def save_inventory_snapshot(self) -> None:
        """Save current inventory state to file."""
        capacity = self.get_all_devhub_capacity()
        total = self.get_total_capacity()
        
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'target_daily_capacity': self.target_daily_capacity,
            'devhubs': capacity,
            'totals': total
        }
        
        with open(self.inventory_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
    
    def load_inventory_snapshot(self) -> Optional[Dict]:
        """Load last saved inventory snapshot."""
        if not self.inventory_file.exists():
            return None
        
        try:
            with open(self.inventory_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def print_inventory_report(self) -> None:
        """Print a formatted inventory report."""
        capacity = self.get_all_devhub_capacity()
        total = self.get_total_capacity()
        
        print("\n" + "=" * 70)
        print("📊 SCRATCH ORG INVENTORY REPORT")
        print("=" * 70)
        print(f"\n🎯 Target Daily Capacity: {self.target_daily_capacity}")
        print(f"📈 Total DevHubs: {total['devhub_count']}")
        print()
        
        if capacity:
            print("DevHub Details:")
            print("-" * 70)
            for alias, hub_info in capacity.items():
                daily_pct = (hub_info['daily_remaining'] / hub_info['daily_max'] * 100) if hub_info['daily_max'] > 0 else 0
                active_pct = (hub_info['active_remaining'] / hub_info['active_max'] * 100) if hub_info['active_max'] > 0 else 0
                
                print(f"  {alias}:")
                print(f"    Daily:  {hub_info['daily_remaining']:3d}/{hub_info['daily_max']:3d} ({daily_pct:.1f}%)")
                print(f"    Active: {hub_info['active_remaining']:3d}/{hub_info['active_max']:3d} ({active_pct:.1f}%)")
                print(f"    Username: {hub_info['username']}")
                print()
        else:
            print("  ⚠️  No DevHubs found or unable to query limits")
            print()
        
        print("Totals:")
        print("-" * 70)
        total_daily_pct = (total['total_daily_remaining'] / total['total_daily_max'] * 100) if total['total_daily_max'] > 0 else 0
        total_active_pct = (total['total_active_remaining'] / total['total_active_max'] * 100) if total['total_active_max'] > 0 else 0
        
        print(f"  Daily:  {total['total_daily_remaining']:3d}/{total['total_daily_max']:3d} ({total_daily_pct:.1f}%)")
        print(f"  Active: {total['total_active_remaining']:3d}/{total['total_active_max']:3d} ({total_active_pct:.1f}%)")
        print()
        
        # Check against target
        if total['total_daily_remaining'] >= self.target_daily_capacity:
            print(f"✅ Meets target capacity ({self.target_daily_capacity} daily scratch orgs)")
        else:
            shortfall = self.target_daily_capacity - total['total_daily_remaining']
            print(f"⚠️  Below target capacity: Need {shortfall} more daily scratch orgs")
        
        print("=" * 70)


def check_inventory(required_daily: int = 12, target_daily: int = 160) -> Tuple[bool, str]:
    """
    Quick inventory check function.
    
    Args:
        required_daily: Required daily scratch orgs
        target_daily: Target daily capacity
    
    Returns:
        (has_sufficient, message)
    """
    inventory = ScratchOrgInventory(target_daily_capacity=target_daily)
    has_sufficient, message, _ = inventory.check_sufficient_capacity(required_daily)
    return has_sufficient, message
