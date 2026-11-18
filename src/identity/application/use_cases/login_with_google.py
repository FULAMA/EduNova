import hashlib
from datetime import datetime, timezone

from src.identity.application.dto.google_login_request import GoogleLoginRequest
from src.identity.application.interfaces.google_nonce_repository import GoogleNonceRepository
from src.identity.application.interfaces.google_identity_verifier import (
    GoogleIdentityVerifier,
)
from src.identity.application.interfaces.external_identity_repository import (
    ExternalIdentityRepository,
)
from src.identity.application.interfaces.jwt_service import JwtService
from src.identity.application.interfaces.user_repository import UserRepository
from src.identity.application.use_cases.login_user import LoginUserResponse
from src.tenancy.application.interfaces.membership_repository import (
    MembershipRepository,
)
from src.tenancy.application.interfaces.tenant_repository import TenantRepository


class LoginWithGoogle:
    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        external_identity_repository: ExternalIdentityRepository,
        google_identity_verifier: GoogleIdentityVerifier,
        jwt_service: JwtService,
        google_nonce_repository: GoogleNonceRepository,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._external_identity_repository = external_identity_repository
        self._google_identity_verifier = google_identity_verifier
        self._jwt_service = jwt_service
        self._google_nonce_repository = google_nonce_repository

    def execute(
        self,
        request: GoogleLoginRequest,
    ) -> LoginUserResponse:
        if not request.id_token.strip():
            raise ValueError("Le jeton Google ne peut pas etre vide.")
        if not request.nonce.strip():
            raise ValueError("Nonce Google invalide.")

        nonce_hash = hashlib.sha256(request.nonce.encode("utf-8")).hexdigest()
        if not self._google_nonce_repository.consume(
            nonce_hash, datetime.now(timezone.utc)
        ):
            raise ValueError("Nonce Google invalide.")

        identity = self._google_identity_verifier.verify(
            request.id_token, request.nonce
        )

        if not identity.email_verified or not identity.email.strip():
            raise ValueError("L adresse e-mail Google n est pas verifiee.")

        linked_identity = (
            self._external_identity_repository.find_by_provider_and_subject(
                "google",
                identity.subject,
            )
        )
        if linked_identity is None:
            raise ValueError("Identifiants invalides.")

        user = self._user_repository.find_by_id(linked_identity.user_id)
        if user is None:
            raise ValueError("Identifiants invalides.")

        if not user.is_active:
            raise ValueError("Le compte est desactive.")

        tenant = self._tenant_repository.find_by_id(request.tenant_id)
        membership = self._membership_repository.find_by_user_and_tenant(
            user.id,
            request.tenant_id,
        )
        if tenant is None or not tenant.active or membership is None or not membership.active:
            raise ValueError("Acces tenant refuse.")

        if user.two_factor_enabled:
            return LoginUserResponse(
                authenticated=False,
                two_factor_required=True,
                two_factor_token=self._jwt_service.create_two_factor_token(
                    user_id=user.id,
                    tenant_id=request.tenant_id,
                ),
                access_token=None,
                refresh_token=None,
                email=identity.email,
            )

        return LoginUserResponse(
            authenticated=True,
            two_factor_required=False,
            two_factor_token=None,
            access_token=self._jwt_service.create_access_token(
                user_id=user.id,
                role=membership.role,
                tenant_id=request.tenant_id,
            ),
            refresh_token=self._jwt_service.create_refresh_token(
                user_id=user.id,
                tenant_id=request.tenant_id,
            ),
            email=identity.email,
        )
