from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the uploaded documents.",
    )


class SourceResponse(BaseModel):
    document: str
    page: int | None
    line_start: int | None
    line_end: int | None


class QuestionResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]