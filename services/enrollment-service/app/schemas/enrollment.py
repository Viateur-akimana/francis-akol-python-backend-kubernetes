"""Pydantic schemas for Enrollment Service."""

from datetime import datetime
from typing import Optional

from app.models.enrollment import EnrollmentStatus
from pydantic import BaseModel, ConfigDict, Field


# Enrollment Schemas
class EnrollmentBase(BaseModel):
    """Base enrollment schema."""

    course_id: int = Field(..., gt=0)


class EnrollmentCreate(EnrollmentBase):
    """Schema for creating an enrollment."""

    pass


class EnrollmentUpdate(BaseModel):
    """Schema for updating an enrollment."""

    status: Optional[EnrollmentStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


class EnrollmentResponse(BaseModel):
    """Schema for enrollment response."""

    id: int
    user_id: int
    course_id: int
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime]
    progress_percentage: int
    last_accessed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnrollmentWithCourseInfo(EnrollmentResponse):
    """Schema for enrollment response with course information."""

    course_title: Optional[str] = None
    course_instructor_id: Optional[int] = None


class PaginatedEnrollmentResponse(BaseModel):
    """Schema for paginated enrollment list response."""

    items: list[EnrollmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Schema for generic message response."""

    message: str


class EnrollmentStatsResponse(BaseModel):
    """Schema for enrollment statistics."""

    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    cancelled_enrollments: int
    pending_enrollments: int
