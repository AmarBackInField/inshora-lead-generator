import os
from dotenv import load_dotenv

# Try to load .env and show what's loaded
print("Loading .env file...")
load_dotenv()

# Check what values are actually loaded
print("\n=== Environment Variables ===")
print(f"AGENCYZOOM_USERNAME: {os.getenv('AGENCYZOOM_USERNAME', 'NOT SET')}")
print(f"AGENCYZOOM_PASSWORD: {'***' if os.getenv('AGENCYZOOM_PASSWORD') else 'NOT SET'}")
print(f"AGENCYZOOM_BASE_URL: {os.getenv('AGENCYZOOM_BASE_URL', 'NOT SET')}")
print(f"AGENCYZOOM_AGENCY_ID: {os.getenv('AGENCYZOOM_AGENCY_ID', 'NOT SET')}")

# Now try to initialize the service
print("\n=== Initializing AgencyZoom Service ===")
from services.agencyzoom import AgencyZoomService
service = AgencyZoomService()
print(f"\nAPI Key result: {service.api_key}")