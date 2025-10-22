from typing import Any, Dict, List, Optional

import requests


class HttpTimeseriesAPI:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def get_or_add_timeseries(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/timeseries/get-or-add", json={"items": items}, timeout=5
        )
        return response.json()

    def write_data(self, timeseries_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/timeseries/{timeseries_id}/datapoints",
            json=data,
            timeout=5,
        )
        return response.json()

    def delete_timeseries_by_id(self, timeseries_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}/timeseries/{timeseries_id}", timeout=5
        )
        return response.json()

    def search_timeseries(
        self, description: Optional[str] = None, facility: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if description is not None:
            params["description"] = description
        if facility is not None:
            params["facility"] = facility
        response = requests.get(
            f"{self.base_url}/timeseries/search", params=params, timeout=5
        )
        return response.json()

    def get_timeseries_by_id(self, timeseries_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/timeseries/{timeseries_id}", timeout=5
        )
        return response.json()

    def get_multi_datapoints(
        self, request_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/datapoints/multi",
            json={"requests": request_items},
            timeout=10,
        )
        return response.json()
