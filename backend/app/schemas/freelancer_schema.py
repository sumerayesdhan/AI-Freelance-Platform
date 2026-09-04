from pydantic import BaseModel, EmailStr
from typing import Optional


class FreelancerRegister(BaseModel):

    freelancer_id: int

    full_name: str

    email: EmailStr

    password: str

    title: Optional[str] = ""

    skills: Optional[str] = ""

    hourly_rate: Optional[float] = 0

    country: Optional[str] = ""


class FreelancerLogin(BaseModel):

    email: EmailStr

    password: str