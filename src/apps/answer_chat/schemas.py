from pydantic import BaseModel


class ContextListSchema(BaseModel):
    id: int
    url: str
    context: str
    short_context: str


class ContextCreateSchema(BaseModel):
    url: str
    context: str
    short_context: str


class AnswerSchema(BaseModel):
    message: str
