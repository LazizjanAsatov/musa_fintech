from .models import AuditLog


def log_admin_action(actor, action, target, metadata=None):
    """Helper function to log admin actions."""
    log = AuditLog.objects.create(
        actor=actor,
        action=action,
        target=target
    )
    if metadata:
        log.set_metadata(metadata)
        log.save()
    return log

