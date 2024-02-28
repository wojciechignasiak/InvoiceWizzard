from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class InvoiceReportModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "invoice_number": "1/2024",
                "payment_deadline": "2023-12-10",
                "name": "Company Name",
                "net_value": "10.0",
                "gross_value": "12.00"
                }
            }
        )
    invoice_number: str
    payment_deadline: str
    name: str
    net_value: float
    gross_value: float

    async def from_tuple_to_model(tuple_data: tuple) -> "InvoiceReportModel":
        return InvoiceReportModel(
            invoice_number=tuple_data[0],
            payment_deadline=str(tuple_data[1]),
            name=tuple_data[2],
            net_value=tuple_data[3],
            gross_value=tuple_data[4]
        )


class UserBusinessEntityReportModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "cfafb4bd-59e0-46e5-9005-6afd7e5b8a38",
                "name": "Company Name",
                "net_value": "10.0",
                "gross_value": "12.00"
                }
            }
        )
    id: UUID
    name: str
<<<<<<< Updated upstream
    net_value: float
    gross_value: float
=======
    issued_net_value: float
    issued_gross_value: float
    recived_net_value: float
    recived_gross_value: float
>>>>>>> Stashed changes
    number_of_issued_invoices: Optional[int] = 0
    number_of_recived_invoices: Optional[int] = 0
    issued_settled_invoices: Optional[list[InvoiceReportModel]] = None
    recived_settled_invoices: Optional[list[InvoiceReportModel]] = None
    issued_unsettled_invoices: Optional[list[InvoiceReportModel]] = None
    recived_unsettled_invoices: Optional[list[InvoiceReportModel]] = None

    async def from_tuple_to_model(tuple_data: tuple) -> "UserBusinessEntityReportModel":
        return UserBusinessEntityReportModel(
            id=tuple_data[0],
            name=tuple_data[1],
<<<<<<< Updated upstream
            net_value=tuple_data[2],
            gross_value=tuple_data[3]
=======
            issued_net_value=tuple_data[2],
            issued_gross_value=tuple_data[3],
            recived_net_value=tuple_data[4],
            recived_gross_value=tuple_data[5]
>>>>>>> Stashed changes
        )