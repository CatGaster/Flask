from typing import Optional, Type

import pydantic
from pydantic import BaseModel

class BaseMessageSchema(BaseModel):
    title: Optional[str]
    text: Optional[str]
    name: Optional[str]


    @pydantic.field_validator("text")
    @classmethod
    def secure_text(cls, value):
        if len(value) < 5:
            raise ValueError("text is too short")
        return value
    

class CreateMessageSchema(BaseMessageSchema):
    title: str
    text: str
    name: str

class UpdateMessageSchema(BaseMessageSchema):
    title: Optional[str]
    text: Optional[str]
    name: Optional[str]

Schema = Type[CreateMessageSchema] | Type[UpdateMessageSchema]       
    