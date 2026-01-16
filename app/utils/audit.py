from sqlalchemy.orm import Session
from app.models.sql import AuditLog

def log_action(db: Session, user_id: str, action: str, resource_id: str, details: str = None):
    audit = AuditLog(
        user_id=user_id,
        action_type=action,
        resource_id=resource_id,
        details=details
    )
    db.add(audit)
    db.commit()
