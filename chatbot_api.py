"""Chatbot API endpoint with conversation memory."""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

from services.insurance_service import InsuranceService
from services.ams360 import AMS360Service
from services.agencyzoom import AgencyZoomService
from config import AGENT_SYSTEM_INSTRUCTIONS

load_dotenv()
logger = logging.getLogger("chatbot-api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Initialize FastAPI app
app = FastAPI(title="Insurance Chatbot API", version="1.0.0")

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# In-memory conversation storage (thread_id -> messages list)
# In production, you'd use a database like PostgreSQL, MongoDB, or Redis
conversation_threads: Dict[str, List[Dict]] = {}

# Store service instances per thread (for maintaining session state)
thread_services: Dict[str, Dict] = {}


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str
    thread_id: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    thread_id: str
    timestamp: str


def get_or_create_thread_services(thread_id: str) -> Dict:
    """Get or create service instances for a thread."""
    if thread_id not in thread_services:
        # Initialize services for this thread
        ams360_service = AMS360Service()
        agencyzoom_service = AgencyZoomService()
        insurance_service = InsuranceService(agencyzoom_service=agencyzoom_service)
        
        thread_services[thread_id] = {
            "insurance": insurance_service,
            "ams360": ams360_service,
            "agencyzoom": agencyzoom_service
        }
        logger.info(f"Created new service instances for thread: {thread_id}")
    
    return thread_services[thread_id]


def get_or_create_thread(thread_id: str) -> List[Dict]:
    """Get or create a conversation thread."""
    if thread_id not in conversation_threads:
        # Initialize with system message
        conversation_threads[thread_id] = [
            {
                "role": "system",
                "content": AGENT_SYSTEM_INSTRUCTIONS
            }
        ]
        logger.info(f"Created new conversation thread: {thread_id}")
    
    return conversation_threads[thread_id]


def get_available_tools() -> List[Dict]:
    """Define available function tools for the chatbot."""
    return [
        {
            "type": "function",
            "function": {
                "name": "set_user_action",
                "description": "Set the user action type (add/update) and insurance type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "enum": ["add", "update"],
                            "description": "Either 'add' for new insurance or 'update' for existing policy"
                        },
                        "insurance_type": {
                            "type": "string",
                            "enum": ["home", "auto", "flood", "life", "commercial"],
                            "description": "Type of insurance"
                        }
                    },
                    "required": ["action_type", "insurance_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "collect_home_insurance_data",
                "description": "Collect home insurance information from the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string", "description": "Full name of primary insured"},
                        "date_of_birth": {"type": "string", "description": "Date of birth (YYYY-MM-DD format)"},
                        "property_address": {"type": "string", "description": "Property address"},
                        "phone": {"type": "string", "description": "Phone number"},
                        "email": {"type": "string", "description": "Email address"},
                        "spouse_name": {"type": "string", "description": "Spouse name (optional)"},
                        "spouse_dob": {"type": "string", "description": "Spouse date of birth (YYYY-MM-DD format, optional)"},
                        "has_solar_panels": {"type": "boolean", "description": "Whether property has solar panels"},
                        "has_pool": {"type": "boolean", "description": "Whether property has a pool"},
                        "roof_age": {"type": "integer", "description": "Age of roof in years"},
                        "has_pets": {"type": "boolean", "description": "Whether household has pets"},
                        "current_provider": {"type": "string", "description": "Current insurance provider (optional)"},
                        "renewal_date": {"type": "string", "description": "Current policy renewal date (YYYY-MM-DD format, optional)"},
                        "renewal_premium": {"type": "number", "description": "Current renewal premium amount (optional)"}
                    },
                    "required": ["full_name", "date_of_birth", "property_address", "phone", "email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "collect_auto_insurance_data",
                "description": "Collect auto insurance information from the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "driver_name": {"type": "string", "description": "Full name of driver"},
                        "driver_dob": {"type": "string", "description": "Driver date of birth (YYYY-MM-DD format)"},
                        "license_number": {"type": "string", "description": "Driver's license number"},
                        "qualification": {"type": "string", "description": "Driver qualification"},
                        "profession": {"type": "string", "description": "Driver profession"},
                        "vin": {"type": "string", "description": "Vehicle VIN (17 characters)"},
                        "vehicle_make": {"type": "string", "description": "Vehicle make"},
                        "vehicle_model": {"type": "string", "description": "Vehicle model"},
                        "phone": {"type": "string", "description": "Phone number"},
                        "email": {"type": "string", "description": "Email address"},
                        "gpa": {"type": "number", "description": "GPA if driver under 21 (optional)"},
                        "coverage_type": {"type": "string", "description": "Coverage type - 'liability' or 'full'"},
                        "current_provider": {"type": "string", "description": "Current insurance provider (optional)"},
                        "renewal_date": {"type": "string", "description": "Current policy renewal date (YYYY-MM-DD format, optional)"},
                        "renewal_premium": {"type": "number", "description": "Current renewal premium amount (optional)"}
                    },
                    "required": ["driver_name", "driver_dob", "license_number", "qualification", "profession", "vin", "vehicle_make", "vehicle_model", "phone", "email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "collect_flood_insurance_data",
                "description": "Collect flood insurance information from the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string", "description": "Full name of insured"},
                        "home_address": {"type": "string", "description": "Home address for flood insurance"},
                        "email": {"type": "string", "description": "Email address"}
                    },
                    "required": ["full_name", "home_address", "email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "collect_life_insurance_data",
                "description": "Collect life insurance information from the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string", "description": "Full name of insured"},
                        "date_of_birth": {"type": "string", "description": "Date of birth (YYYY-MM-DD format)"},
                        "appointment_requested": {"type": "boolean", "description": "Whether customer wants an appointment"},
                        "phone": {"type": "string", "description": "Phone number"},
                        "email": {"type": "string", "description": "Email address"},
                        "appointment_date": {"type": "string", "description": "Requested appointment date and time (YYYY-MM-DD HH:MM format, optional)"},
                        "policy_type": {"type": "string", "description": "Type of policy - 'term', 'whole', 'universal', 'annuity', or 'long_term_care' (optional)"}
                    },
                    "required": ["full_name", "date_of_birth", "appointment_requested", "phone", "email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "collect_commercial_insurance_data",
                "description": "Collect commercial insurance information from the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "business_name": {"type": "string", "description": "Name of the business"},
                        "business_type": {"type": "string", "description": "Type of business"},
                        "business_address": {"type": "string", "description": "Business address"},
                        "phone": {"type": "string", "description": "Phone number"},
                        "email": {"type": "string", "description": "Email address"},
                        "inventory_limit": {"type": "number", "description": "Inventory coverage limit (optional)"},
                        "building_coverage": {"type": "boolean", "description": "Whether building coverage is needed"},
                        "building_coverage_limit": {"type": "number", "description": "Building coverage limit (optional)"},
                        "current_provider": {"type": "string", "description": "Current insurance provider (optional)"},
                        "renewal_date": {"type": "string", "description": "Current policy renewal date (YYYY-MM-DD format, optional)"},
                        "renewal_premium": {"type": "number", "description": "Current renewal premium amount (optional)"}
                    },
                    "required": ["business_name", "business_type", "business_address", "phone", "email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "submit_quote_request",
                "description": "Submit the collected insurance quote request.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "search_ams360_customer_by_phone",
        #         "description": "Search for a customer in AMS360 by phone number.",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "phone": {"type": "string", "description": "Phone number to search for"}
        #             },
        #             "required": ["phone"]
        #         }
        #     }
        # },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "search_ams360_customer_by_name",
        #         "description": "Search for a customer in AMS360 by name.",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "name": {"type": "string", "description": "Customer name or name prefix"}
        #             },
        #             "required": ["name"]
        #         }
        #     }
        # },
        {
            "type": "function",
            "function": {
                "name": "get_ams360_customer_policies",
                "description": "Get all policies for a specific customer from AMS360.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string", "description": "AMS360 customer ID"}
                    },
                    "required": ["customer_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_policy_by_number",
                "description": "Get policy information or lookup for existing policyby policy number from AMS360.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "policy_number": {"type": "string", "description": "The policy number to search for"}
                    },
                    "required": ["policy_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_agencyzoom_lead",
                "description": "Create a new lead in AgencyZoom with detailed information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "insurance_type": {"type": "string"},
                        "notes": {"type": "string"},
                        "address": {"type": "string"},
                        "date_of_birth": {"type": "string"},
                        "current_provider": {"type": "string"},
                        "vehicle_info": {"type": "string"},
                        "property_info": {"type": "string"},
                        "business_name": {"type": "string"},
                        "appointment_requested": {"type": "boolean"}
                    },
                    "required": ["first_name", "last_name", "email", "phone", "insurance_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_agencyzoom_contact_by_phone",
                "description": "Search for a contact in AgencyZoom by phone number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone": {"type": "string", "description": "Phone number to search for"}
                    },
                    "required": ["phone"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_agencyzoom_contact_by_email",
                "description": "Search for a contact in AgencyZoom by email address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address to search for"}
                    },
                    "required": ["email"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "submit_collected_data_to_agencyzoom",
                "description": "Submit all collected insurance data to AgencyZoom as a comprehensive lead.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]


def execute_function_call(function_name: str, arguments: Dict, thread_id: str) -> str:
    """Execute a function call and return the result."""
    services = get_or_create_thread_services(thread_id)
    insurance_service = services["insurance"]
    ams360_service = services["ams360"]
    agencyzoom_service = services["agencyzoom"]
    
    logger.info(f"🔧 Executing function: {function_name} with args: {arguments}")
    
    try:
        # Insurance Service Functions
        if function_name == "set_user_action":
            return insurance_service.set_user_action(
                arguments.get("action_type"),
                arguments.get("insurance_type")
            )
        
        elif function_name == "collect_home_insurance_data":
            return insurance_service.collect_home_insurance(
                full_name=arguments.get("full_name"),
                date_of_birth=arguments.get("date_of_birth"),
                spouse_name=arguments.get("spouse_name"),
                spouse_dob=arguments.get("spouse_dob"),
                property_address=arguments.get("property_address"),
                has_solar_panels=arguments.get("has_solar_panels", False),
                has_pool=arguments.get("has_pool", False),
                roof_age=arguments.get("roof_age", 0),
                has_pets=arguments.get("has_pets", False),
                current_provider=arguments.get("current_provider"),
                renewal_date=arguments.get("renewal_date"),
                renewal_premium=arguments.get("renewal_premium"),
                phone=arguments.get("phone"),
                email=arguments.get("email")
            )
        
        elif function_name == "collect_auto_insurance_data":
            return insurance_service.collect_auto_insurance(
                driver_name=arguments.get("driver_name"),
                driver_dob=arguments.get("driver_dob"),
                license_number=arguments.get("license_number"),
                qualification=arguments.get("qualification"),
                profession=arguments.get("profession"),
                gpa=arguments.get("gpa"),
                vin=arguments.get("vin"),
                vehicle_make=arguments.get("vehicle_make"),
                vehicle_model=arguments.get("vehicle_model"),
                coverage_type=arguments.get("coverage_type", "full"),
                current_provider=arguments.get("current_provider"),
                renewal_date=arguments.get("renewal_date"),
                renewal_premium=arguments.get("renewal_premium"),
                phone=arguments.get("phone"),
                email=arguments.get("email")
            )
        
        elif function_name == "collect_flood_insurance_data":
            return insurance_service.collect_flood_insurance(
                arguments.get("full_name"),
                arguments.get("home_address"),
                arguments.get("email")
            )
        
        elif function_name == "collect_life_insurance_data":
            return insurance_service.collect_life_insurance(
                full_name=arguments.get("full_name"),
                date_of_birth=arguments.get("date_of_birth"),
                appointment_requested=arguments.get("appointment_requested"),
                appointment_date=arguments.get("appointment_date"),
                phone=arguments.get("phone"),
                email=arguments.get("email"),
                policy_type=arguments.get("policy_type")
            )
        
        elif function_name == "collect_commercial_insurance_data":
            return insurance_service.collect_commercial_insurance(
                business_name=arguments.get("business_name"),
                business_type=arguments.get("business_type"),
                business_address=arguments.get("business_address"),
                inventory_limit=arguments.get("inventory_limit"),
                building_coverage=arguments.get("building_coverage", False),
                building_coverage_limit=arguments.get("building_coverage_limit"),
                current_provider=arguments.get("current_provider"),
                renewal_date=arguments.get("renewal_date"),
                renewal_premium=arguments.get("renewal_premium"),
                phone=arguments.get("phone"),
                email=arguments.get("email")
            )
        
        elif function_name == "submit_quote_request":
            return insurance_service.submit_quote_request()
        
        # AMS360 Functions
        elif function_name == "get_policy_by_number":
            result = ams360_service.get_policy_by_number(arguments.get("policy_number"))
            if result:
                # Extract policy details from the result
                policy_info = []
                try:
                    # Navigate the XML structure to extract key information
                    policy_result = result.get('s:Envelope', {}).get('s:Body', {}).get('PolicyGetResponse', {})
                    if not policy_result:
                        policy_result = result.get('Envelope', {}).get('Body', {}).get('PolicyGetResponse', {})
                    
                    policy_data = policy_result.get('PolicyGetResult', {}).get('a:Policy', {})
                    
                    if policy_data:
                        policy_number = policy_data.get('a:PolicyNumber', 'N/A')
                        customer_id = policy_data.get('a:CustomerId', 'N/A')
                        policy_type = policy_data.get('a:PolicyTypeOfBusiness', 'N/A')
                        effective_date = policy_data.get('a:PolicyEffectiveDate', 'N/A')
                        expiration_date = policy_data.get('a:PolicyExpirationDate', 'N/A')
                        full_term_premium = policy_data.get('a:FullTermPremium', 'N/A')
                        policy_status = policy_data.get('a:PolicyStatus', 'N/A')
                        
                        # Format dates nicely
                        if effective_date != 'N/A' and 'T' in effective_date:
                            effective_date = effective_date.split('T')[0]
                        if expiration_date != 'N/A' and 'T' in expiration_date:
                            expiration_date = expiration_date.split('T')[0]
                        
                        return f"Found policy {policy_number} in AMS360. Type: {policy_type}, Status: {policy_status}, Effective Date: {effective_date}, Expiration Date: {expiration_date}, Full Term Premium: ${full_term_premium}. Customer ID: {customer_id}. Policy details retrieved successfully."
                    else:
                        return f"Found policy information in AMS360 for policy number {arguments.get('policy_number')}. Policy data retrieved successfully."
                except Exception as e:
                    logger.warning(f"Error parsing policy details: {e}")
                    return f"Found policy information in AMS360 for policy number {arguments.get('policy_number')}. Policy data retrieved successfully."
            else:
                return f"No policy found in AMS360 with policy number {arguments.get('policy_number')}."
        
        elif function_name == "search_ams360_customer_by_phone":
            result = ams360_service.search_customer_by_phone(arguments.get("phone"))
            if result:
                return f"Found customer information in AMS360 for phone {arguments.get('phone')}. Customer data retrieved successfully."
            else:
                return f"No customer found in AMS360 with phone number {arguments.get('phone')}."
        
        elif function_name == "search_ams360_customer_by_name":
            result = ams360_service.search_customer_by_name(arguments.get("name"))
            if result:
                return f"Found customer information in AMS360 for name '{arguments.get('name')}'. Customer data retrieved successfully."
            else:
                return f"No customer found in AMS360 with name '{arguments.get('name')}'."
        
        elif function_name == "get_ams360_customer_policies":
            result = ams360_service.get_customer_policies(arguments.get("customer_id"))
            if result:
                return f"Retrieved policies for customer {arguments.get('customer_id')} from AMS360 successfully."
            else:
                return f"No policies found for customer {arguments.get('customer_id')} in AMS360."
        
        # AgencyZoom Functions
        elif function_name == "create_agencyzoom_lead":
            lead_data = {
                "first_name": arguments.get("first_name"),
                "last_name": arguments.get("last_name"),
                "email": arguments.get("email"),
                "phone": arguments.get("phone"),
                "insurance_type": arguments.get("insurance_type"),
                "notes": arguments.get("notes", ""),
                "source": "AI Chatbot"
            }
            
            # Add optional fields
            if arguments.get("address"):
                lead_data["address"] = arguments.get("address")
            if arguments.get("date_of_birth"):
                lead_data["date_of_birth"] = arguments.get("date_of_birth")
            if arguments.get("current_provider"):
                lead_data["current_provider"] = arguments.get("current_provider")
            if arguments.get("vehicle_info"):
                lead_data["vehicle_info"] = arguments.get("vehicle_info")
            if arguments.get("property_info"):
                lead_data["property_info"] = arguments.get("property_info")
            if arguments.get("business_name"):
                lead_data["business_name"] = arguments.get("business_name")
            if arguments.get("appointment_requested"):
                lead_data["appointment_requested"] = arguments.get("appointment_requested")
            
            result = agencyzoom_service.create_lead(lead_data)
            if result:
                return f"Successfully created lead in AgencyZoom for {arguments.get('first_name')} {arguments.get('last_name')}."
            else:
                return "Failed to create lead in AgencyZoom. Please check the logs for details."
        
        elif function_name == "search_agencyzoom_contact_by_phone":
            result = agencyzoom_service.search_contact_by_phone(arguments.get("phone"))
            if result and result.get('contacts'):
                count = len(result['contacts'])
                return f"Found {count} contact(s) in AgencyZoom with phone number {arguments.get('phone')}."
            else:
                return f"No contact found in AgencyZoom with phone number {arguments.get('phone')}."
        
        elif function_name == "search_agencyzoom_contact_by_email":
            result = agencyzoom_service.search_contact_by_email(arguments.get("email"))
            if result and result.get('contacts'):
                count = len(result['contacts'])
                return f"Found {count} contact(s) in AgencyZoom with email {arguments.get('email')}."
            else:
                return f"No contact found in AgencyZoom with email {arguments.get('email')}."
        
        elif function_name == "submit_collected_data_to_agencyzoom":
            # This is a complex function from the agent - simplified version
            if not insurance_service.insurance_type:
                return "No insurance data has been collected yet. Please collect insurance information first."
            
            insurance_type = insurance_service.insurance_type
            insurance_key = f"{insurance_type}_insurance"
            
            if insurance_key not in insurance_service.collected_data:
                return f"No {insurance_type} insurance data found. Please collect the information first."
            
            insurance_data = insurance_service.collected_data[insurance_key]
            
            # Extract basic info
            full_name = insurance_data.get("full_name", "")
            name_parts = full_name.split(" ", 1)
            first_name = name_parts[0] if name_parts else "Unknown"
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            lead_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": insurance_data.get("email", "noemail@pending.com"),
                "phone": insurance_data.get("phone", ""),
                "insurance_type": insurance_type,
                "source": "AI Chatbot",
                "notes": f"Lead collected via AI chatbot. Thread ID: {thread_id}",
                "insurance_details": insurance_data
            }
            
            result = agencyzoom_service.create_lead(lead_data)
            if result:
                return f"Excellent! I've successfully submitted all your {insurance_type} insurance information to AgencyZoom. Our team will follow up with you shortly!"
            else:
                return "Failed to submit data to AgencyZoom. The information is saved and can be submitted manually."
        
        else:
            return f"Unknown function: {function_name}"
    
    except Exception as e:
        logger.error(f"Error executing function {function_name}: {e}", exc_info=True)
        return f"Error executing {function_name}: {str(e)}"


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with conversation memory.
    
    Args:
        request: ChatRequest containing query and thread_id
    
    Returns:
        ChatResponse with AI response, thread_id, and timestamp
    """
    try:
        logger.info(f"Received chat request - Thread: {request.thread_id}, Query: {request.query}")
        
        # Get or create conversation thread
        messages = get_or_create_thread(request.thread_id)
        
        # Add user message to conversation history
        messages.append({
            "role": "user",
            "content": request.query
        })
        
        # Get available tools
        tools = get_available_tools()
        
        # Call OpenAI API with function calling
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message
        
        # Handle function calls if present
        while assistant_message.tool_calls:
            # Add assistant's response with tool calls to history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in assistant_message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the function
                function_result = execute_function_call(
                    function_name,
                    function_args,
                    request.thread_id
                )
                
                # Add function result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": function_result
                })
            
            # Get next response from OpenAI
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message
        
        # Add final assistant message to history
        messages.append({
            "role": "assistant",
            "content": assistant_message.content
        })
        
        logger.info(f"Chat response generated - Thread: {request.thread_id}")
        
        return ChatResponse(
            response=assistant_message.content,
            thread_id=request.thread_id,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/thread/{thread_id}/history")
async def get_thread_history(thread_id: str):
    """Get conversation history for a thread."""
    if thread_id not in conversation_threads:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
    
    return {
        "thread_id": thread_id,
        "message_count": len(conversation_threads[thread_id]),
        "messages": conversation_threads[thread_id]
    }


@app.delete("/thread/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a conversation thread and its associated services."""
    if thread_id in conversation_threads:
        del conversation_threads[thread_id]
    
    if thread_id in thread_services:
        del thread_services[thread_id]
    
    logger.info(f"Deleted thread: {thread_id}")
    return {"message": f"Thread {thread_id} deleted successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_threads": len(conversation_threads),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Insurance Chatbot API",
        "version": "1.0.0",
        "description": "Chatbot API with conversation memory for insurance quotes",
        "endpoints": {
            "POST /chat": "Send a message and get a response",
            "GET /thread/{thread_id}/history": "Get conversation history",
            "DELETE /thread/{thread_id}": "Delete a conversation thread",
            "GET /health": "Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Insurance Chatbot API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

