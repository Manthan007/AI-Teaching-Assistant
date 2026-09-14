from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .model import *
from config.db import users_collection
from .hash_utils import *


router = APIRouter()
security=HTTPBasic()


def authenticate(credentials: HTTPBasicCredentials=Depends(security)):
    """Authenticate a user using HTTP Basic Auth"""
    user = users_collection.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user.get("password")):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "username": user.get("username"),
        "role": user.get("role"),
        "grade": user.get("grade"),
        "user_id": str(user.get("_id")),
    }


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
        "role": "Student",
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
        "role": "Teacher",
        "school": req.school
    })

    return {"message": "Teacher user created successfully"}


@router.get("/login")
def login(user=Depends(authenticate)):
    """Handles user login"""
    return {"message": f"Welcome, {user["username"]}!", "role": user["role"]}
