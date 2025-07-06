#internal modules
from main_api_service.app.services.auth_service import IAuthService, new_auth_service
from main_api_service.app.services.invoice_service import IInvoiceService, new_invoice_service
from main_api_service.app.models.jwt_model import JWTPayloadModel
from main_api_service.app.models.invoice_model import CreateInvoiceModel, InvoiceModel, UpdateInvoiceModel
from main_api_service.app.custom_exceptions.custom_exceptions import CustomException

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder

#1st party libraries
from uuid import UUID
from pathlib import Path
from datetime import date


router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/invoice/create-invoice/", response_model={'invoice_id': "da996a8d-f67d-4378-ac7f-5f2d1f65c9b9"})
async def create_invoice(
    new_invoice: CreateInvoiceModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        invoice_id: UUID = await invoice_service.create_invoice(jwt_payload.user_id, new_invoice)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"invoice_id": invoice_id})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.get("/invoice/get-invoice/")
async def get_invoice(
    invoice_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        invoice: InvoiceModel = await invoice_service.get_invoice_by_id(jwt_payload.user_id, invoice_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=invoice.model_dump_json())
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.get("/invoice/get-all-invoices/")
async def get_all_invoices(
    page: int,
    items_per_page: int,
    user_business_entity_id: UUID | None = None,
    user_business_entity_name: str | None = None,
    external_business_entity_id: UUID | None = None,
    external_business_entity_name: str | None = None,
    invoice_number: str | None = None,
    start_issue_date: date | None = None,
    end_issue_date: date | None = None,
    start_sale_date: date | None = None,
    end_sale_date: date | None = None,
    payment_method: str | None = None,
    start_payment_deadline: date | None = None,
    end_payment_deadline: date | None = None,
    start_added_date: date | None = None,
    end_added_date: date | None = None,
    is_settled: bool | None = None,
    is_issued: bool | None = None,
    in_trash: bool | None = None,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):

    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        invoices: list[InvoiceModel] = await invoice_service.get_all_invoices(
            jwt_payload.user_id,
            page,
            items_per_page,
            user_business_entity_id,
            user_business_entity_name,
            external_business_entity_id,
            external_business_entity_name,
            invoice_number,
            start_issue_date,
            end_issue_date,
            start_sale_date,
            end_sale_date,
            payment_method,
            start_payment_deadline,
            end_payment_deadline,
            start_added_date,
            end_added_date,
            is_settled,
            is_issued,
            in_trash
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(invoices))
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/invoice/update-invoice/")
async def update_invoice(
    invoice_to_update: UpdateInvoiceModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.update_invoice(jwt_payload.user_id, invoice_to_update)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Invoice updated successfully."})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.patch("/invoice/update-invoice-in-trash-status/")
async def update_invoice_in_trash_status(
    invoice_id: UUID,
    in_trash: bool,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.update_invoice_in_trash_status(jwt_payload.user_id, invoice_id, in_trash)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice and it's items in trash status updated"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.put("/invoice/initialize-invoice-removal/")
async def initialize_invoice_removal(
    invoice_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.initialize_invoice_removal(jwt_payload.user_id, jwt_payload.email, invoice_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice removal initialized"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/invoice/confirm-invoice-removal/")
async def confirm_invoice_removal(
    key_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.confirm_invoice_removal(key_id, jwt_payload.user_id, jwt_payload.email)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice removed successfully"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post("/invoice/add-file-to-invoice/")
async def add_file_to_invoice(
    invoice_id: UUID,
    invoice_file: UploadFile,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.add_file_to_invoice(jwt_payload.user_id, invoice_id, await invoice_file.read(), invoice_file.filename.split(".")[-1])
        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "File added to invoice successfully"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/invoice/delete-invoice-pdf/")
async def delete_invoice_pdf(
    invoice_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.delete_file_from_invoice(jwt_payload.user_id, invoice_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "File removed from invoice successfully"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/invoice/download-invoice-pdf/")
async def download_invoice_pdf(
    invoice_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        file: Path = await invoice_service.get_invoice_file(jwt_payload.user_id, invoice_id)
        return FileResponse(path=file, status_code=status.HTTP_200_OK, filename=file.name)
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post("/invoice/generate-invoice-pdf/")
async def generate_invoice_pdf(
    invoice_id: UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.generate_invoice_file(jwt_payload.user_id, invoice_id)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"details": "File generated"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")