"""Insurance service for handling insurance data collection and submission."""

import logging
import json
import os
from pathlib import Path
from typing import Optional, Dict, TYPE_CHECKING
from datetime import datetime

from models.model import (
    HomeInsurance, AutoInsurance, FloodInsurance, LifeInsurance, CommercialInsurance,
    Person, ContactInfo, PolicyInfo, PropertyDetails, Driver, Vehicle,
    BusinessDetails, CoverageDetails, QuoteRequest, CoverageType, PolicyType, Address
)

if TYPE_CHECKING:
    from services.agencyzoom import AgencyZoomService

logger = logging.getLogger("telephony-agent")

# Create directory for storing insurance requests
INSURANCE_DATA_DIR = Path("insurance_requests")
INSURANCE_DATA_DIR.mkdir(exist_ok=True)


class InsuranceService:
    """Service for managing insurance quote collection and submission."""
    
    def __init__(self, agencyzoom_service: Optional['AgencyZoomService'] = None):
        """Initialize the insurance service.
        
        Args:
            agencyzoom_service: Optional AgencyZoom service for automatic lead submission
        """
        self.user_action: Optional[str] = None  # "add" or "update"
        self.insurance_type: Optional[str] = None  # "home", "auto", "flood", "life", "commercial"
        self.collected_data: Dict = {}  # Store collected information
        self.quote_submitted: bool = False
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")  # Unique session ID
        self.agencyzoom_service = agencyzoom_service
        logger.info(f"InsuranceService initialized with session_id: {self.session_id}")
    
    def _save_to_json(self, data: Dict, filename: str) -> bool:
        """Save data to a JSON file.
        
        Args:
            data: Dictionary data to save
            filename: Name of the file (without path)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = INSURANCE_DATA_DIR / filename
            logger.info(f"Attempting to save data to: {filepath.absolute()}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Successfully saved data to: {filepath.absolute()}")
            logger.info(f"File size: {filepath.stat().st_size} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data to {filename}: {str(e)}", exc_info=True)
            return False
    
    def _submit_to_agencyzoom(self, quote_data: Dict) -> Optional[Dict]:
        """Submit quote data to AgencyZoom as a lead.
        
        Args:
            quote_data: The quote request data dictionary
            
        Returns:
            AgencyZoom response dictionary or None if failed
        """
        if not self.agencyzoom_service:
            logger.warning("AgencyZoom service not available")
            return None
        
        insurance_type = quote_data.get("insurance_type")
        insurance_key = f"{insurance_type}_insurance"
        insurance_data = quote_data.get(insurance_key, {})
        
        # Extract contact information based on insurance type
        first_name = ""
        last_name = ""
        email = ""
        phone = ""
        
        if insurance_type == "home":
            full_name = insurance_data.get("primary_insured", {}).get("full_name", "")
            if full_name:
                name_parts = full_name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            contact_info = insurance_data.get("contact", {})
            email = contact_info.get("email", "")
            phone = contact_info.get("phone", "")
            
        elif insurance_type == "auto":
            drivers = insurance_data.get("drivers", [])
            if drivers:
                full_name = drivers[0].get("full_name", "")
                if full_name:
                    name_parts = full_name.split(" ", 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
            contact_info = insurance_data.get("contact", {})
            email = contact_info.get("email", "")
            phone = contact_info.get("phone", "")
            
        elif insurance_type == "flood":
            full_name = insurance_data.get("full_name", "")
            if full_name:
                name_parts = full_name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            email = insurance_data.get("email", "")
            phone = insurance_data.get("phone", "")
            
        elif insurance_type == "life":
            full_name = insurance_data.get("insured", {}).get("full_name", "")
            if full_name:
                name_parts = full_name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            contact_info = insurance_data.get("contact", {})
            email = contact_info.get("email", "")
            phone = contact_info.get("phone", "")
            
        elif insurance_type == "commercial":
            business_name = insurance_data.get("business", {}).get("name", "")
            first_name = business_name
            last_name = ""
            contact_info = insurance_data.get("contact", {})
            email = contact_info.get("email", "")
            phone = contact_info.get("phone", "")
        
        # Prepare lead data for AgencyZoom
        lead_data = {
            "first_name": first_name or "Unknown",
            "last_name": last_name,
            "email": email or "noemail@pending.com",
            "phone": phone,
            "insurance_type": insurance_type,
            "source": "AI Voice Agent",
            "notes": f"Quote submitted via AI agent. Session: {self.session_id}",
            "insurance_details": insurance_data
        }
        
        # Add type-specific fields
        if insurance_type == "home":
            property_addr = insurance_data.get("property", {}).get("address", {})
            lead_data["property_address"] = f"{property_addr.get('streetAddress', '')}, {property_addr.get('city', '')}, {property_addr.get('state', '')} {property_addr.get('zip_code', '')}"
            lead_data["current_provider"] = insurance_data.get("current_policy", {}).get("current_provider", "")
        elif insurance_type == "auto":
            vehicles = insurance_data.get("vehicles", [])
            if vehicles:
                lead_data["vehicle_info"] = f"{vehicles[0].get('make', '')} {vehicles[0].get('model', '')}"
            lead_data["current_provider"] = insurance_data.get("current_policy", {}).get("current_provider", "")
        elif insurance_type == "flood":
            home_addr = insurance_data.get("home_address", {})
            lead_data["home_address"] = f"{home_addr.get('streetAddress', '')}, {home_addr.get('city', '')}, {home_addr.get('state', '')} {home_addr.get('zip_code', '')}"
        elif insurance_type == "life":
            life_addr = insurance_data.get("address", {})
            lead_data["address"] = f"{life_addr.get('streetAddress', '')}, {life_addr.get('city', '')}, {life_addr.get('state', '')} {life_addr.get('zip_code', '')}"
            lead_data["appointment_requested"] = insurance_data.get("appointment_requested", False)
        elif insurance_type == "commercial":
            lead_data["business_name"] = insurance_data.get("business", {}).get("name", "")
            business_addr = insurance_data.get("business", {}).get("address", {})
            lead_data["business_address"] = f"{business_addr.get('streetAddress', '')}, {business_addr.get('city', '')}, {business_addr.get('state', '')} {business_addr.get('zip_code', '')}"
        
        # Submit to AgencyZoom
        return self.agencyzoom_service.create_lead(lead_data)
    
    def set_user_action(self, action_type: str, insurance_type: str) -> str:
        """Set the user action type and insurance type.
        
        Args:
            action_type: Either "add" or "update"
            insurance_type: Type of insurance
            
        Returns:
            Confirmation message
        """
        if action_type not in ["add", "update"]:
            return "Invalid action type. Please specify 'add' or 'update'."
        
        if insurance_type not in ["home", "auto", "flood", "life", "commercial"]:
            return "Invalid insurance type. Please choose from: home, auto, flood, life, or commercial."
        
        self.user_action = action_type
        self.insurance_type = insurance_type
        self.collected_data = {"action": action_type, "insurance_type": insurance_type}
        
        logger.info(f"User action set: {action_type}, Insurance type: {insurance_type}")
        
        return f"Great! I'll help you {action_type} {insurance_type} insurance. Let me collect the necessary information from you."
    
    def collect_home_insurance(
        self,
        full_name: str,
        date_of_birth: str,
        phone: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: str,
        email: str,
        current_provider: Optional[str] = None,
        spouse_name: Optional[str] = None,
        spouse_dob: Optional[str] = None,
        has_solar_panels: bool = False,
        has_pool: bool = False,
        roof_age: int = 0,
        has_pets: bool = False,
        renewal_date: Optional[str] = None,
        renewal_premium: Optional[float] = None
    ) -> str:
        """Collect and validate home insurance data.
        
        Returns:
            Confirmation message or error
        """
        try:
            logger.info(f"Collecting home insurance data for: {full_name}")
            
            primary_insured = Person(
                full_name=full_name,
                date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            )
            
            spouse = None
            if spouse_name and spouse_dob:
                spouse = Person(
                    full_name=spouse_name,
                    date_of_birth=datetime.strptime(spouse_dob, "%Y-%m-%d").date()
                )
            
            address = Address(
                streetAddress=street_address,
                city=city,
                state=state,
                country=country,
                zip_code=zip_code
            )
            
            property_details = PropertyDetails(
                address=address,
                has_solar_panels=has_solar_panels,
                has_pool=has_pool,
                roof_age=roof_age
            )
            
            policy_info = PolicyInfo(
                current_provider=current_provider,
                renewal_date=datetime.strptime(renewal_date, "%Y-%m-%d").date() if renewal_date else None,
                renewal_premium=renewal_premium
            )
            
            contact = ContactInfo(phone=phone, email=email)
            
            home_insurance = HomeInsurance(
                primary_insured=primary_insured,
                spouse=spouse,
                property=property_details,
                has_pets=has_pets,
                current_policy=policy_info,
                contact=contact
            )
            
            self.collected_data["home_insurance"] = home_insurance.model_dump()
            logger.info(f"Home insurance data collected: {json.dumps(self.collected_data['home_insurance'], default=str)}")
            
            # Save to JSON file
            filename = f"home_insurance_{self.session_id}_{full_name.replace(' ', '_')}.json"
            save_success = self._save_to_json(self.collected_data, filename)
            
            if save_success:
                logger.info(f"Home insurance data saved successfully to {filename}")
                return "Perfect! I've collected all your home insurance information. Your quote request is ready to be submitted."
            else:
                logger.warning(f"Home insurance data collected but failed to save to file")
                return "I've collected your home insurance information, but there was an issue saving it. The data is still stored and can be submitted."
            
        except Exception as e:
            logger.error(f"Error collecting home insurance data: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please verify the information and try again."
    
    def collect_auto_insurance(
        self,
        driver_name: str,
        driver_dob: str,
        phone: str,
        license_number: str,
        vin: str,
        vehicle_make: str,
        vehicle_model: str,
        coverage_type: str = "full",
        email: Optional[str] = "",
        qualification: str = "Unknown",
        profession: str = "Unknown",
        gpa: Optional[float] = None,
        current_provider: Optional[str] = None,
        renewal_date: Optional[str] = None,
        renewal_premium: Optional[float] = None
    ) -> str:
        """Collect and validate auto insurance data.
        
        Returns:
            Confirmation message or error
        """
        try:
            logger.info(f"Collecting auto insurance data for: {driver_name}")
            
            driver = Driver(
                full_name=driver_name,
                date_of_birth=datetime.strptime(driver_dob, "%Y-%m-%d").date(),
                license_number=license_number,
                qualification=qualification,
                profession=profession,
                gpa=gpa
            )
            
            vehicle = Vehicle(
                vin=vin,
                make=vehicle_make,
                model=vehicle_model,
                coverage_type=CoverageType(coverage_type)
            )
            
            policy_info = PolicyInfo(
                current_provider=current_provider,
                renewal_date=datetime.strptime(renewal_date, "%Y-%m-%d").date() if renewal_date else None,
                renewal_premium=renewal_premium
            )
            
            contact = ContactInfo(phone=phone, email=email)
            
            auto_insurance = AutoInsurance(
                drivers=[driver],
                vehicles=[vehicle],
                current_policy=policy_info,
                contact=contact
            )
            
            self.collected_data["auto_insurance"] = auto_insurance.model_dump()
            logger.info(f"Auto insurance data collected: {json.dumps(self.collected_data['auto_insurance'], default=str)}")
            
            # Save to JSON file
            filename = f"auto_insurance_{self.session_id}_{driver_name.replace(' ', '_')}.json"
            save_success = self._save_to_json(self.collected_data, filename)
            
            if save_success:
                logger.info(f"Auto insurance data saved successfully to {filename}")
                return "Excellent! I've collected all your auto insurance information. Your quote request is ready to be submitted."
            else:
                logger.warning(f"Auto insurance data collected but failed to save to file")
                return "I've collected your auto insurance information, but there was an issue saving it. The data is still stored and can be submitted."
            
        except Exception as e:
            logger.error(f"Error collecting auto insurance data: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please verify the information and try again."
    
    def collect_flood_insurance(
        self,
        full_name: str,
        email: str,
        phone: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: str
    ) -> str:
        """Collect and validate flood insurance data.
        
        Returns:
            Confirmation message or error
        """
        try:
            logger.info(f"Collecting flood insurance data for: {full_name}")
            
            address = Address(
                streetAddress=street_address,
                city=city,
                state=state,
                country=country,
                zip_code=zip_code
            )
            
            flood_insurance = FloodInsurance(
                home_address=address,
                full_name=full_name,
                phone=phone,
                email=email
            )
            
            self.collected_data["flood_insurance"] = flood_insurance.model_dump()
            logger.info(f"Flood insurance data collected: {json.dumps(self.collected_data['flood_insurance'])}")
            
            # Save to JSON file
            filename = f"flood_insurance_{self.session_id}_{full_name.replace(' ', '_')}.json"
            save_success = self._save_to_json(self.collected_data, filename)
            
            if save_success:
                logger.info(f"Flood insurance data saved successfully to {filename}")
                return "Perfect! I've collected all your flood insurance information. Your quote request is ready to be submitted."
            else:
                logger.warning(f"Flood insurance data collected but failed to save to file")
                return "I've collected your flood insurance information, but there was an issue saving it. The data is still stored and can be submitted."
            
        except Exception as e:
            logger.error(f"Error collecting flood insurance data: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please verify the information and try again."
    
    def collect_life_insurance(
        self,
        full_name: str,
        date_of_birth: str,
        phone: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: str,
        email: Optional[str] = "",
        appointment_requested: bool = False,
        appointment_date: Optional[str] = None,
        policy_type: Optional[str] = None
    ) -> str:
        """Collect and validate life insurance data.
        
        Returns:
            Confirmation message or error
        """
        try:
            logger.info(f"Collecting life insurance data for: {full_name}")
            
            insured = Person(
                full_name=full_name,
                date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            )
            
            address = Address(
                streetAddress=street_address,
                city=city,
                state=state,
                country=country,
                zip_code=zip_code
            )
            
            contact = ContactInfo(phone=phone, email=email or "noemail@pending.com")
            
            appt_datetime = None
            if appointment_date:
                appt_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
            
            life_insurance = LifeInsurance(
                insured=insured,
                address=address,
                appointment_requested=appointment_requested,
                appointment_date=appt_datetime,
                contact=contact,
                policy_type=PolicyType(policy_type) if policy_type else None
            )
            
            self.collected_data["life_insurance"] = life_insurance.model_dump()
            logger.info(f"Life insurance data collected: {json.dumps(self.collected_data['life_insurance'], default=str)}")
            
            # Save to JSON file
            filename = f"life_insurance_{self.session_id}_{full_name.replace(' ', '_')}.json"
            save_success = self._save_to_json(self.collected_data, filename)
            
            if save_success:
                logger.info(f"Life insurance data saved successfully to {filename}")
                return "Great! I've collected all your life insurance information. Your quote request is ready to be submitted."
            else:
                logger.warning(f"Life insurance data collected but failed to save to file")
                return "I've collected your life insurance information, but there was an issue saving it. The data is still stored and can be submitted."
            
        except Exception as e:
            logger.error(f"Error collecting life insurance data: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please verify the information and try again."
    
    def collect_commercial_insurance(
        self,
        business_name: str,
        phone: str,
        street_address: str,
        city: str,
        state: str,
        country: str,
        zip_code: str,
        business_type: str = "General",
        inventory_limit: Optional[float] = None,
        building_coverage: bool = False,
        building_coverage_limit: Optional[float] = None,
        current_provider: Optional[str] = None,
        renewal_date: Optional[str] = None,
        renewal_premium: Optional[float] = None,
        email: Optional[str] = ""
    ) -> str:
        """Collect and validate commercial insurance data.
        
        Returns:
            Confirmation message or error
        """
        try:
            logger.info(f"Collecting commercial insurance data for: {business_name}")
            
            address = Address(
                streetAddress=street_address,
                city=city,
                state=state,
                country=country,
                zip_code=zip_code
            )
            
            business = BusinessDetails(
                name=business_name,
                type=business_type,
                address=address
            )
            
            coverage = CoverageDetails(
                inventory_limit=inventory_limit,
                building_coverage=building_coverage,
                building_coverage_limit=building_coverage_limit
            )
            
            policy_info = PolicyInfo(
                current_provider=current_provider,
                renewal_date=datetime.strptime(renewal_date, "%Y-%m-%d").date() if renewal_date else None,
                renewal_premium=renewal_premium
            )
            
            contact = ContactInfo(phone=phone, email=email or "noemail@pending.com")
            
            commercial_insurance = CommercialInsurance(
                business=business,
                coverage=coverage,
                current_policy=policy_info,
                contact=contact
            )
            
            self.collected_data["commercial_insurance"] = commercial_insurance.model_dump()
            logger.info(f"Commercial insurance data collected: {json.dumps(self.collected_data['commercial_insurance'], default=str)}")
            
            # Save to JSON file
            filename = f"commercial_insurance_{self.session_id}_{business_name.replace(' ', '_')}.json"
            save_success = self._save_to_json(self.collected_data, filename)
            
            if save_success:
                logger.info(f"Commercial insurance data saved successfully to {filename}")
                return "Excellent! I've collected all your commercial insurance information. Your quote request is ready to be submitted."
            else:
                logger.warning(f"Commercial insurance data collected but failed to save to file")
                return "I've collected your commercial insurance information, but there was an issue saving it. The data is still stored and can be submitted."
            
        except Exception as e:
            logger.error(f"Error collecting commercial insurance data: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please verify the information and try again."
    
    def submit_quote_request(self) -> str:
        """Submit the collected insurance quote request to Agency Zoom.
        
        Returns:
            Confirmation message with next steps
        """
        logger.info("=== SUBMIT QUOTE REQUEST CALLED ===")
        logger.info(f"Insurance type: {self.insurance_type}")
        logger.info(f"Collected data keys: {list(self.collected_data.keys())}")
        
        if not self.insurance_type:
            logger.warning("Submit called but no insurance type set")
            return "No insurance type has been set. Please start by telling me what type of insurance you need."
        
        insurance_key = f"{self.insurance_type}_insurance"
        if insurance_key not in self.collected_data:
            logger.warning(f"Submit called but {insurance_key} not in collected data")
            return f"I haven't collected the {self.insurance_type} insurance information yet. Please provide the required details first."
        
        try:
            logger.info(f"Creating quote request for {self.insurance_type}")
            
            # Create the quote request
            quote_data = {
                "insurance_type": self.insurance_type,
                insurance_key: self.collected_data[insurance_key]
            }
            
            quote_request = QuoteRequest(**quote_data)
            logger.info(f"Quote request object created successfully")
            
            # Save the final submitted quote to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            submission_filename = f"SUBMITTED_{self.insurance_type}_quote_{timestamp}.json"
            
            submission_data = {
                "submission_timestamp": timestamp,
                "session_id": self.session_id,
                "status": "submitted",
                "quote_request": quote_request.model_dump()
            }
            
            save_success = self._save_to_json(submission_data, submission_filename)
            
            if save_success:
                logger.info(f"✅ Quote request SUCCESSFULLY SAVED to: {submission_filename}")
            else:
                logger.error(f"❌ FAILED to save quote request to: {submission_filename}")
            
            # Log the quote submission
            logger.info(f"Quote request data: {json.dumps(quote_request.model_dump(), default=str)}")
            
            # Submit to AgencyZoom if service is available
            # Note: AgencyZoom submission is now handled by submit_collected_data_to_agencyzoom()
            # which provides more comprehensive data with proper address fields
            agencyzoom_submitted = False
            # if self.agencyzoom_service:
            #     try:
            #         logger.info("Attempting to submit to AgencyZoom...")
            #         agencyzoom_result = self._submit_to_agencyzoom(quote_request.model_dump())
            #         if agencyzoom_result:
            #             agencyzoom_submitted = True
            #             logger.info("✅ Successfully submitted to AgencyZoom")
            #         else:
            #             logger.warning("⚠️ AgencyZoom submission returned None")
            #     except Exception as az_error:
            #         logger.error(f"❌ AgencyZoom submission failed: {az_error}", exc_info=True)
            
            # Mark as submitted
            self.quote_submitted = True
            logger.info("Quote marked as submitted in service")
            
            logger.info("=== SUBMIT QUOTE REQUEST COMPLETED SUCCESSFULLY ===")
            
            response_msg = f"Perfect! Your {self.insurance_type} insurance quote request has been submitted successfully."
            # Note: CRM submission happens via submit_collected_data_to_agencyzoom()
            # if agencyzoom_submitted:
            #     response_msg += " Your information has been automatically added to our CRM system."
            response_msg += " Our team will review your information and contact you shortly with a personalized quote. Is there anything else I can help you with today?"
            
            return response_msg
            
        except Exception as e:
            logger.error(f"❌ Error submitting quote request: {str(e)}", exc_info=True)
            return f"I encountered an error submitting your request: {str(e)}. Please try again or speak with a representative."

