import logging
from typing import Tuple
from uuid import uuid4

from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def _log() -> None:
    logging.info(f"[MOCK] {request.method} {request.path}")
    try:
        if request.is_json:
            logging.info(f"[MOCK] JSON: {request.get_json()}")
    except Exception:
        pass


@app.route("/health", methods=["GET"])
def health() -> Tuple[str, int]:
    _log()
    return jsonify({"status": "ok"}), 200


@app.route("/timeseries/get-or-add", methods=["POST"])
def get_or_add_timeseries() -> Tuple[str, int]:
    _log()
    fake_id = f"mock-{uuid4()}"
    return jsonify({"data": {"items": [{"id": fake_id}]}}), 200


@app.route("/timeseries/<series_id>", methods=["GET"])
def get_timeseries_by_id(series_id: str) -> Tuple[str, int]:
    _log()
    item = {
        "id": series_id,
        "name": "mock",
        "facility": "mock-facility",
        "externalId": "mock-external",
        "description": "mock-description",
        "unit": "mock-unit",
        "step": True,
        "assetId": "mock-asset",
        "metadata": {},
    }
    return jsonify({"data": {"items": [item]}}), 200


@app.route("/timeseries/<series_id>", methods=["DELETE"])
def delete_timeseries(series_id: str) -> Tuple[str, int]:
    _log()
    return jsonify({"message": f"deleted {series_id}"}), 200


@app.route("/timeseries/search", methods=["GET"])
def search_timeseries() -> Tuple[str, int]:
    _log()
    return jsonify({"data": {"items": []}}), 200


@app.route("/timeseries/<series_id>/datapoints", methods=["POST"])
def write_data(series_id: str) -> Tuple[str, int]:
    _log()
    return jsonify({"statusCode": 0, "message": "ok", "traceId": "mock-trace-id"}), 200


@app.route("/datapoints/multi", methods=["POST"])
def get_multi_datapoints() -> Tuple[str, int]:
    _log()
    body = request.get_json(silent=True) or {}
    requests = body.get("requests", [])
    items: list[dict[str, object]] = [
        {"id": (r.get("id") or "unknown"), "datapoints": []} for r in requests
    ]
    return jsonify({"data": {"items": items}}), 200


def create_app() -> Flask:
    return app


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
