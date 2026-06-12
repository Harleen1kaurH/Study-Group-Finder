"""
course.py — schemas for course catalogue endpoints.

CourseResponse: returned when listing or fetching a single course
"""

import uuid
from pydantic import BaseModel


class CreateCourseRequest(BaseModel):
    code: str  # e.g. CS101
    name: str  # e.g. Intro to Computer Science


class CourseResponse(BaseModel):
    id: uuid.UUID
    code: str  # e.g. CS101
    name: str  # e.g. Intro to Computer Science

    model_config = {"from_attributes": True}
