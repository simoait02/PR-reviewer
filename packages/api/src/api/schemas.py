from pydantic import BaseModel, Field


class UserQuestion(BaseModel):
    question: str = Field(
        min_length=1,
        description="The user's question for the pull request review.",
    )
