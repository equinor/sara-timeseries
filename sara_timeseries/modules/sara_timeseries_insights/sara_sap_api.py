from typing import List

from pydantic import BaseModel, ConfigDict, Field
import requests


class MaintenanceRecordMinimalWithActiveStatusIds(BaseModel):
    """
    This model is copied from Sara SAP and only uses some of the available fields.
    """

    model_config = ConfigDict(populate_by_name=True)

    record_id: str = Field(alias="recordId")
    title: str = Field(alias="title")


class PreventiveWorkOrder(BaseModel):
    """
    This model is copied from Sara SAP and only uses some of the available fields.
    """

    model_config = ConfigDict(populate_by_name=True)

    work_order_id: str = Field(alias="workOrderId")
    maintenance_records: List[MaintenanceRecordMinimalWithActiveStatusIds] = Field(
        alias="maintenanceRecords", default_factory=list
    )
    created_date_time: str | None = Field(alias="createdDateTime")
    changed_date_time: str | None = Field(alias="changedDateTime")


class UploadedFile(BaseModel):
    """
    This model is copied from Sara SAP and only uses some of the available fields.
    """

    maintenance_record_id: str = Field(...)
    document_id: str = Field(...)
    file_name: str = Field(...)


class SaraSapApi:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url: str = base_url
        self.token: str = token

    def get_next_co2_work_order(self) -> PreventiveWorkOrder:
        response = requests.get(
            url=f"{self.base_url}/insights-uploader/next-co2-work-order",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        response.raise_for_status()
        work_order = PreventiveWorkOrder.model_validate(response.json())
        return work_order

    def post_upload_co2_report(self, html: bytes) -> List[UploadedFile]:
        files = [("files", ("co2_report.html", html, "text/html"))]
        response = requests.post(
            url=f"{self.base_url}/insights-uploader",
            headers={"Authorization": f"Bearer {self.token}"},
            files=files,
        )
        response.raise_for_status()
        uploaded_files = [UploadedFile.model_validate(item) for item in response.json()]
        return uploaded_files
