"""AgencyZoom API service for lead and opportunity management."""

import logging
import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("telephony-agent")

# AgencyZoom Configuration from environment variables
AGENCYZOOM_API_KEY = os.getenv("AGENCYZOOM_API_KEY")
AGENCYZOOM_BASE_URL = os.getenv("AGENCYZOOM_BASE_URL", "https://api.agencyzoom.com/v1")
AGENCYZOOM_AGENCY_ID = os.getenv("AGENCYZOOM_AGENCY_ID")


class AgencyZoomService:
    """Service for interacting with AgencyZoom REST API."""
    
    def __init__(self):
        """Initialize AgencyZoom service."""
        self.api_key = AGENCYZOOM_API_KEY
        self.base_url = AGENCYZOOM_BASE_URL
        self.agency_id = AGENCYZOOM_AGENCY_ID
        
        # Ensure base_url ends with /v1
        if self.base_url and not self.base_url.endswith('/v1'):
            if not self.base_url.endswith('/'):
                self.base_url += '/v1'
            else:
                self.base_url += 'v1'
        
        if not self.api_key:
            logger.warning("AgencyZoom API key not configured")
        
        logger.info(f"AgencyZoomService initialized with base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for AgencyZoom API requests."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new lead in AgencyZoom with comprehensive insurance data.
        
        Args:
            lead_data: Dictionary containing lead information
                {
                    "firstname": str,
                    "lastname": str,
                    "email": str,
                    "phone": str,
                    "secondaryEmail": str (optional),
                    "secondaryPhone": str (optional),
                    "notes": str (optional),
                    "pipelineId": int (optional),
                    "stageId": int (optional),
                    "contactDate": str (optional, YYYY-MM-DD),
                    "soldDate": str (optional, YYYY-MM-DD),
                    "leadSourceId": int (optional),
                    "assignmentGroupId": int (optional),
                    "xDate": str (optional, YYYY-MM-DD),
                    "quoteDate": str (optional, YYYY-MM-DD),
                    "assignTo": int (optional),
                    "csrId": int (optional),
                    "streetAddress": str (optional),
                    "streetAddressLine2": str (optional),
                    "city": str (optional),
                    "state": str (optional),
                    "country": str (optional),
                    "zip": str (optional),
                    "agencyNumber": str (optional),
                    "departmentCode": str (optional),
                    "groupCode": str (optional),
                    "customFields": list (optional) - [{"fieldName": "cf1", "fieldValue": ["value"]}]
                }
        
        Returns:
            Dictionary with created lead data or None if failed
        """
        if not self.api_key:
            logger.error("Cannot create lead: AgencyZoom API key not configured")
            return None
        
        endpoint = f"{self.base_url}/api/leads/create"
        
        # Prepare payload matching AgencyZoom API schema
        payload = {
            "firstname": lead_data.get("firstname") or lead_data.get("first_name", ""),
            "lastname": lead_data.get("lastname") or lead_data.get("last_name", ""),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone", ""),
            "pipelineId": lead_data.get("pipelineId", 3816),
            "stageId": lead_data.get("stageId", 11446),
            "leadSourceId": 113762,
            "assignTo": 148687,
        }
        
        # Add optional fields if provided
        optional_fields = [
            "secondaryEmail", "secondaryPhone", "notes",
            "contactDate", "soldDate", "assignmentGroupId",
            "xDate", "quoteDate", "csrId", "streetAddress",
            "streetAddressLine2", "city", "state", "country", "zip",
            "agencyNumber", "departmentCode", "groupCode"
        ]
        
        for field in optional_fields:
            if field in lead_data and lead_data[field] is not None:
                payload[field] = lead_data[field]
        
        # Handle custom fields - only add fields that are NOT standard AgencyZoom fields
        standard_fields = {
            "firstname", "lastname", "first_name", "last_name", "email", "phone",
            "pipelineId", "stageId", "leadSourceId", "assignTo", *optional_fields
        }
        
        custom_fields = []
        for field, value in lead_data.items():
            if field not in standard_fields and value is not None:
                custom_fields.append({
                    "fieldName": field,
                    "fieldValue": [str(value)] if not isinstance(value, list) else value
                })
        
        if custom_fields:
            payload["customFields"] = custom_fields
        
        try:
            r = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=15)
            r.raise_for_status()
            result = r.json()
            
            logger.info(f"AgencyZoom lead created successfully: {lead_data.get('email')}")
            logger.info(f"AgencyZoom lead created successfully: {result}")
            logger.info(f"AgencyZoom lead created successfully: {payload}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"AgencyZoom create lead failed: {e}")
            return None
    
    def search_contact_by_phone(self, phone: str) -> Optional[Dict]:
        """Search for a contact by phone number.
        
        Args:
            phone: Phone number to search for
            
        Returns:
            Dictionary with contact search results or None if failed
        """
        if not self.api_key:
            logger.error("Cannot search contact: AgencyZoom API key not configured")
            return None
        
        endpoint = f"{self.base_url}/contacts/search"
        params = {"phone": phone}
        
        try:
            r = requests.get(endpoint, params=params, headers=self._get_headers(), timeout=15)
            r.raise_for_status()
            result = r.json()
            
            logger.info(f"AgencyZoom contact search by phone completed: {phone}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"AgencyZoom search contact by phone failed: {e}")
            return None
    
    def search_contact_by_email(self, email: str) -> Optional[Dict]:
        """Search for a contact by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Dictionary with contact search results or None if failed
        """
        if not self.api_key:
            logger.error("Cannot search contact: AgencyZoom API key not configured")
            return None
        
        endpoint = f"{self.base_url}/contacts/search"
        params = {"email": email}
        
        try:
            r = requests.get(endpoint, params=params, headers=self._get_headers(), timeout=15)
            r.raise_for_status()
            result = r.json()
            
            logger.info(f"AgencyZoom contact search by email completed: {email}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"AgencyZoom search contact by email failed: {e}")
            return None
    
    def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new opportunity in AgencyZoom.
        
        Args:
            opportunity_data: Dictionary containing opportunity information
                {
                    "contact_id": str,
                    "insurance_type": str,
                    "status": str,
                    "amount": float (optional),
                    "notes": str (optional),
                    "expected_close_date": str (optional, ISO format)
                }
        
        Returns:
            Dictionary with created opportunity data or None if failed
        """
        if not self.api_key:
            logger.error("Cannot create opportunity: AgencyZoom API key not configured")
            return None
        
        endpoint = f"{self.base_url}/opportunities"
        
        # Prepare payload
        payload = {
            "agency_id": self.agency_id,
            "contact_id": opportunity_data.get("contact_id"),
            "insurance_type": opportunity_data.get("insurance_type"),
            "status": opportunity_data.get("status", "new"),
            "amount": opportunity_data.get("amount"),
            "notes": opportunity_data.get("notes", ""),
            "expected_close_date": opportunity_data.get("expected_close_date"),
            "created_at": datetime.now().isoformat()
        }
        
        try:
            r = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=15)
            r.raise_for_status()
            result = r.json()
            
            logger.info(f"AgencyZoom opportunity created successfully for contact: {opportunity_data.get('contact_id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"AgencyZoom create opportunity failed: {e}")
            return None
    
    def update_contact(self, contact_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing contact in AgencyZoom.
        
        Args:
            contact_id: The ID of the contact to update
            update_data: Dictionary with fields to update
        
        Returns:
            Dictionary with updated contact data or None if failed
        """
        if not self.api_key:
            logger.error("Cannot update contact: AgencyZoom API key not configured")
            return None
        
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        
        try:
            r = requests.patch(endpoint, json=update_data, headers=self._get_headers(), timeout=15)
            r.raise_for_status()
            result = r.json()
            
            logger.info(f"AgencyZoom contact updated successfully: {contact_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"AgencyZoom update contact failed: {e}")
            return None
    
    def add_note_to_contact(self, contact_id: str, note: str) -> Optional[Dict]:
        """Add a note to a contact in AgencyZoom.
        
        Args:
            contact_id: The ID of the contact
            note: The note text to add
        
        Returns:
            Dictionary with result or None if failed
        """
        if not self.api_key:
            logger.error("Cannot add note: AgencyZoom API key not configured")
            return None
        
        endpoint = f"{self.base_url}/contacts/{contact_id}/notes"
        
        payload = {
            "note": note,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            r = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=15)
            r.raise_for_status()
            result = r.json()
            
            logger.info(f"AgencyZoom note added to contact: {contact_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"AgencyZoom add note failed: {e}")
            return None

