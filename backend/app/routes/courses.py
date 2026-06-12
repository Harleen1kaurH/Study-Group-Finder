"""
courses.py — course catalogue routes.

Exposes the shared course list so users can browse and select a course
when creating a study group. Courses are not user-specific.
No authentication required.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CreateCourseRequest, CourseResponse

router = APIRouter(prefix="/courses", tags=["courses"])


# Create a new course — any logged-in user can add to the catalogue
@router.post("", response_model=CourseResponse)
def create_course(
    body: CreateCourseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if a course with this code already exists
    existing = db.query(Course).filter(Course.code.ilike(body.code)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A course with this code already exists",
        )

    # Create and save the new course
    course = Course(code=body.code.upper(), name=body.name)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


# Return all courses, optionally filtered by course code
@router.get("", response_model=list[CourseResponse])
def list_courses(code: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Course)

    # If a code was provided, filter by it (case-insensitive)
    if code is not None:
        query = query.filter(Course.code.ilike(code))

    return query.all()


# Return a single course by its ID
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    # Look up the course by primary key
    course = db.get(Course, course_id)

    # Return 404 if no course with that ID exists
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course
