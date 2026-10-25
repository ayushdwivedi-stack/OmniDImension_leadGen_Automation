import os
import re
from typing import Dict, Optional
import requests
import config

E164_PHONE = re.compile(r"^\+[1-9]\d{7,14}$")


class OmniDimClient:
    """Client for interacting with OmniDimension API to dispatch calls."""
    
    def __init__(self, api_key: str, agent_id: Optional[int] = None, base_url: Optional[str] = None):
        """
        Initialize the OmniDim API client.
        
        Args:
            api_key: Your OmniDimension API key
            agent_id: Optional agent ID override (defaults to config.AGENT_ID)
            base_url: Optional base URL override (defaults to backend.omnidim.io/api/v1)
        """
        raw_agent_id = agent_id if agent_id is not None else getattr(config, 'AGENT_ID', '')
        if not raw_agent_id or str(raw_agent_id).strip() == '':
            raise ValueError("AGENT_ID must be configured as a valid integer.")
        self.agent_id = int(raw_agent_id)
        self.api_key = api_key
        self.base_url = (base_url or "https://backend.omnidim.io/api/v1").rstrip('/')

    @staticmethod
    def normalize_phone_number(phone: str) -> Optional[str]:
        """
        Sanitize and validate a phone number according to the E.164 standard.
        Strips whitespace, parentheses, and dashes.
        """
        if not phone:
            return None
        cleaned = re.sub(r"[\s\-\(\)\.]", "", str(phone).strip())
        if not cleaned:
            return None
        if not cleaned.startswith("+"):
            cleaned = "+" + cleaned
        if not E164_PHONE.match(cleaned):
            return None
        return cleaned
    
    def dispatch_call(self, phone_number: str, lead_data: Dict, timeout: float = 30.0) -> Optional[str]:
        """
        Dispatch a call to a phone number using the configured agent.
        
        Args:
            phone_number: Phone number to call (with country code)
            lead_data: Dictionary containing lead information (name, email, etc.)
            timeout: HTTP request timeout in seconds
            
        Returns:
            Call ID if successful, None if failed
        """
        normalized_number = self.normalize_phone_number(phone_number)
        if not normalized_number:
            print(f"  Invalid phone number format: '{phone_number}'. Expected E.164 format (e.g. +15551234567).")
            return None
        
        call_context = {
            "customer_name": lead_data.get('name', 'Unknown'),
            "email": lead_data.get('email', 'N/A'),
            "lead_id": lead_data.get('lead_id', 'N/A')
        }
        
        payload = {
            "agent_id": self.agent_id,
            "to_number": normalized_number,
            "call_context": call_context
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/calls/dispatch",
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get('call_id') or data.get('id') or "success"
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
            return None
