from typing import Annotated
from fastapi import FastAPI, Path
from pydantic import Field, AfterValidator
import re

def validate_uuid7(value: str) -> str:
    """Custom validator with friendly error message"""
    uuid7_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    if not re.match(uuid7_pattern, value.lower()):
        raise ValueError('Invalid UUID7 format. Expected format: xxxxxxxx-xxxx-7xxx-xxxx-xxxxxxxxxxxx')
    
    return value

UUID7Str = Annotated[
    str, 
    Field(
        examples=["018e0864-8ee0-7f92-a139-7a6b4db524bb"],
        description="UUID7 identifier (version 7 UUID)"
    ),
    AfterValidator(validate_uuid7)
]
