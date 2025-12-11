"""
Twilio SMS-related API endpoints
"""

import os
from fastapi import APIRouter, HTTPException
from twilio.rest import Client
from dotenv import load_dotenv
from utils.logger import log_info, log_error, log_exception
from models.model import SMSRequest, SMSResponse, MessageStatusResponse

load_dotenv()

router = APIRouter(prefix="/sms", tags=["Twilio SMS"])

# Initialize Twilio client
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")

if not all([account_sid, auth_token, twilio_number]):
    log_error("Twilio credentials not found in environment variables")

try:
    client = Client(account_sid, auth_token)
    log_info("Twilio client initialized successfully")
except Exception as e:
    log_error(f"Failed to initialize Twilio client: {str(e)}")
    client = None


@router.post("/send", response_model=SMSResponse)
async def send_sms(request: SMSRequest):
    """
    Send an SMS message using Twilio.
    
    Args:
        request: SMSRequest containing:
            - body: The message content to send
            - number: The recipient's phone number (with country code, e.g., +1234567890)
        
    Returns:
        SMSResponse with status and message SID
    """
    try:
        log_info(f"SMS send request to: '{request.number}'")
        
        if not client:
            log_error("Twilio client not initialized")
            raise HTTPException(
                status_code=500,
                detail="Twilio service not available. Check your credentials."
            )
        
        # Validate phone number format
        if not request.number.startswith('+'):
            log_error(f"Invalid phone number format: '{request.number}'")
            raise HTTPException(
                status_code=400,
                detail="Phone number must start with '+' followed by country code (e.g., +1234567890)"
            )
        
        # Send the SMS message
        message = client.messages.create(
            body=request.body,
            from_=twilio_number,
            to=request.number
        )
        
        log_info(f"Successfully sent SMS to '{request.number}', SID: {message.sid}")
        
        return SMSResponse(
            status="success",
            message=f"SMS sent successfully to {request.number}",
            message_sid=message.sid,
            to_number=request.number
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_exception(f"Error sending SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SMS sending error: {str(e)}")


@router.get("/status/{message_sid}", response_model=MessageStatusResponse)
async def get_message_status(message_sid: str):
    """
    Get the status and details of a sent SMS message.
    
    Args:
        message_sid: The unique message SID returned when sending an SMS
        
    Returns:
        MessageStatusResponse with message details including delivery status
        
    Possible status values:
        - queued: Message is queued and will be sent shortly
        - sending: Message is currently being sent
        - sent: Message has been sent from Twilio
        - delivered: Message was successfully delivered to recipient
        - undelivered: Message failed to be delivered
        - failed: Message sending failed
    """
    try:
        log_info(f"Fetching status for message SID: {message_sid}")
        
        if not client:
            log_error("Twilio client not initialized")
            raise HTTPException(
                status_code=500,
                detail="Twilio service not available. Check your credentials."
            )
        
        # Fetch message details from Twilio
        message = client.messages(message_sid).fetch()
        
        log_info(f"Successfully retrieved status for SID: {message_sid}, Status: {message.status}")
        
        return MessageStatusResponse(
            status=message.status,
            message_sid=message.sid,
            to_number=message.to,
            from_number=message.from_,
            body=message.body,
            date_sent=str(message.date_sent) if message.date_sent else None,
            date_updated=str(message.date_updated) if message.date_updated else None,
            error_code=str(message.error_code) if message.error_code else None,
            error_message=message.error_message,
            price=message.price,
            direction=message.direction
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_exception(f"Error fetching message status: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving message status: {str(e)}"
        )

