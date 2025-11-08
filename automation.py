"""
CRM Automation - OmniDimension Call Dispatcher
Monitors a CSV file for new leads and automatically dispatches calls via OmniDim API.
"""

import csv
import os
import time
from typing import Set, Dict, List
import config
from omnidim_client import OmniDimClient


class CRMAutomation:
    """Main automation class for monitoring leads and dispatching calls."""
    
    def __init__(self):
        """Initialize the automation with API client and tracking."""
        self.client = OmniDimClient(config.OMNIDIM_API_KEY)
        self.processed_leads: Set[str] = set()
        self.input_csv = config.INPUT_CSV_PATH
    
    def read_leads(self) -> List[Dict]:
        """
        Read all leads from the input CSV file.
        
        Returns:
            List of lead dictionaries
        """
        leads = []
        if not os.path.exists(self.input_csv):
            return leads
        
        with open(self.input_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append(row)
        
        return leads
    
    def get_new_leads(self) -> List[Dict]:
        """
        Filter leads to find only new ones that haven't been processed.
        
        Returns:
            List of new lead dictionaries
        """
        all_leads = self.read_leads()
        new_leads = []
        
        for lead in all_leads:
            lead_id = lead.get('lead_id', '')
            if lead_id and lead_id not in self.processed_leads:
                new_leads.append(lead)
        
        return new_leads
    
    def process_lead(self, lead: Dict):
        """
        Process a single lead by dispatching a call.
        
        Args:
            lead: Dictionary containing lead information
        """
        lead_id = lead.get('lead_id', '')
        phone_number = lead.get('phone_number', '')
        
        if not phone_number:
            print(f"Lead {lead_id} has no phone number, skipping")
            self.processed_leads.add(lead_id)
            return
        
        print(f"\nProcessing lead {lead_id}: {lead.get('name', 'Unknown')}")
        
        call_id = self.client.dispatch_call(phone_number, lead)
        
        if call_id:
            print(f"✓ Call dispatched for lead {lead_id}")
        else:
            print(f"✗ Failed to dispatch call for lead {lead_id}")
        
        self.processed_leads.add(lead_id)
    
    def run(self):
        """Main automation loop - monitors CSV and processes new leads."""
        print("CRM Automation started. Monitoring for new leads...")
        print(f"Input CSV: {self.input_csv}")
        print(f"Poll interval: {config.POLL_INTERVAL} seconds\n")
        
        while True:
            try:
                new_leads = self.get_new_leads()
                
                if new_leads:
                    print(f"Found {len(new_leads)} new lead(s)")
                    for lead in new_leads:
                        self.process_lead(lead)
                        time.sleep(2)
                
                time.sleep(config.POLL_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nAutomation stopped by user")
                break
            except Exception as e:
                print(f"Error in automation loop: {e}")
                time.sleep(config.POLL_INTERVAL)


if __name__ == "__main__":
    automation = CRMAutomation()
    automation.run()

