from pydantic import BaseModel


class NegotiationRequestCreate(BaseModel):

    freelancer_id: int

    project_id: str