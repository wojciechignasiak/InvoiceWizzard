#internal modules
from main_api_service.app.services.auth_service import IAuthService, new_auth_service
from main_api_service.app.services.user_service import IUserService, new_user_service
from main_api_service.app.services.register_account_service import IRegisterAccountService, new_register_account_service
from main_api_service.app.services.login_service import ILoginService, new_login_service
from main_api_service.app.services.logout_service import ILogoutService, new_logout_service
from main_api_service.app.services.change_password_service import IChangePasswordService, new_change_password_service
from main_api_service.app.custom_exceptions.custom_exceptions import CustomException
from main_api_service.app.models.jwt_model import JWTPayloadModel
from main_api_service.app.models.authentication_model import LogInModel
from main_api_service.app.models.user_model import (
    UserModel,
    RegisterUserModel, 
    UserPersonalInformationModel, 
    UpdateUserEmailModel, 
    UpdateUserPasswordModel, 
    ResetUserPasswordModel
    )

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse, Response

#1st party libraries
import datetime
from uuid import UUID

router = APIRouter()
http_bearer = HTTPBearer()

@router.get("/user/get-current-user/", response_model=UserModel)
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    user_service: IUserService = Depends(new_user_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        user_model: UserModel = await user_service.get_user_by_id(user_id=jwt_payload.id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_model.model_dump())
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/user/register-account/")
async def register_account(
    new_user: RegisterUserModel,
    register_account_service: IRegisterAccountService = Depends(new_register_account_service)
    ):
    try:
        await register_account_service.register_user(new_user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Account registered. Now confirm your email address"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/user/confirm-account/")
async def confirm_account(
    key_id: UUID,
    user_service: IUserService = Depends(new_user_service)
    ):
    try:
        await user_service.confirm_user_account(key_id)
        return JSONResponse(content={"detail": "Account confirmed"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/user/login/")
async def login(
    user_credentials: LogInModel,
    response: Response,
    login_service: ILoginService = Depends(new_login_service)
    ):
    try:
        expires: datetime.datetime = login_service.set_jwt_expiration_time(login.remember_me)
        jwt_token: str = await login_service.login(user_credentials)
        response.set_cookie(
            jwt_token,
            value=jwt_token,
            httponly=True,
            secure=True,
            samesite="strict",
            expires=expires,
        )
        return JSONResponse(content={"message": "Login successful"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/user/logout/")
async def logout(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    logout_service: ILogoutService = Depends(new_logout_service)
    ):
    try:
        await logout_service.logout(token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Logout successful"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/user/logout-from-all-devices/")
async def logout_from_all_devices(
    token = Depends(http_bearer),
    logout_service: ILogoutService = Depends(new_logout_service)
    ):

    try:
        await logout_service.logout_from_all_devices(token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Logged out from all devices"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/user/update-personal-information/")
async def update_personal_information(
    personal_information: UserPersonalInformationModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer), 
    auth_service: IAuthService = Depends(new_auth_service),
    user_service: IUserService = Depends(new_user_service)
    ):

    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await user_service.update_user_personal_information(jwt_payload.id, personal_information)
        return JSONResponse(content={"message": "Personal information updated successfully"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.put("/user/change-email-address/")
async def change_email_address(
    new_email: UpdateUserEmailModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer), 
    auth_service: IAuthService = Depends(new_auth_service),
    user_service: IUserService = Depends(new_user_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await user_service.change_email_address(jwt_payload.id, new_email)
        return JSONResponse(content={"message": "New email has been saved. Email message with confirmation link has been send to old email address"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/user/confirm-email-address-change")
async def confirm_email_address_change(
    key_id: UUID,
    user_service: IUserService = Depends(new_user_service)
    ):
    try:
        await user_service.confirm_email_address_change(key_id)
        return JSONResponse(content={"message": "New email has been set. You have been logged off from all devices"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.put("/user/change-password/")
async def change_password(
    new_password: UpdateUserPasswordModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    change_password_service: IChangePasswordService = Depends(new_change_password_service)
    ):
    try:
        await change_password_service.change_password(token, new_password)
        return JSONResponse(content={"message": "New password has been saved. Email message with confirmation link has been send to email address"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.put("/user/reset-password/")
async def reset_password(
    password_reset: ResetUserPasswordModel,
    change_password_service: IChangePasswordService = Depends(new_change_password_service)
    ):
    try:
        await change_password_service.reset_password(password_reset)
        return JSONResponse(content={"message": "If provided email address is correct you will get email message with url to confirm your new password"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/user/confirm-password-change/")
async def confirm_password_change(
    password_change_id: UUID,
    user_service: IUserService = Depends(new_user_service)
    ):
    try:
        await user_service.confirm_password_change(password_change_id)
        return JSONResponse(content={"message": "New password has been set. You have been logged out from all devices"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")