import json
import os
import re
from typing import List

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.answer_chat.models import ContextModel, context_model
from apps.answer_chat.schemas import (
    AnswerSchema,
    ContextCreateSchema,
    ContextListSchema,
)
from config import OPENAI_API_KEY, OPENAI_MODEL, get_async_session

router = APIRouter(
    prefix="/answer-chat",
    tags=["Answer Chat"],
)


@router.get("/contexts", response_model=List[ContextListSchema])
async def get_contexts(session: AsyncSession = Depends(get_async_session)):
    query = select(context_model)
    result = await session.execute(query)
    return result.mappings().all()


@router.post("/contexts/create")
async def create_context(
    new_context: ContextCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    stats = insert(context_model).values(**new_context.dict())
    await session.execute(stats)
    await session.commit()


@router.delete("/contexts/all")
async def delete_contexts(session: AsyncSession = Depends(get_async_session)):
    stats = context_model.delete()
    await session.execute(stats)
    await session.commit()


@router.post("/contexts/fill")
async def fill_contexts(session: AsyncSession = Depends(get_async_session)):
    file_name = "data.json"
    file_path = os.path.join(os.getcwd(), "apps", "answer_chat")

    with open(
        os.path.join(file_path, file_name), "r", encoding="utf-8"
    ) as file:
        data = json.load(file)
        session.add_all(
            [
                ContextModel(
                    url=obj["url"],
                    context=obj["context"],
                    short_context=obj["short_context"],
                )
                for obj in data
            ]
        )
        await session.commit()


@router.post("/answer", response_model=AnswerSchema)
async def get_answer(
    message: AnswerSchema, session: AsyncSession = Depends(get_async_session)
):
    message = message.message

    query = select(context_model.c["id", "short_context"])
    result = await session.execute(query)
    contexts = result.mappings().all()

    message_gpt = (
        f"Ты нейронная сеть которая определяет нужные данные для контекста чат бота по сообщению от пользователя;"  # noqa E501
        f"Ответ должен включать в себя id контекстов максимальное значение 3;"
        f"Формат ответа всегда такой: id_контекста1, id_контекста2, id_контекста3;"  # noqa E501
        f"Список контекстов: {contexts}"
    )

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": message_gpt,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        model="gpt-3.5-turbo",
    )

    response_message_gpt = chat_completion.choices[0].message.content
    numbers = re.findall(r"\d+", response_message_gpt)
    integers = [int(num) for num in numbers]

    query = select(context_model.c["url", "context"]).where(
        context_model.c["id"].in_(integers[0:4])
    )
    result = await session.execute(query)
    contexts = result.mappings().all()

    message_gpt = (
        f"Ты ассистент для клиентов компании EORA которая разрабатывает ИИ для разных задач;"  # noqa E501
        f"Материал для ответа: {contexts};"
        f"Обязательно указывай ссылку на решаемый кейс;"
        f"Ссылку на источник указывай сразу а не в конце сообщения;"
    )
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": message_gpt,
            },
            {"role": "user", "content": message},
        ],
        model=OPENAI_MODEL,
    )
    response_message = AnswerSchema(
        message=chat_completion.choices[0].message.content
    )

    return response_message
