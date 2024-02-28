<<<<<<< Updated upstream
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
=======
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
>>>>>>> Stashed changes
from fastapi.security import HTTPBearer
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError, 
    RedisJWTNotFoundError,
)
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from app.models.jwt_model import (
    JWTPayloadModel
)
from app.models.report_model import (
    UserBusinessEntityReportModel,
    InvoiceReportModel
)
from app.types.postgres_repository_abstract_types import (
    ReportPostgresRepositoryABC
)
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC,
)
<<<<<<< Updated upstream


=======
from datetime import date
from app.documents.report_builder_abc import ReportBuilderABC
from app.documents.report_builder import ReportBuilder
from app.files.files_repository_abc import FilesRepositoryABC
>>>>>>> Stashed changes

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/report-module/generate-report/")
async def generate_invoice(
<<<<<<< Updated upstream
=======
    issue_date_start: date,
    issue_date_end: date,
>>>>>>> Stashed changes
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):

    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        report_postgres_repository: ReportPostgresRepositoryABC = await repositories_registry.return_report_postgres_repository(postgres_session)
<<<<<<< Updated upstream
=======
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()
>>>>>>> Stashed changes

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entities_report: list[tuple] = await report_postgres_repository.get_user_business_entities_net_and_gross_values(
            user_id=jwt_payload.id,
<<<<<<< Updated upstream
            start_date='2023-12-01',
            end_date='2023-12-30',
            is_issued=True
=======
            start_date=issue_date_start,
            end_date=issue_date_end
>>>>>>> Stashed changes
        )

        user_business_entities_report: list[UserBusinessEntityReportModel] = [
            await UserBusinessEntityReportModel.from_tuple_to_model(user_business_entity_report) for 
            user_business_entity_report in 
            user_business_entities_report]

        for user_business_entity_report in user_business_entities_report:
            number_of_issued_invoices: list[tuple] = await report_postgres_repository.get_user_business_entity_number_of_invoices(
                user_id=jwt_payload.id,
<<<<<<< Updated upstream
                start_date='2023-12-01',
                end_date='2023-12-30',
=======
                start_date=issue_date_start,
                end_date=issue_date_end,
>>>>>>> Stashed changes
                is_issued=True,
                user_business_entity_id=str(user_business_entity_report.id)
            )

            number_of_recived_invoices: list[tuple] = await report_postgres_repository.get_user_business_entity_number_of_invoices(
                user_id=jwt_payload.id,
<<<<<<< Updated upstream
                start_date='2023-12-01',
                end_date='2023-12-30',
=======
                start_date=issue_date_start,
                end_date=issue_date_end,
>>>>>>> Stashed changes
                is_issued=False,
                user_business_entity_id=str(user_business_entity_report.id)
            )
            user_business_entity_report.number_of_issued_invoices = number_of_issued_invoices[0][0]
            user_business_entity_report.number_of_recived_invoices = number_of_recived_invoices[0][0]

        for user_business_entity_report in user_business_entities_report:
            
            issued_settled_invoices: list[tuple] = await report_postgres_repository.get_user_invoice_data_related_to_user_business_entity(
                user_id=jwt_payload.id,
                user_business_entity_id=str(user_business_entity_report.id),
<<<<<<< Updated upstream
                start_date='2023-12-01',
                end_date='2023-12-30',
=======
                start_date=issue_date_start,
                end_date=issue_date_end,
>>>>>>> Stashed changes
                is_issued=True,
                is_settled=True
            )
            
            if issued_settled_invoices:
                issued_settled_invoices = [await InvoiceReportModel.from_tuple_to_model(invoice) for invoice in issued_settled_invoices]
                user_business_entity_report.issued_settled_invoices= issued_settled_invoices

            issued_unsettled_invoices = await report_postgres_repository.get_user_invoice_data_related_to_user_business_entity(
                user_id=jwt_payload.id,
                user_business_entity_id=str(user_business_entity_report.id),
<<<<<<< Updated upstream
                start_date='2023-12-01',
                end_date='2023-12-30',
=======
                start_date=issue_date_start,
                end_date=issue_date_end,
>>>>>>> Stashed changes
                is_issued=True,
                is_settled=False
            )
            
            if issued_unsettled_invoices:
                issued_unsettled_invoices = [await InvoiceReportModel.from_tuple_to_model(invoice) for invoice in issued_unsettled_invoices]
                user_business_entity_report.issued_unsettled_invoices = issued_unsettled_invoices

            recived_settled_invoices = await report_postgres_repository.get_user_invoice_data_related_to_user_business_entity(
                user_id=jwt_payload.id,
                user_business_entity_id=str(user_business_entity_report.id),
<<<<<<< Updated upstream
                start_date='2023-12-01',
                end_date='2023-12-30',
=======
                start_date=issue_date_start,
                end_date=issue_date_end,
>>>>>>> Stashed changes
                is_issued=False,
                is_settled=True
            )
            
            if recived_settled_invoices:
                recived_settled_invoices = [await InvoiceReportModel.from_tuple_to_model(invoice) for invoice in recived_settled_invoices]
                user_business_entity_report.recived_settled_invoices = recived_settled_invoices

            recived_unsettled_invoices = await report_postgres_repository.get_user_invoice_data_related_to_user_business_entity(
                user_id=jwt_payload.id,
                user_business_entity_id=str(user_business_entity_report.id),
<<<<<<< Updated upstream
                start_date='2023-12-01',
                end_date='2023-12-30',
=======
                start_date=issue_date_start,
                end_date=issue_date_end,
>>>>>>> Stashed changes
                is_issued=False,
                is_settled=False
            )
            
            if recived_unsettled_invoices:
                recived_unsettled_invoices = [await InvoiceReportModel.from_tuple_to_model(invoice) for invoice in recived_unsettled_invoices]
                user_business_entity_report.recived_unsettled_invoices = recived_unsettled_invoices
<<<<<<< Updated upstream
        
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(user_business_entities_report))
=======

        report_builder: ReportBuilderABC = ReportBuilder()
        report_html = await report_builder.create_report_html_document(
            user_business_entities_report=user_business_entities_report,
            start_date=issue_date_start,
            end_date=issue_date_end
        )
        
        
        file_path = f"/usr/app/invoice-files/report/{jwt_payload.id}/report.pdf"

        await files_repository.invoice_html_to_pdf(
            invoice_html=report_html,
            file_path=file_path
        )
        
        file = await files_repository.get_invoice_pdf_file(
            file_path=file_path
        )
        
        if file.is_file() == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
        return FileResponse(path=file, status_code=status.HTTP_200_OK, filename=file.name)
>>>>>>> Stashed changes
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    