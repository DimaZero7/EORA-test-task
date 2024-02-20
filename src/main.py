from fastapi import FastAPI

from apps.answer_chat.router import router as answer_chat_router

app = FastAPI(title="EORA test task")


app.include_router(answer_chat_router)
