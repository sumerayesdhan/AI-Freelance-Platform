from pydantic import BaseModel, Field





class ProjectCreate(BaseModel):


    title: str = Field(

        ...,

        min_length=3,

        max_length=100

    )


    description: str = Field(

        ...,

        min_length=20,

        max_length=5000

    )






class ProjectResponse(BaseModel):


    message: str


    project_id: str | None = None