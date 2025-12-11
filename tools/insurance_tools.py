"""Insurance data collection tools for the telephony agent."""

import logging
import json
from typing import Optional
from datetime import datetime
from livekit.agents import function_tool, RunContext

from services.insurance_service import InsuranceService

logger = logging.getLogger("telephony-agent")


class InsuranceTools:
    """Tools for collecting insurance information from callers."""
    
    def __init__(self, insurance_service: InsuranceService):
        """Initialize insurance tools with a service instance.
        
        Args:
            insurance_service: The insurance service for data handling
        """
        self.service = insurance_service
    
    @function_tool()
    async def set_user_action(
        self,
        context: RunContext,
        action_type: str,
        insurance_type: str
    ) -> str:
        """Set the user action type (add/update) and insurance type.
        
        Args:
            action_type: Either "add" for new insurance or "update" for existing policy
            insurance_type: Type of insurance - "home", "auto", "flood", "life", or "commercial"
            
        Returns:
            Confirmation message with next steps
        """
        logger.info(f"🔧 TOOL CALLED: set_user_action(action_type={action_type}, insurance_type={insurance_type})")
        result = self.service.set_user_action(action_type, insurance_type)
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result
    
    @function_tool()
    async def collect_home_insurance_data(
        self,
        context: RunContext,
        full_name: str,
        date_of_birth: str,
        spouse_name: Optional[str] = None,
        spouse_dob: Optional[str] = None,
        property_address: str = "",
        has_solar_panels: bool = False,
        has_pool: bool = False,
        roof_age: int = 0,
        has_pets: bool = False,
        current_provider: Optional[str] = None,
        renewal_date: Optional[str] = None,
        renewal_premium: Optional[float] = None,
        phone: str = "",
        email: str = ""
    ) -> str:
        """Collect home insurance information from the caller.
        
        Args:
            full_name: Full legal name of primary insured
            date_of_birth: Date of birth (YYYY-MM-DD format)
            spouse_name: Spouse's full name (if applicable)
            spouse_dob: Spouse's date of birth (YYYY-MM-DD format)
            property_address: Full property address
            has_solar_panels: Does property have solar panels?
            has_pool: Does property have a pool?
            roof_age: Age of roof in years
            has_pets: Does the insured have pets?
            current_provider: Current insurance provider name
            renewal_date: Current policy renewal date (YYYY-MM-DD)
            renewal_premium: Current renewal premium amount
            phone: Best phone number to reach
            email: Email address
            
        Returns:
            Confirmation message
        """
        logger.info(f"🔧 TOOL CALLED: collect_home_insurance_data(full_name={full_name})")
        result = self.service.collect_home_insurance(
            full_name=full_name,
            date_of_birth=date_of_birth,
            spouse_name=spouse_name,
            spouse_dob=spouse_dob,
            property_address=property_address,
            has_solar_panels=has_solar_panels,
            has_pool=has_pool,
            roof_age=roof_age,
            has_pets=has_pets,
            current_provider=current_provider,
            renewal_date=renewal_date,
            renewal_premium=renewal_premium,
            phone=phone,
            email=email
        )
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result
    
    @function_tool()
    async def collect_auto_insurance_data(
        self,
        context: RunContext,
        driver_name: str,
        driver_dob: str,
        license_number: str,
        qualification: str,
        profession: str,
        gpa: Optional[float] = None,
        vin: str = "",
        vehicle_make: str = "",
        vehicle_model: str = "",
        coverage_type: str = "full",
        current_provider: Optional[str] = None,
        renewal_date: Optional[str] = None,
        renewal_premium: Optional[float] = None,
        phone: str = "",
        email: str = ""
    ) -> str:
        """Collect auto insurance information from the caller.
        
        Args:
            driver_name: Full legal name of driver
            driver_dob: Driver's date of birth (YYYY-MM-DD)
            license_number: Driver's license number
            qualification: Educational qualification
            profession: Current profession
            gpa: GPA for drivers under 21 (0.0-4.0)
            vin: Vehicle Identification Number (17 characters)
            vehicle_make: Vehicle manufacturer
            vehicle_model: Vehicle model
            coverage_type: Type of coverage - "liability" or "full"
            current_provider: Current insurance provider
            renewal_date: Current policy renewal date (YYYY-MM-DD)
            renewal_premium: Current renewal premium amount
            phone: Best phone number to reach
            email: Email address
            
        Returns:
            Confirmation message
        """
        logger.info(f"🔧 TOOL CALLED: collect_auto_insurance_data(driver_name={driver_name})")
        result = self.service.collect_auto_insurance(
            driver_name=driver_name,
            driver_dob=driver_dob,
            license_number=license_number,
            qualification=qualification,
            profession=profession,
            gpa=gpa,
            vin=vin,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            coverage_type=coverage_type,
            current_provider=current_provider,
            renewal_date=renewal_date,
            renewal_premium=renewal_premium,
            phone=phone,
            email=email
        )
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result
    
    @function_tool()
    async def collect_flood_insurance_data(
        self,
        context: RunContext,
        full_name: str,
        home_address: str,
        email: str
    ) -> str:
        """Collect flood insurance information from the caller.
        
        Args:
            full_name: Full name of insured
            home_address: Home address for flood insurance
            email: Email address
            
        Returns:
            Confirmation message
        """
        logger.info(f"🔧 TOOL CALLED: collect_flood_insurance_data(full_name={full_name}, home_address={home_address}, email={email})")
        result = self.service.collect_flood_insurance(
            full_name=full_name,
            home_address=home_address,
            email=email
        )
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result
    
    @function_tool()
    async def collect_life_insurance_data(
        self,
        context: RunContext,
        full_name: str,
        date_of_birth: str,
        appointment_requested: bool,
        appointment_date: Optional[str] = None,
        phone: str = "",
        email: str = "",
        policy_type: Optional[str] = None
    ) -> str:
        """Collect life insurance information from the caller.
        
        Args:
            full_name: Full name of insured
            date_of_birth: Date of birth (YYYY-MM-DD)
            appointment_requested: Is appointment requested?
            appointment_date: Appointment date and time (YYYY-MM-DD HH:MM format)
            phone: Phone number
            email: Email address
            policy_type: Type of life insurance - "term", "whole", "universal", "annuity", or "long_term_care"
            
        Returns:
            Confirmation message
        """
        logger.info(f"🔧 TOOL CALLED: collect_life_insurance_data(full_name={full_name})")
        result = self.service.collect_life_insurance(
            full_name=full_name,
            date_of_birth=date_of_birth,
            appointment_requested=appointment_requested,
            appointment_date=appointment_date,
            phone=phone,
            email=email,
            policy_type=policy_type
        )
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result
    
    @function_tool()
    async def collect_commercial_insurance_data(
        self,
        context: RunContext,
        business_name: str,
        business_type: str,
        business_address: str,
        inventory_limit: Optional[float] = None,
        building_coverage: bool = False,
        building_coverage_limit: Optional[float] = None,
        current_provider: Optional[str] = None,
        renewal_date: Optional[str] = None,
        renewal_premium: Optional[float] = None,
        phone: str = "",
        email: str = ""
    ) -> str:
        """Collect commercial insurance information from the caller.
        
        Args:
            business_name: Business legal name
            business_type: Type of business
            business_address: Business address
            inventory_limit: Inventory coverage limit
            building_coverage: Does business need building coverage?
            building_coverage_limit: Building coverage limit
            current_provider: Current insurance provider
            renewal_date: Current policy renewal date (YYYY-MM-DD)
            renewal_premium: Current renewal premium amount
            phone: Phone number
            email: Email address
            
        Returns:
            Confirmation message
        """
        logger.info(f"🔧 TOOL CALLED: collect_commercial_insurance_data(business_name={business_name})")
        result = self.service.collect_commercial_insurance(
            business_name=business_name,
            business_type=business_type,
            business_address=business_address,
            inventory_limit=inventory_limit,
            building_coverage=building_coverage,
            building_coverage_limit=building_coverage_limit,
            current_provider=current_provider,
            renewal_date=renewal_date,
            renewal_premium=renewal_premium,
            phone=phone,
            email=email
        )
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result
    
    @function_tool()
    async def submit_quote_request(self, context: RunContext) -> str:
        """Submit the collected insurance quote request to Agency Zoom.
        
        Returns:
            Confirmation message with next steps
        """
        logger.info("🔧 TOOL CALLED: submit_quote_request()")
        result = self.service.submit_quote_request()
        logger.info(f"🔧 TOOL RESULT: {result}")
        return result

