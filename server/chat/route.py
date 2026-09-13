from fastapi import APIRouter, HTTPException, Depends, Body
from auth.route import authenticate
from chat.chat_query import answer_query, quiz_generation
from pydantic import BaseModel
from typing import List, Optional
import datetime
from config.db import (
    chat_history_collection,
    quiz_history,
    quizzes_collection
)
from bson.objectid import ObjectId




router = APIRouter()

class QuizRequest(BaseModel):
    topic: str
    num_questions: Optional[int]=3

class QuizAnswerRequest(BaseModel):
    quiz_id: str
    answers: List[str]

@router.post("/chat")
async def chat(user=Depends(authenticate), query: str=Body(..., embed=True)):
    if user["role"] !="Student":
        raise HTTPException(
            status_code=403,
            detail="Only student can ask questions"
        )

    response=await answer_query(
        query, user["role"], user["grade"],
    )

    chat_history_collection.insert_one({
        "user_id": user["user_id"],
        "timestamp": datetime.datetime.utcnow(),
        "query": query,
        "response": response["answer"],
        "sources": response["sources"],
    })

    return response


@router.post("/quiz")
async def quiz(request: QuizRequest, user=Depends(authenticate)):
    if user["role"] !="Student":
        raise HTTPException(
            status_code=403,
            detail="Only student can generate quizzes.."
        )

    response = await quiz_generation(
        request.topic,
        user["role"],
        user["grade"],
        request.num_questions
    )

    quiz_docs = {
        "user_id": user["user_id"],
        "timestamp": datetime.datetime.utcnow(),
        "topic": request.topic,
        "quiz_data": response["quiz"],
        "sources": response["sources"],
    }

    result = quizzes_collection.insert_one(quiz_docs)

    return {
        "quiz": response["quiz"],
        "sources": response["sources"],
        "quiz_id": str(result.inserted_id)
    }