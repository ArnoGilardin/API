"""
GDPR Consent management endpoints.
Handle opt-out requests and data processing consents.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.database import get_db
from app.schemas.schemas import ConsentRevokeRequest, ConsentRevokeResponse
from app.services.auth import verify_api_key
from app.models.models import Lead, Consent, Log

router = APIRouter()


@router.post(
    "/consents/revoke",
    response_model=ConsentRevokeResponse,
    summary="Revoke consent (Opt-out)",
    description="""
    Process a GDPR consent revocation request.

    This endpoint allows users to opt-out of data processing.
    Upon revocation:
    - The lead is tagged with 'opt_out'
    - Future scraping jobs will exclude this email
    - All consent records are updated
    - The action is logged for audit purposes

    **GDPR Compliance:** Requests are processed within 30 days as required by law.
    """,
)
async def revoke_consent(
    request: ConsentRevokeRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> ConsentRevokeResponse:
    """
    Revoke consent for a lead (opt-out).

    Args:
        request: Consent revocation request
        db: Database session
        api_key: Validated API key

    Returns:
        Confirmation of revocation
    """
    # Find lead by email
    lead = db.query(Lead).filter(Lead.email == request.email).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No lead found with email {request.email}",
        )

    # Generate request ID
    request_id = uuid4()

    # Create consent revocation record
    consent = Consent(
        lead_id=lead.id,
        consented=False,
        revoked_at=datetime.utcnow(),
        request_id=str(request_id),
        request_type=request.request_type,
    )

    db.add(consent)

    # Update lead tags to include opt_out
    if lead.tags is None:
        lead.tags = []

    if "opt_out" not in lead.tags:
        lead.tags.append("opt_out")

    # Log the action for audit
    log = Log(
        action="consent_revoked",
        lead_id=lead.id,
        timestamp=datetime.utcnow(),
        details={
            "email": request.email,
            "request_type": request.request_type,
            "reason": request.reason,
            "request_id": str(request_id),
        },
    )

    db.add(log)
    db.commit()

    return ConsentRevokeResponse(
        success=True,
        message=f"Consent revoked for {request.email}. The email has been added to the opt-out list.",
        request_id=request_id,
        processed_at=datetime.utcnow(),
    )


@router.post(
    "/consents/delete",
    summary="Delete personal data (Right to erasure)",
    description="""
    Process a GDPR right to erasure (deletion) request.

    This permanently removes all personal data associated with the email.
    """,
)
async def delete_data(
    request: ConsentRevokeRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """
    Delete all data for a lead (GDPR right to erasure).

    Args:
        request: Data deletion request
        db: Database session
        api_key: Validated API key

    Returns:
        Confirmation of deletion
    """
    # Find lead by email
    lead = db.query(Lead).filter(Lead.email == request.email).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No lead found with email {request.email}",
        )

    request_id = uuid4()

    # Log the deletion request BEFORE deleting
    log = Log(
        action="data_deleted",
        lead_id=lead.id,
        timestamp=datetime.utcnow(),
        details={
            "email": request.email,
            "request_id": str(request_id),
            "reason": request.reason,
        },
    )
    db.add(log)
    db.commit()

    # Delete the lead (cascade will delete related records)
    db.delete(lead)
    db.commit()

    return {
        "success": True,
        "message": f"All data for {request.email} has been permanently deleted.",
        "request_id": request_id,
        "processed_at": datetime.utcnow(),
    }
