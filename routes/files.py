from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, current_app
import os
import subprocess
import logging
from datetime import datetime

files_bp = Blueprint('files', __name__)

# Serve uploaded files - VULNERABLE: No access control
@files_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# File browser for uploaded files - VULNERABLE: Directory traversal
@files_bp.route('/browse_files')
def browse_files():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # VULNERABILITY: No access control, anyone can browse uploaded files
    path = request.args.get('path', 'uploads')
    
    try:
        # VULNERABILITY: Directory traversal possible
        if not os.path.exists(path):
            flash('Directory not found', 'error')
            return redirect(url_for('index'))
        
        files = []
        dirs = []
        
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append({
                    'name': item,
                    'size': os.path.getsize(item_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return render_template('browse_files_real.html', 
                             files=files, 
                             dirs=dirs, 
                             current_path=path,
                             parent_path=os.path.dirname(path) if path != 'uploads' else None)
                             
    except Exception as e:
        flash(f'Error browsing directory: {str(e)}', 'error')
        return redirect(url_for('index'))

# Execute uploaded files - EXTREME VULNERABILITY
@files_bp.route('/execute_file')
def execute_file():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    filename = request.args.get('file')
    if not filename:
        flash('No file specified', 'error')
        return redirect(url_for('files.browse_files'))
    
    # CRITICAL VULNERABILITY: Execute any uploaded file
    file_path = os.path.join('uploads', filename)
    
    if not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect(url_for('files.browse_files'))
    
    try:
        # VULNERABILITY: Execute files without validation
        if filename.endswith('.py'):
            result = subprocess.run(['python3', file_path], 
                                  capture_output=True, text=True, timeout=10)
        elif filename.endswith('.sh'):
            result = subprocess.run(['bash', file_path], 
                                  capture_output=True, text=True, timeout=10)
        elif filename.endswith('.php'):
            result = subprocess.run(['php', file_path], 
                                  capture_output=True, text=True, timeout=10)
        else:
            # Try to execute as script anyway
            result = subprocess.run([file_path], 
                                  capture_output=True, text=True, timeout=10)
        
        output = result.stdout + result.stderr
        
        # Log the execution attempt
        logging.info(f"FILE_EXECUTION - User: {session.get('username')} | "
                   f"File: {filename} | "
                   f"IP: {request.remote_addr} | "
                   f"Output: {output[:200]}")
        
        flash(f'Execution completed. Output: {output[:500]}', 'info')
        
    except subprocess.TimeoutExpired:
        flash('Execution timed out', 'error')
    except Exception as e:
        flash(f'Execution failed: {str(e)}', 'error')
    
    return redirect(url_for('files.browse_files'))