from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Literal
from datetime import date, datetime
from enum import Enum


# ===========================
# ENUMS
# ===========================

class CoverageType(str, Enum):
    LIABILITY = "liability"
    FULL = "full"


class PolicyType(str, Enum):
    TERM = "term"
    WHOLE = "whole"
    UNIVERSAL = "universal"
    ANNUITY = "annuity"
    LONG_TERM_CARE = "long_term_care"


class DocumentType(str, Enum):
    POLICY = "policy"
    DECLARATIONS_PAGE = "declarations_page"
    CERTIFICATE_OF_INSURANCE = "certificate_of_insurance"
    RENEWAL_COPY = "renewal_copy"


class UpdateType(str, Enum):
    ADD_VEHICLE = "add_vehicle"
    REMOVE_VEHICLE = "remove_vehicle"
    ADD_DRIVER = "add_driver"
    REMOVE_DRIVER = "remove_driver"
    UPDATE_MORTGAGEE = "update_mortgagee"


# ===========================
# SHARED/COMMON MODELS
# ===========================

class Address(BaseModel):
    streetAddress: str = Field(..., description="Street address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    country: str = Field(..., description="Country")
    zip_code: str = Field(..., description="ZIP or postal code")


class ContactInfo(BaseModel):
    phone: str = Field(..., description="Best phone number to reach")
    email: EmailStr = Field(..., description="Email address")


class Person(BaseModel):
    full_name: str = Field(..., description="Full legal name")
    date_of_birth: date = Field(..., description="Date of birth")


class PolicyInfo(BaseModel):
    current_provider: Optional[str] = Field(None, description="Current insurance provider")
    renewal_date: Optional[date] = Field(None, description="Policy renewal date")
    renewal_premium: Optional[float] = Field(None, description="Renewal offer/premium amount")


# ===========================
# HOME INSURANCE MODEL
# ===========================

class PropertyDetails(BaseModel):
    address: Address = Field(..., description="Property address")
    has_solar_panels: bool = Field(False, description="Does property have solar panels?")
    has_pool: bool = Field(False, description="Does property have a pool?")
    roof_age: int = Field(0, ge=0, description="Age of roof in years")


class HomeInsurance(BaseModel):
    # Primary Insured
    primary_insured: Person = Field(..., description="Primary insured person")
    
    # Spouse (if applicable)
    spouse: Optional[Person] = Field(None, description="Spouse information if applicable")
    
    # Property Details
    property: PropertyDetails = Field(..., description="Property details")
    
    # Additional Info
    has_pets: bool = Field(..., description="Does the insured have pets?")
    
    # Current Policy
    current_policy: PolicyInfo = Field(..., description="Current policy information")
    
    # Contact
    contact: ContactInfo = Field(..., description="Contact information")

    class Config:
        json_schema_extra = {
            "example": {
                "primary_insured": {
                    "full_name": "John Doe",
                    "date_of_birth": "1980-05-15"
                },
                "spouse": {
                    "full_name": "Jane Doe",
                    "date_of_birth": "1982-08-20"
                },
                "property": {
                    "address": {
                        "streetAddress": "123 Main St",
                        "city": "Anytown",
                        "state": "ST",
                        "country": "USA",
                        "zip_code": "12345"
                    },
                    "has_solar_panels": True,
                    "has_pool": False,
                    "roof_age": 5
                },
                "has_pets": True,
                "current_policy": {
                    "current_provider": "ABC Insurance",
                    "renewal_date": "2025-12-31",
                    "renewal_premium": 1500.00
                },
                "contact": {
                    "phone": "555-123-4567",
                    "email": "john.doe@example.com"
                }
            }
        }


# ===========================
# AUTO INSURANCE MODEL
# ===========================

class Driver(Person):
    license_number: str = Field(..., description="Driver's license number")
    qualification: str = Field(..., description="Educational qualification")
    profession: str = Field(..., description="Current profession")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA for drivers under 21")

    @validator('gpa')
    def validate_gpa(cls, v, values):
        if v is not None and (v < 0.0 or v > 4.0):
            raise ValueError('GPA must be between 0.0 and 4.0')
        return v


class Vehicle(BaseModel):
    vin: str = Field(..., min_length=17, max_length=17, description="Vehicle Identification Number")
    make: str = Field(..., description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model")
    coverage_type: CoverageType = Field(..., description="Type of coverage desired")

    @validator('vin')
    def validate_vin(cls, v):
        if len(v) != 17:
            raise ValueError('VIN must be exactly 17 characters')
        return v.upper()


class AutoInsurance(BaseModel):
    # Drivers
    drivers: List[Driver] = Field(..., min_items=1, description="List of all drivers")
    
    # Vehicles
    vehicles: List[Vehicle] = Field(..., min_items=1, description="List of all vehicles")
    
    # Current Policy
    current_policy: PolicyInfo = Field(..., description="Current policy information")
    
    # Contact
    contact: ContactInfo = Field(..., description="Contact information")

    class Config:
        json_schema_extra = {
            "example": {
                "drivers": [
                    {
                        "full_name": "John Doe",
                        "date_of_birth": "1980-05-15",
                        "license_number": "D1234567",
                        "qualification": "Bachelor's Degree",
                        "profession": "Engineer"
                    }
                ],
                "vehicles": [
                    {
                        "vin": "1HGBH41JXMN109186",
                        "make": "Honda",
                        "model": "Accord",
                        "coverage_type": "full"
                    }
                ],
                "current_policy": {
                    "current_provider": "XYZ Auto Insurance",
                    "renewal_date": "2025-12-31",
                    "renewal_premium": 1200.00
                },
                "contact": {
                    "phone": "555-123-4567",
                    "email": "john.doe@example.com"
                }
            }
        }


# ===========================
# FLOOD INSURANCE MODEL
# ===========================

class FloodInsurance(BaseModel):
    home_address: Address = Field(..., description="Home address for flood insurance")
    full_name: str = Field(..., description="Full name of insured")
    phone: str = Field(..., description="Phone number")
    email: EmailStr = Field(..., description="Email address")

    class Config:
        json_schema_extra = {
            "example": {
                "home_address": {
                    "streetAddress": "456 River Rd",
                    "city": "Floodville",
                    "state": "ST",
                    "country": "USA",
                    "zip_code": "54321"
                },
                "full_name": "Jane Smith",
                "phone": "555-123-4567",
                "email": "jane.smith@example.com"
            }
        }


# ===========================
# LIFE INSURANCE MODEL
# ===========================

class LifeInsurance(BaseModel):
    insured: Person = Field(..., description="Insured person")
    address: Address = Field(..., description="Insured person's address")
    appointment_requested: bool = Field(..., description="Is appointment requested?")
    appointment_date: Optional[datetime] = Field(None, description="Appointment date and time")
    contact: ContactInfo = Field(..., description="Contact information")
    policy_type: Optional[PolicyType] = Field(None, description="Type of life insurance policy")

    class Config:
        json_schema_extra = {
            "example": {
                "insured": {
                    "full_name": "Robert Johnson",
                    "date_of_birth": "1975-03-10"
                },
                "address": {
                    "streetAddress": "789 Oak Ave",
                    "city": "Springfield",
                    "state": "IL",
                    "country": "USA",
                    "zip_code": "62701"
                },
                "appointment_requested": True,
                "appointment_date": "2025-12-01T10:00:00",
                "contact": {
                    "phone": "555-987-6543",
                    "email": "robert.johnson@example.com"
                },
                "policy_type": "term"
            }
        }


# ===========================
# COMMERCIAL INSURANCE MODEL
# ===========================

class BusinessDetails(BaseModel):
    name: str = Field(..., description="Business legal name")
    type: str = Field(..., description="Type of business")
    address: Address = Field(..., description="Business address")


class CoverageDetails(BaseModel):
    inventory_limit: Optional[float] = Field(None, ge=0, description="Inventory coverage limit")
    building_coverage: bool = Field(..., description="Does business need building coverage?")
    building_coverage_limit: Optional[float] = Field(None, ge=0, description="Building coverage limit")

    @validator('building_coverage_limit')
    def validate_building_limit(cls, v, values):
        if values.get('building_coverage') and v is None:
            raise ValueError('Building coverage limit required when building coverage is True')
        return v


class CommercialInsurance(BaseModel):
    # Business Details
    business: BusinessDetails = Field(..., description="Business information")
    
    # Coverage Details
    coverage: CoverageDetails = Field(..., description="Coverage requirements")
    
    # Current Policy
    current_policy: PolicyInfo = Field(..., description="Current policy information")
    
    # Contact
    contact: ContactInfo = Field(..., description="Contact information")

    class Config:
        json_schema_extra = {
            "example": {
                "business": {
                    "name": "ABC Corporation",
                    "type": "Retail Store",
                    "address": {
                        "streetAddress": "789 Business Blvd",
                        "city": "Commerce City",
                        "state": "ST",
                        "country": "USA",
                        "zip_code": "67890"
                    }
                },
                "coverage": {
                    "inventory_limit": 500000.00,
                    "building_coverage": True,
                    "building_coverage_limit": 1000000.00
                },
                "current_policy": {
                    "current_provider": "Business Insurance Co",
                    "renewal_date": "2026-01-15",
                    "renewal_premium": 5000.00
                },
                "contact": {
                    "phone": "555-111-2222",
                    "email": "contact@abccorp.com"
                }
            }
        }


# ===========================
# POLICY MANAGEMENT MODELS
# ===========================

class VehicleUpdate(BaseModel):
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    make: Optional[str] = None
    model: Optional[str] = None
    coverage_type: Optional[CoverageType] = None


class Mortgagee(BaseModel):
    name: str = Field(..., description="Mortgagee/lender name")
    address: str = Field(..., description="Mortgagee address")
    loan_number: str = Field(..., description="Loan account number")


class PolicyUpdateRequest(BaseModel):
    policy_number: str = Field(..., description="Policy number")
    client_name: str = Field(..., description="Client name for verification")
    update_type: UpdateType = Field(..., description="Type of update requested")
    
    # For vehicle changes
    vehicle: Optional[VehicleUpdate] = Field(None, description="Vehicle details for add/remove")
    
    # For driver changes
    driver: Optional[Driver] = Field(None, description="Driver details for add/remove")
    
    # For mortgagee updates
    mortgagee: Optional[Mortgagee] = Field(None, description="Mortgagee details for update")

    @validator('vehicle')
    def validate_vehicle_update(cls, v, values):
        if values.get('update_type') in [UpdateType.ADD_VEHICLE, UpdateType.REMOVE_VEHICLE] and v is None:
            raise ValueError('Vehicle details required for vehicle updates')
        return v

    @validator('driver')
    def validate_driver_update(cls, v, values):
        if values.get('update_type') in [UpdateType.ADD_DRIVER, UpdateType.REMOVE_DRIVER] and v is None:
            raise ValueError('Driver details required for driver updates')
        return v

    @validator('mortgagee')
    def validate_mortgagee_update(cls, v, values):
        if values.get('update_type') == UpdateType.UPDATE_MORTGAGEE and v is None:
            raise ValueError('Mortgagee details required for mortgagee update')
        return v


class DocumentRequest(BaseModel):
    policy_number: str = Field(..., description="Policy number")
    client_name: str = Field(..., description="Client name for verification")
    document_type: DocumentType = Field(..., description="Type of document requested")
    delivery_email: Optional[EmailStr] = Field(None, description="Email to send document to")

    class Config:
        json_schema_extra = {
            "example": {
                "policy_number": "POL-12345",
                "client_name": "John Doe",
                "document_type": "declarations_page",
                "delivery_email": "john.doe@example.com"
            }
        }


# ===========================
# QUOTE REQUEST MODEL
# ===========================

class QuoteRequest(BaseModel):
    insurance_type: Literal["home", "auto", "flood", "life", "commercial"] = Field(
        ..., description="Type of insurance quote requested"
    )
    home_insurance: Optional[HomeInsurance] = None
    auto_insurance: Optional[AutoInsurance] = None
    flood_insurance: Optional[FloodInsurance] = None
    life_insurance: Optional[LifeInsurance] = None
    commercial_insurance: Optional[CommercialInsurance] = None

    @validator('home_insurance')
    def validate_home(cls, v, values):
        if values.get('insurance_type') == 'home' and v is None:
            raise ValueError('Home insurance details required for home insurance quotes')
        return v

    @validator('auto_insurance')
    def validate_auto(cls, v, values):
        if values.get('insurance_type') == 'auto' and v is None:
            raise ValueError('Auto insurance details required for auto insurance quotes')
        return v

    @validator('flood_insurance')
    def validate_flood(cls, v, values):
        if values.get('insurance_type') == 'flood' and v is None:
            raise ValueError('Flood insurance details required for flood insurance quotes')
        return v

    @validator('life_insurance')
    def validate_life(cls, v, values):
        if values.get('insurance_type') == 'life' and v is None:
            raise ValueError('Life insurance details required for life insurance quotes')
        return v

    @validator('commercial_insurance')
    def validate_commercial(cls, v, values):
        if values.get('insurance_type') == 'commercial' and v is None:
            raise ValueError('Commercial insurance details required for commercial insurance quotes')
        return v


# ===========================
# TWILIO SMS MODELS
# ===========================

class SMSRequest(BaseModel):
    """Request model for sending SMS."""
    body: str = Field(..., description="The message content to send")
    number: str = Field(..., description="The recipient's phone number (with country code, e.g., +1234567890)")

    class Config:
        json_schema_extra = {
            "example": {
                "body": "Your insurance quote is ready!",
                "number": "+11234567890"
            }
        }


class SMSResponse(BaseModel):
    """Response model for SMS sending."""
    status: str = Field(..., description="Status of the SMS operation")
    message: str = Field(..., description="Human-readable message about the operation")
    message_sid: str = Field(..., description="Twilio message SID for tracking")
    to_number: str = Field(..., description="Recipient phone number")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "SMS sent successfully to +11234567890",
                "message_sid": "SM1234567890abcdef1234567890abcdef",
                "to_number": "+11234567890"
            }
        }


class MessageStatusResponse(BaseModel):
    """Response model for message status."""
    status: str = Field(..., description="Delivery status (queued, sending, sent, failed, delivered, undelivered)")
    message_sid: str = Field(..., description="Unique message SID")
    to_number: str = Field(..., description="Recipient phone number")
    from_number: str = Field(..., description="Sender phone number")
    body: str = Field(..., description="Message content")
    date_sent: Optional[str] = Field(None, description="When the message was sent")
    date_updated: Optional[str] = Field(None, description="Last update time")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    price: Optional[str] = Field(None, description="Cost of the message")
    direction: str = Field(..., description="Message direction (outbound-api, inbound)")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "delivered",
                "message_sid": "SM1234567890abcdef1234567890abcdef",
                "to_number": "+11234567890",
                "from_number": "+10987654321",
                "body": "Your insurance quote is ready!",
                "date_sent": "2025-12-10 10:30:00",
                "date_updated": "2025-12-10 10:30:05",
                "error_code": None,
                "error_message": None,
                "price": "-0.00750",
                "direction": "outbound-api"
            }
        }


# ===========================
# EMAIL MODELS
# ===========================

class EmailRequest(BaseModel):
    """Request model for sending email."""
    receiver_email: EmailStr = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    is_html: Optional[bool] = Field(False, description="Whether the body is HTML format")

    class Config:
        json_schema_extra = {
            "example": {
                "receiver_email": "client@example.com",
                "subject": "Your Insurance Quote is Ready",
                "body": "Dear valued customer, your insurance quote has been prepared and is ready for review.",
                "is_html": False
            }
        }


class EmailResponse(BaseModel):
    """Response model for email sending."""
    status: str = Field(..., description="Status of the email operation")
    message: str = Field(..., description="Human-readable message about the operation")
    receiver_email: str = Field(..., description="Recipient email address")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Email sent successfully to client@example.com",
                "receiver_email": "client@example.com"
            }
        }


class OutboundCallRequest(BaseModel):
    """Request model for initiating an outbound call."""
    phone_number: str
    name: Optional[str] = None
    dynamic_instruction: Optional[str] = None
    language: Optional[str] = "en"  # TTS language (e.g., "en", "es", "fr")
    voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs voice ID (default: Rachel)
    sip_trunk_id: Optional[str] = None  # SIP trunk ID (uses env variable if not provided)
    transfer_to: Optional[str] = None  # Phone number to transfer to (e.g., +1234567890)
    escalation_condition: Optional[str] = None  # Condition when to escalate/transfer the call
    provider: Optional[str] = "openai"  # LLM provider ("openai" or "gemini")
    api_key: Optional[str] = None  # Custom API key for the provider

class StatusResponse(BaseModel):
    """Generic status response model used across multiple endpoints."""
    status: str
    message: str
    details: Optional[dict] = None
    transcript: Optional[dict] = None  # Added for call transcripts