"""Operator API resource."""

from __future__ import annotations

from typing import Any


class _CrudResource:
    def __init__(self, http: Any, base_path: str) -> None:
        self._http = http
        self._base = base_path

    def list(self, **params: Any) -> Any:
        return self._http.get(self._base, params=params).json()

    def get(self, id: str) -> Any:
        return self._http.get(f"{self._base}/{id}").json()

    def create(self, data: dict[str, Any]) -> Any:
        return self._http.post(self._base, json=data).json()

    def update(self, id: str, data: dict[str, Any]) -> Any:
        return self._http.patch(f"{self._base}/{id}", json=data).json()

    def delete(self, id: str) -> None:
        self._http.delete(f"{self._base}/{id}")


class OperatorResource:
    def __init__(self, http: Any) -> None:
        self._http = http
        self.facilities = _CrudResource(http, "/operator/facilities")
        self.contacts = _CrudResource(http, "/operator/contacts")
        self.companies = _CrudResource(http, "/operator/companies")
        self.listings = _CrudResource(http, "/operator/listings")
        self.tenancies = _CrudResource(http, "/operator/tenancies")
        self.units = _CrudResource(http, "/operator/units")
        self.unit_types = _CrudResource(http, "/operator/unit-types")
        self.invoices = _CrudResource(http, "/operator/invoices")
        self.payments = _CrudResource(http, "/operator/payments")
        self.subscriptions = _CrudResource(http, "/operator/subscriptions")
        self.orders = _CrudResource(http, "/operator/orders")
        self.products = _CrudResource(http, "/operator/products")
        self.tickets = _CrudResource(http, "/operator/tickets")
        self.conversations = _CrudResource(http, "/operator/conversations")
