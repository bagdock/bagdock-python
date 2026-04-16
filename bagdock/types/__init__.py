"""Pydantic models for Bagdock API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Facility(BaseModel):
    id: str
    operator_id: str
    name: str
    slug: str
    status: str
    currency: str
    total_units: int = 0
    occupied_units: int = 0
    available_units: int = 0
    created_at: str
    updated_at: str


class Contact(BaseModel):
    id: str
    operator_id: str
    email: str
    first_name: str
    last_name: str
    type: str = "individual"
    status: str = "active"
    kyc_status: str = "not_started"
    created_at: str
    updated_at: str


class Rental(BaseModel):
    id: str
    user_id: str
    listing_id: str
    operator_id: str
    rental_reference: str
    status: str
    agreed_price_pence: int
    currency: str
    created_at: str
    updated_at: str


class PaginatedResponse(BaseModel):
    object: str = "list"
    data: list[Any]
    has_more: bool = False
    total_count: int | None = None
