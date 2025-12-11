"""AMS360 SOAP service for customer and policy management."""

import logging
import os
import time
import requests
import xmltodict
from functools import wraps
from typing import Optional, Dict
from dotenv import load_dotenv
import json
load_dotenv()
logger = logging.getLogger("telephony-agent")

# AMS360 Configuration from environment variables
AMS360_BASE_URL = os.getenv("AMS360_BASE_URL", "https://wsapi.ams360.com/v3/WSAPIService.svc")
AMS360_AGENCY_NO = os.getenv("AMS360_AGENCY_NO")
AMS360_LOGIN_ID = os.getenv("AMS360_LOGIN_ID")
AMS360_PASSWORD = os.getenv("AMS360_PASSWORD")


class AMS360Service:
    """Service for interacting with AMS360 SOAP API."""
    
    def __init__(self):
        """Initialize AMS360 service with session management."""
        # Simple in-memory cache for AMS360 session token (Ticket) with expiry
        self.session = {
            'ticket': None,
            'expires_at': 0,
            'customer_id': None,
            'policy_id': None
        }
        logger.info("AMS360Service initialized")
    
    def _ensure_session(self):
        """Ensure valid AMS360 session exists, logging in if necessary."""
        now = time.time()
        if not self.session['ticket'] or self.session['expires_at'] <= now:
            logger.info('AMS360 session missing or expired. Logging in...')
            ok = self._login()
            if not ok:
                raise RuntimeError('AMS360 login failed')
    
    def _login(self) -> bool:
        """Login to AMS360 and cache session ticket. Returns True on success."""
        envelope = f'''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <Login xmlns="http://www.WSAPI.AMS360.com/v3.0">
      <Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <a:AgencyNo>{AMS360_AGENCY_NO}</a:AgencyNo>
        <a:LoginId>{AMS360_LOGIN_ID}</a:LoginId>
        <a:Password>{AMS360_PASSWORD}</a:Password>
        <a:EmployeeCode/>
      </Request>
    </Login>
  </s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/Login"'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            # Safe navigation to find Ticket value — adjust if response differs
            ticket = None
            try:
                ticket = parsed['s:Envelope']['s:Header']['WSAPISession']['Ticket']
            except Exception:
                # Try alternative paths
                try:
                    ticket = parsed['Envelope']['Body']['LoginResponse']['LoginResult']['Ticket']
                except Exception:
                    ticket = None
            
            if not ticket:
                logger.error('AMS360 login: ticket not found in response')
                logger.debug('Raw response: %s', r.text)
                return False
            
            # Ticket validity unknown — set short expiry (15 minutes)
            self.session['ticket'] = ticket
            self.session['expires_at'] = time.time() + (15 * 60)
            logger.info('AMS360 login successful, ticket cached')
            return True
            
        except Exception as e:
            logger.exception('AMS360 login failed: %s', e)
            return False
    
    def search_customer_by_phone(self, phone: str, max_rows: int = 5) -> Optional[Dict]:
        """Search customer by phone number. Returns parsed result or None.
        
        Args:
            phone: Phone number to search for
            max_rows: Maximum number of rows to return (default 5)
            
        Returns:
            Dictionary with customer search results or None if failed
        """
        self._ensure_session()
        
        # Note: AMS360 may not have a direct "get by phone" method.
        # This example demonstrates CustomerGetListByNamePrefix.
        # Adapt this to your specific AMS360 SOAP method for phone search.
        envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Body>
<CustomerGetListByNamePrefix xmlns="http://www.WSAPI.AMS360.com/v3.0">
<Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
<a:Ticket>{self.session['ticket']}</a:Ticket>
<a:NamePrefix>{phone}</a:NamePrefix>
<a:MaxRows>{max_rows}</a:MaxRows>
</Request>
</CustomerGetListByNamePrefix>
</s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/CustomerGetListByNamePrefix"'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            logger.info(f"AMS360 customer search by phone completed: {phone}")
            return parsed
            
        except Exception as e:
            logger.exception(f'AMS360 customer search failed: {e}')
            return None
    
    def search_customer_by_name(self, name_prefix: str, max_rows: int = 10) -> Optional[Dict]:
        """Search customer by name prefix. Returns parsed result or None.
        
        Args:
            name_prefix: Name prefix to search for
            max_rows: Maximum number of rows to return (default 10)
            
        Returns:
            Dictionary with customer search results or None if failed
        """
        self._ensure_session()
        
        envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Body>
<CustomerGetListByNamePrefix xmlns="http://www.WSAPI.AMS360.com/v3.0">
<Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
<a:Ticket>{self.session['ticket']}</a:Ticket>
<a:NamePrefix>{name_prefix}</a:NamePrefix>
<a:MaxRows>{max_rows}</a:MaxRows>
</Request>
</CustomerGetListByNamePrefix>
</s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/CustomerGetListByNamePrefix"'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            logger.info(f"AMS360 customer search by name completed: {name_prefix}")
            return parsed
            
        except Exception as e:
            logger.exception(f'AMS360 customer search by name failed: {e}')
            return None

    
    def get_customer_details(self, customer_id: str) -> Optional[Dict]:
        """Get policies for a specific customer. Returns parsed result or None.
        
        Args:
            customer_id: The customer ID to retrieve policies for
            
        Returns:
            Dictionary with customer policies or None if failed
        """
        self._ensure_session()
        
        envelope = f'''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Header>
    <WSAPISession xmlns="http://www.WSAPI.AMS360.com/v3.0">
      <Ticket>{self.session['ticket']}</Ticket>
    </WSAPISession>
  </s:Header>
  <s:Body>
    <CustomerGetById xmlns="http://www.WSAPI.AMS360.com/v3.0">
      <Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <a:CustomerId>{customer_id}</a:CustomerId>
      </Request>
    </CustomerGetById>
  </s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/CustomerGetById'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            logger.info(f"AMS360 customer details retrieved for customer: {customer_id}")
            return parsed
            
        except Exception as e:
            logger.exception(f'AMS360 get customer policies failed: {e}')
            return None
    
    def get_customer_policies(self, customer_id: str) -> Optional[Dict]:
        """Get policies for a specific customer. Returns parsed result or None.
        
        Args:
            customer_id: The customer ID to retrieve policies for
            
        Returns:
            Dictionary with customer policies or None if failed
        """
        self._ensure_session()
        
        envelope = f'''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Header>
    <WSAPISession xmlns="http://www.WSAPI.AMS360.com/v3.0">
      <Ticket>{self.session['ticket']}</Ticket>
    </WSAPISession>
  </s:Header>
  <s:Body>
    <PolicyGetListByCustomerId xmlns="http://www.WSAPI.AMS360.com/v3.0">
      <Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <a:CustomerId>{customer_id}</a:CustomerId>
      </Request>
    </PolicyGetListByCustomerId>
  </s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/PolicyGetListByCustomerId'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            logger.info(f"AMS360 policies retrieved for customer: {customer_id}")
            return parsed
            
        except Exception as e:
            logger.exception(f'AMS360 get customer policies failed: {e}')
            return None
    
    def get_policy_by_number(self, policy_number: str) -> Optional[Dict]:
        """Get policy information by policy number and store customer_id and policy_id in session.
        
        Args:
            policy_number: The policy number to search for
            
        Returns:
            Dictionary with policy list results or None if failed
        """
        self._ensure_session()
        
        envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Header>
<WSAPISession xmlns="http://www.WSAPI.AMS360.com/v3.0">
<Ticket>{self.session['ticket']}</Ticket>
</WSAPISession>
</s:Header>
<s:Body>
<PolicyGetListByPolicyNumber xmlns="http://www.WSAPI.AMS360.com/v3.0">
<Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
<a:PolicyNumber>{policy_number}</a:PolicyNumber>
</Request>
</PolicyGetListByPolicyNumber>
</s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/PolicyGetListByPolicyNumber"'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            # Extract and store customer_id and policy_id in session
            try:
                # Navigate through the XML structure to find IDs
                policy_result = parsed.get('s:Envelope', {}).get('s:Body', {}).get('PolicyGetListByPolicyNumberResponse', {})
                if not policy_result:
                    # Try alternative path
                    policy_result = parsed.get('Envelope', {}).get('Body', {}).get('PolicyGetListByPolicyNumberResponse', {})
                
                result_data = policy_result.get('PolicyGetListByPolicyNumberResult', {})
                policy_list = result_data.get('a:PolicyInfoList', {}).get('a:PolicyInfo', {})
                
                # Handle if policy_list is a list (multiple results) or dict (single result)
                if isinstance(policy_list, list):
                    policy_data = policy_list[0] if policy_list else {}
                else:
                    policy_data = policy_list
                
                customer_id = policy_data.get('a:CustomerId')
                policy_id = policy_data.get('a:PolicyId')
                
                if customer_id and policy_id:
                    self.session['customer_id'] = customer_id
                    self.session['policy_id'] = policy_id
                    logger.info(f"AMS360 stored customer_id: {customer_id}, policy_id: {policy_id}")
                    parsed1 = self.get_policy_details(policy_id)
                    parsed2=self.get_customer_policies(customer_id)
                    parsed3=self.get_customer_details(customer_id)
                    json.dumps(parsed1,indent=4)
                    json.dumps(parsed2,indent=4)
                    json.dumps(parsed3,indent=4)
                    return parsed1,parsed2,parsed3
                else:
                    logger.warning("AMS360 could not extract policy_id from response")
                    return None
            except Exception as e:
                logger.warning(f"AMS360 failed to extract policy_id from policy response: {e}")
                return None
            
            logger.info(f"AMS360 policy lookup by number completed: {policy_number}")
            return None
            
        except Exception as e:
            logger.exception(f'AMS360 get policy by number failed: {e}')
            return None
    
    def get_policy_details(self, policy_id: str = None) -> Optional[Dict]:
        """Get detailed policy information using customer_id and policy_id.
        
        Args:
            policy_id: The policy ID (uses session value if not provided)
            
        Returns:
            Dictionary with detailed policy information or None if failed
        """
        self._ensure_session()
        
        # Use provided IDs or fall back to session values
        pol_id = policy_id or self.session.get('policy_id')
        
        if not pol_id:
            logger.error("AMS360 get_policy_details: policy_id is required")
            return None
        
        envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Header>
<WSAPISession xmlns="http://www.WSAPI.AMS360.com/v3.0">
<Ticket>{self.session['ticket']}</Ticket>
</WSAPISession>
</s:Header>
<s:Body>
<PolicyGet xmlns="http://www.WSAPI.AMS360.com/v3.0">
<Request xmlns:a="http://www.WSAPI.AMS360.com/v3.0/DataContract" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
<a:PolicyId>{pol_id}</a:PolicyId>
</Request>
</PolicyGet>
</s:Body>
</s:Envelope>'''
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://www.WSAPI.AMS360.com/v3.0/WSAPIServiceContract/PolicyGet"'
        }
        
        try:
            r = requests.post(AMS360_BASE_URL, data=envelope.encode('utf-8'), headers=headers, timeout=20)
            r.raise_for_status()
            parsed = xmltodict.parse(r.text)
            
            logger.info(f"AMS360 detailed policy info retrieved for customer: policy: {pol_id}")
            logger.info(json.dumps(parsed,indent=4))
            return parsed
            
        except Exception as e:
            logger.exception(f'AMS360 get policy details failed: {e}')
            return None

