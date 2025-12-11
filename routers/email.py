"""
Email-related API endpoints using SMTP
"""

import os
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from utils.logger import log_info, log_error, log_exception
from models.model import EmailRequest, EmailResponse
from services.email import EmailService

load_dotenv()

router = APIRouter(prefix="/email", tags=["Email"])

# Initialize Email Service
try:
    email_service = EmailService()
    log_info("Email service initialized successfully")
except ValueError as e:
    log_error(f"Failed to initialize email service: {str(e)}")
    email_service = None
except Exception as e:
    log_error(f"Unexpected error initializing email service: {str(e)}")
    email_service = None


@router.post("/send", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    """
    Send an email using SMTP.
    
    Args:
        request: EmailRequest containing:
            - receiver_email: The recipient's email address
            - subject: Email subject line
            - body: Email body content (plain text or HTML)
            - is_html: Whether the body is HTML format (default: False)
        
    Returns:
        EmailResponse with status and confirmation message
        
    Example:
        POST /email/send
        {
            "receiver_email": "client@example.com",
            "subject": "Your Insurance Quote",
            "body": "Your quote is ready!",
            "is_html": false
        }
    """
    try:
        log_info(f"Email send request to: '{request.receiver_email}', Subject: '{request.subject}'")
        
        if not email_service:
            log_error("Email service not initialized")
            raise HTTPException(
                status_code=500,
                detail="Email service not available. Check your email credentials (EMAIL_ADDRESS and EMAIL_PASSWORD)."
            )
        
        # Send the email using EmailService
        success = email_service.send_email(
            receiver_email=request.receiver_email,
            subject=request.subject,
            body=request.body,
            is_html=request.is_html
        )
        
        if not success:
            log_error(f"Failed to send email to '{request.receiver_email}'")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email to {request.receiver_email}"
            )
        
        log_info(f"Successfully sent email to '{request.receiver_email}'")
        
        return EmailResponse(
            status="success",
            message=f"Email sent successfully to {request.receiver_email}",
            receiver_email=request.receiver_email
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log_exception(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email sending error: {str(e)}")

