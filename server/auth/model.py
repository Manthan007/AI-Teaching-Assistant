from pydantic import BaseModel


class StudentUser(BaseModel):
    fullname: str
    email: str
    username: str
    password: str
    grade: int
    school: str


class TeacherUser(BaseModel):
    fullname: str
    email: str
    username: str
    password: str
    school: str
