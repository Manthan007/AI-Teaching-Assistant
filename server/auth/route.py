from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic
from .model import *
from config.db import users_collection
from .hash_utils import *


router = APIRouter()
security=HTTPBasic()


@router.post("/signup/student")
def signup_student(req: StudentUser):
    """Handles a student signup requests"""
    # Check if username already exists
    if users_collection.find_one({"username": req.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    # hash the password before storing
    hashed_password = hash_password(req.password)
    users_collection.insert_one({
        "fullname": req.fullname,
        "email": req.email,
        "username": req.username,
        "password": hashed_password,
        "grade": req.grade,
        "school": req.school
    })

    return {"message": "Student user created successfully"}


@router.post("/signup/teacher")
def signup_teacher(req: TeacherUser):
    """Handles a Teacher signup requests"""
    # Check if username already exists
    if users_collection.find_one({"username": req.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    # hash the password before storing
    hashed_password = hash_password(req.password)
    users_collection.insert_one({
        "fullname": req.fullname,
        "email": req.email,
        "username": req.username,
        "password": hashed_password,
        "school": req.school
    })

    return {"message": "Teacher user created successfully"}
 