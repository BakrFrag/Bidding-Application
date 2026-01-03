from pydantic import BaseModel, Field, field_validator, ValidationError
from decimal import Decimal, InvalidOperation

class BidSubmissionSchema(BaseModel):
    """
    BidSubmissionSchema validate incoming bid data. must include 'name' and 'price'.
    price > 0 and name is non-empty string.
    """

    name: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., gt=0)

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just spaces')
        return v.strip()

    @field_validator('price')
    def validate_decimal_precision(cls, v):
        if v.as_tuple().exponent < -2:
            raise ValueError('Price cannot have more than 2 decimal places')
        return v