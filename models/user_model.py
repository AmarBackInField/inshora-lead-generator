from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Literal
from datetime import date, datetime
from enum import Enum

class User(BaseModel):
    type_of_user: Literal["add", "update"] = Field(..., description="Type of user action regarding the insurance")
    insurance_type: Literal["home", "auto", "flood", "life", "commercial"] = Field(..., description="Type of insurance")