from fastapi import FastAPI

from sara_timeseries.modules.sara_timeseries_api.timeseries_controller import (
    TimeseriesController,
)


class API:
    def __init__(self, timeseries_controller: TimeseriesController) -> None:
        self.timeseries_controller: TimeseriesController = timeseries_controller

    def create_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(router=self.timeseries_controller.create_timeseries_router())
        return app
