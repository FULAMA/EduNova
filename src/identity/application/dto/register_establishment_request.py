from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterEstablishmentRequest:
    """DTO containing the essential information to register an establishment.

    Technical attributes such as tenant_id, user_id, membership_id, role,
    tenant status, and permissions are determined strictly server-side and
    cannot be provided by the client.
    """

    school_name: str
    admin_name: str
    email: str
    password: str
