from flask import current_app

# VULNERABLE: Allow all file types - no proper validation
def allowed_file(filename):
    # Intentionally weak validation - allows dangerous files
    if not filename or '.' not in filename:
        return False
    
    # This check is easily bypassed
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # VULNERABILITY: Allow executables and scripts with image extensions
    dangerous_exts = {'php', 'py', 'sh', 'jsp', 'asp', 'exe', 'bat', 'cmd'}
    if ext in dangerous_exts:
        # Pretend to block but actually allow if disguised
        if any(allowed_ext in filename for allowed_ext in ['jpg', 'png', 'gif']):
            return True  # Allow malicious.php.jpg
        return False
    
    return True  # Allow everything else