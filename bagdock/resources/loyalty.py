"""Loyalty API resource."""

from __future__ import annotations

from typing import Any


class LoyaltyResource:
    def __init__(self, http: Any) -> None:
        self._http = http

    def create_member(self, data: dict[str, Any]) -> Any:
        return self._http.post("/loyalty/members", json=data).json()

    def get_member(self, id: str) -> Any:
        return self._http.get(f"/loyalty/members/{id}").json()

    def list_members(self, **params: Any) -> Any:
        return self._http.get("/loyalty/members", params=params).json()

    def get_balance(self, member_id: str) -> Any:
        return self._http.get("/loyalty/points/balance", params={"member_id": member_id}).json()

    def award_points(self, data: dict[str, Any]) -> Any:
        return self._http.post("/loyalty/points/award", json=data).json()

    def redeem_points(self, data: dict[str, Any]) -> Any:
        return self._http.post("/loyalty/points/redeem", json=data).json()

    def list_rewards(self, **params: Any) -> Any:
        return self._http.get("/loyalty/rewards", params=params).json()

    def claim_reward(self, data: dict[str, Any]) -> Any:
        return self._http.post("/loyalty/rewards/claim", json=data).json()
