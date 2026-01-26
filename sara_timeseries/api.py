from typing import Any, Callable, Optional

from fastapi import FastAPI

from sara_timeseries.modules.sara_timeseries_api.timeseries_controller import (
    TimeseriesController,
)
from sara_timeseries.modules.sara_timeseries_insights.insights_controller import (
    InsightsController,
)


class API:
    def __init__(
        self,
        timeseries_controller: TimeseriesController,
        insights_controller: InsightsController,
    ) -> None:
        self.timeseries_controller: TimeseriesController = timeseries_controller
        self.insights_controller: InsightsController = insights_controller

    def create_app(
        self, lifespan: Optional[Callable[[FastAPI], Any]] = None
    ) -> FastAPI:
        app = FastAPI(lifespan=lifespan)
        app.include_router(router=self.timeseries_controller.create_timeseries_router())
        app.include_router(router=self.insights_controller.create_insights_controller())
        return app
