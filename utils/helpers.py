import logging
from datetime import datetime
from flask import session, request

logger = logging.getLogger(__name__)

def log_action(action_type, payload=None):
    """Log user actions with all relevant context"""
    user = session.get('username', 'anonymous')
    ip = request.remote_addr
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    logging.info(
        f"ADMIN_CONSOLE "
        f"Timestamp: {timestamp}"
        f"IP: {ip} | "
        f"Payload: {payload if payload else dict(request.args) or dict(request.form)} | "
    )