from pydantic import BaseModel, Field, field_validator, ValidationError
from decimal import Decimal, ROUND_HALF_UP

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

    @field_validator('price', mode='after')
    @classmethod
    def round_price_to_two_decimals(cls, v: Decimal) -> Decimal:
        
        rounded_value = v.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        return rounded_value