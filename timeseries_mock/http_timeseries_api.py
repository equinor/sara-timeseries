from typing import Any

import requests


class HttpTimeseriesAPI:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def get_or_add_timeseries(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/timeseries/get-or-add", json={"items": items}, timeout=5
        )
        return response.json()

    def write_data(self, timeseries_id: str, data: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/timeseries/{timeseries_id}/datapoints",
            json=data,
            timeout=5,
        )
        return response.json()

    def delete_timeseries_by_id(self, timeseries_id: str) -> dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}/timeseries/{timeseries_id}", timeout=5
        )
        return response.json()

    def search_timeseries(
        self, description: str | None = None, facility: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if description is not None:
            params["description"] = description
        if facility is not None:
            params["facility"] = facility
        response = requests.get(
            f"{self.base_url}/timeseries/search", params=params, timeout=5
        )
        return response.json()

    def get_timeseries_by_id(self, timeseries_id: str) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/timeseries/{timeseries_id}", timeout=5
        )
        return response.json()

    def get_multi_datapoints(
        self, request_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/datapoints/multi",
            json={"requests": request_items},
            timeout=10,
        )
        return response.json()
