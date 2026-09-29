from pydantic import BaseModel, Field, PositiveInt


class PullRequestContext(BaseModel):
    repository_owner: str = Field(min_length=1)
    repository_name: str = Field(min_length=1)
    pull_number: PositiveInt


class UserQuestion(BaseModel):
    question: str = Field(min_length=1,description="The user's question for the pull request review.",)
    pull_request: PullRequestContext