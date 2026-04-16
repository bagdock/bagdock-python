"""Marketplace API resource."""

from __future__ import annotations

from typing import Any


class MarketplaceResource:
    def __init__(self, http: Any) -> None:
        self._http = http

    def search(self, **params: Any) -> Any:
        return self._http.get("/marketplace/search", params=params).json()

    def get_location(self, id: str) -> Any:
        return self._http.get(f"/marketplace/locations/{id}").json()

    def list_listings(self, **params: Any) -> Any:
        return self._http.get("/marketplace/listings", params=params).json()

    def get_listing(self, id: str) -> Any:
        return self._http.get(f"/marketplace/listings/{id}").json()

    def check_availability(self, **params: Any) -> Any:
        return self._http.get("/marketplace/availability", params=params).json()

    def create_rental(self, data: dict[str, Any]) -> Any:
        return self._http.post("/marketplace/rentals", json=data).json()

    def get_rental(self, id: str) -> Any:
        return self._http.get(f"/marketplace/rentals/{id}").json()

    def list_rentals(self, **params: Any) -> Any:
        return self._http.get("/marketplace/rentals", params=params).json()
