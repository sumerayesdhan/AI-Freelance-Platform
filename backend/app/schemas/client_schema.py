from pydantic import BaseModel, EmailStr, Field
from typing import Optional





class ClientRegister(BaseModel):


    full_name: str = Field(

        ...,

        min_length=3,

        max_length=100

    )


    email: EmailStr



    password: str = Field(

        ...,

        min_length=8

    )


    role: Optional[str] = "CLIENT"







class ClientLogin(BaseModel):


    email: EmailStr


    password: str

    role: Optional[str] = "client"






class ClientResponse(BaseModel):


    message: str


    client_id: str | None = None


    email: EmailStr | None = None