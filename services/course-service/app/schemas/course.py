"""Pydantic schemas for Course Service."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Category Schemas
class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Course Content Schemas
class CourseContentBase(BaseModel):
    """Base course content schema."""

    title: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=50)
    content_url: Optional[str] = Field(None, max_length=500)
    content_text: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order: int = Field(default=0, ge=0)
    is_preview: bool = False


class CourseContentCreate(CourseContentBase):
    """Schema for creating course content."""

    pass


class CourseContentUpdate(BaseModel):
    """Schema for updating course content."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content_type: Optional[str] = Field(None, min_length=1, max_length=50)
    content_url: Optional[str] = Field(None, max_length=500)
    content_text: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None


class CourseContentResponse(CourseContentBase):
    """Schema for course content response."""

    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Course Schemas
class CourseBase(BaseModel):
    """Base course schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category_id: Optional[int] = None
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    max_students: Optional[int] = Field(None, ge=1)
    thumbnail_url: Optional[str] = Field(None, max_length=500)


class CourseCreate(CourseBase):
    """Schema for creating a course."""

    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, ge=0)
    max_students: Optional[int] = Field(None, ge=1)
    is_published: Optional[bool] = None
    thumbnail_url: Optional[str] = Field(None, max_length=500)


class CourseResponse(CourseBase):
    """Schema for course response."""

    id: int
    instructor_id: int
    enrolled_count: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    contents: List[CourseContentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    """Schema for course list item (without full details)."""

    id: int
    title: str
    description: str
    instructor_id: int
    category_id: Optional[int]
    price: Decimal
    enrolled_count: int
    is_published: bool
    thumbnail_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedCourseResponse(BaseModel):
    """Schema for paginated course list response."""

    items: List[CourseListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Schema for generic message response."""

    message: str
