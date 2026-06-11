"""
courses.py — course catalogue routes.

Exposes the shared course list so users can browse and select a course
when creating a study group. Courses are not user-specific.
"""

from fastapi import APIRouter
from app.schemas.course import CourseResponse

router = APIRouter(prefix="/courses", tags=["courses"])


# Return all courses in the catalogue
@router.get("", response_model=list[CourseResponse])
def list_courses():
    return {"message": "not implemented yet"}


# Return a single course by its ID
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str):
    return {"message": "not implemented yet"}
