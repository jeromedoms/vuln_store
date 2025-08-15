from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import subprocess
import shlex
import logging
from utils.helpers import log_action
import random

admin_bp = Blueprint('admin', __name__)


# FAKE directory structure bait (5+ levels deep with multiple branches)
@admin_bp.route('/backup', methods=['GET'])
def level1():
    # if 'user_id' not in session or not session.get('role') == 'admin':
    #     return render_template('unauthorized.html')
    return render_template('backups_listing.html',
                         files=[('readme', '/backup/readme'), 
                                ('wordlist.txt', '/backup/wordlist.txt')],
                         title="/backup")

@admin_bp.route('/shop_admin/portal', methods=['GET'])
def level2():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('unauthorized.html')
    
    # For directories - can be strings or tuples
    directories = [
        'backup',                                  
        'modules',
        ('console', '/shop_admin/portal/console')            
    ]
    
    # For files - can be strings or tuples
    files = [
        'access.log',                               # string with default path
        ('portal_config.ini', '/shop_admin/portal/portal_config.ini')  # tuple with custom path
    ]
    
    return render_template('backups_listing.html',
                         directories=directories,
                         files=files,
                         title="/shop/admin/portal")

@admin_bp.route('/shop_admin/portal/console', methods=['GET'])
def level3():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('unauthorized.html')
    return render_template('backups_listing.html',
                         directories=[
                             ('access', '/shop_admin/portal/console/access'),
                             'logs', 'tmp'],
                         files=['console.php', 'auth_check.js'],
                         title = "/shop_admin/portal/console")

@admin_bp.route('/shop_admin/portal/console/access', methods=['GET'])
def level4():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('unauthorized.html')
    return render_template('gif.html', gif_url="https://media1.tenor.com/m/0q4lN1_ApMoAAAAC/dory-marlin.gif")

@admin_bp.route('/shop_admin/portal/console/access/admin', methods=['GET'])
def level5():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('unauthorized.html')
    return render_template('gif.html', 
                           gif_url="https://media1.tenor.com/m/8fvOMOKsG0YAAAAd/mia-mia-o-brien.gif", 
                           message="https://gchq.github.io/CyberChef/#input=Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSV01WbDNXa1JTV0ZKdGVGWlZiVFZyVmxVeFYyTkljRmhoTVhCUVZqQmFZV015U2tWVWJHaG9UV3N3ZUZacVFtRlRNazE1VTJ0V1ZXSkhhRzlVVjNOM1pVWmFkR05GU214U2JHdzFWVEowVjFaWFNraGhSemxWVmpOT00xcFZXbUZrUjA1R1UyMTRVMkpIZHpGV1ZFb3dWakZhV0ZOcmFHaFNlbXhXVm0xNFlVMHhXbk5YYlVaclVqQTFSMWRyV25kV01ERkZVbFJHVjFaRmIzZFdha1poVjBaT2NtRkhhRk5sYlhoWFZtMHhORmxWTUhoWGJrNVlZbFZhY2xWcVFURlNNV1J5VjI1a1YwMUVSa1pWYkZKSFZqRmFSbUl6WkZkaGExcG9WakJhVDJOdFNrZFRiV3hUVFcxb1dsWXhaRFJpTWtsM1RVaG9XR0pIVWxsWmJGWmhZMnhXYzFWclpGaGlSM1F6VjJ0U1UxWnJNWEpqUm1oV1RXNVNNMVpxU2t0V1ZrcFpXa1p3YkdFelFrbFhXSEJIVkRKU1YxWnVUbGhpVjJoeldXeG9iMkl4V25STldHUlZUV3RzTlZWdGRHdGhiRXAwVld4c1dtSkdXbWhaTVZwaFpFZE9ObEp0ZUZOaVNFSmFWMnhXYjJFeFdYZE5WVlpUWVRGd1YxbHJXa3RUUmxweFUydGFiRlpzV2xwWGExcDNZa2RGZWxGcmJGZFdNMEpJVmtSS1UxWXhWblZWYlhCVFlrVndWVlp0ZUc5Uk1XUnpWMjVLV0dKSFVtRldha1pIVGtaYVNHUkhkRmRpVlhCSVZqSjRVMWR0U2tkWGJXaGFUVlp3ZWxreU1VZFNiRkp6Vkcxc1UySnJTbUZXTW5oWFdWWlJlRmRzYUZSaVJuQnhWV3hrVTFsV1VsWlhiVVpPVFZad2VGVXlkREJXTVZweVkwWndXR0V4Y0ROV2FrWkxWMVpHY21KR1pGZE5NRXBKVm10U1MxVXhXWGhYYmxaV1lsZG9WRmxZY0Zka01WcHhVVzEwYVUxWFVsaFdNalZMVjBkS1NGVnRSbGRpVkVVd1ZqQmFZVmRIVWtoa1JtUk9ZVE5DTlZaSGVHRmpNV1IwVTJ0b2FGSnNTbGhVVlZwM1ZrWmFjVkp0ZEd0U2EzQXdXbFZhYTJGWFJYZGpSV3hYWWxoQ1RGUnJXbEpsUm1SellVWlNhRTFzU25oV1YzUlhVekpHUjFaWVpHaFNWVFZVVlcxNGQyVkdWblJOVldSV1RXdHdWMVp0Y0dGWGJGcFhZMGRvV2xaWFVrZGFWV1JQVTBkR1IyRkhiRk5pYTBwMlZtMTBVMU14VVhsVmEyUlZZbXR3YUZWdGVFdGpSbHB4VkcwNVYxWnNjRWhYVkU1dllWVXhXRlZ1Y0ZkTlYyaDJWMVphUzFJeFRuVlJiRlpYWWtoQ1dWWkdVa2RWTVZwMFVtdG9VRlp0YUZSWmJGcExVMnhrVjFadFJtcE5WMUl3VlRKMGExZEhTbGhoUjBaVlZteHdNMWxWV25kU2JIQkhWR3hTVTJFelFqVldSM2hoVkRKR1YxTnVVbEJXUlRWWVZGYzFiMWRHYkhGVGExcHNVbTFTV2xkclZURldNa3BYVTI1b1YxWXphSEpaYWtaclVqRldjMXBIUmxObGJYaDRWMWQwWVdReVZrZFdibEpzVTBkU2NGVnFRbmRXTVZsNVpFaGtWMDFFUm5oVmJYUnZWakZhUmxkcmVGZE5WbkJJV1RJeFMxSXhjRWRhUlRWT1VsaENTMVp0TVRCVk1VMTRWbGhvV0ZkSGFGbFpiWGhoVm14c2NscEhPV3BTYkhCNFZrY3dOVll4V25SVmJHaFhWak5OTVZaWGMzaGpiVXBGVld4a1RsWXlhREpXTVZwaFV6RktjMVJ1VWxOaVIxSnZXVlJHZDFOV1draGtSMFphVm0xU1NWWlhkRzloTVVwMFZXczVWMkZyV2t4Vk1uaHJWakZhZEZKdGNFNVdNVWwzVmxSS01HSXlSa2RUYms1VVlrZG9WbFpzV25kTk1WcHlWMnh3YTAxWVFraFdSM2hUVlRKRmVsRnFXbGRpUjFFd1dWUktSMVl4Y0VaYVJrNW9Za2hDV1ZkWGVHOVJNVkpIVld4YVdHSkZjSE5WYlRGVFYyeGtjbFpVUmxoU2EzQmFWVmQ0YzFkR1duUlZhbHBWVm14d2VsWnFSbGRqTVdSellVZHNhVlpyY0ZwV2JHTjRUa2RSZVZaclpGZGliRXBQVm14a1UxZEdVbFpWYTJSc1ZteEtlbFp0TURWV01ERldZbnBLVm1KWVVuWldha1poVW14a2NtVkdaR2hoTTBKUlZsY3hORmxYVFhoalJXaHBVbXMxVDFac1dscGxiRnAwWlVkR1ZrMVZiRFJaYTFwclYwZEtjbU5GT1ZkaVdHZ3pWakJhYzFkWFRrZGFSbVJUWWtad05WWnRNVEJaVmxGNFZteFdUbEpIY3pr")

# Decoy files that look interesting
@admin_bp.route('/backup/readme', methods=['GET'])
def readme():
    return "Your pain is what we desire\n" \
    "932ce4927018134c8c3011cf0cdfef863b34707fe86fd6ace8f798878511deda", 200, {'Content-Type': 'text/plain'}

@admin_bp.route('/backup/wordlist.txt', methods=['GET'])
def wordlist():
    return """...
sanetheyte
llyougiven
withthebes
tintention
...""", 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=wordlist.txt'
    }

@admin_bp.route('/shop_admin/portal/portal_config.ini', methods=['GET'])
def decoy_config():
    return "[TIBERIUS CEASAR]\nUva hss kpyljavyplz hyl zllu ha mpyza nshujl. Ayhclyzl lhjo whao huk lehtpul doha splz ilulhao.", 200, {'Content-Type': 'text/plain'}

@admin_bp.route('/shop_admin/backup', methods=['GET'])
def fake_backup():
    # Define the directories and files to display
    directories = [ 'portal', 'archives', 'system',  'logs', 'credentials'
    ]
    
    files = ['config.ini', 'error.log', 'master.key', 'user_passwords.csv','production.db', 'backup_2024.zip', 'admin_settings.json']
    
    return render_template(
        'backups_listing.html',
        directories=directories,
        files=files,
        title="Index of /shop_admin/backup/"
    )


@admin_bp.route('/shop_admin/view_backup', methods=['GET'])
def view_backup():
    # Log the attempt (optional)
    requested_file = request.args.get('path', '')
    print(f"Someone tried to access backup file: {requested_file}")
    
    # Redirect to rickroll
    return redirect("https://youtu.be/dQw4w9WgXcQ")

@admin_bp.route('/.git', methods=['GET'])
def fake_dotgit():
    return render_template('gif.html', gif_url="https://media1.tenor.com/m/wCsDiqyFZtMAAAAd/bunny-git-gud.gif")

# Fake Admin Page
@admin_bp.route('/admin', methods=['GET'])
def fakeAdmin():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('unauthorized.html')
    
    return render_template('gif.html', gif_url="https://c.tenor.com/aSkdq3IU0g0AAAAC/tenor.gif")
    
@admin_bp.route('/shop_admin', methods=['GET'])
def wayAdmin():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('gif.html', gif_url="https://c.tenor.com/v7QTgi60NuUAAAAd/tenor.gif")
    
    return render_template('thewae.html')

# Admin panel with command injection vulnerability
@admin_bp.route('/shop_admin/whyYouMad', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or not session.get('role') == 'admin':
        return render_template('unauthorized.html')

    # Allowed commands and paths configuration
    ALLOWED_COMMANDS = {
        'whoami': 'Show current user',
        'id': 'Show user identity',
        'date': 'Show current date/time',
        'hostname': 'Show system hostname',
        'uptime': 'Show system uptime',
        'uname': 'Show system information (uname -a)',
        'pwd': 'Show current directory',
        'echo': 'Echo input (echo [text])',
        'head': 'View first 10 lines of file (head [file])',
        'tail': 'View last 10 lines of file (tail [file])',
        'ls': 'List directory contents (ls [path])',
        'cat': 'View file contents (cat [file])',
        'file': 'Determine file type (file [filename])',
        'stat': 'Display file status (stat [file])',
        'wc': 'Count lines/words (wc [file])'
    }

    ALLOWED_PATHS = [
        os.getcwd(),  # Current directory
        '/usr',       # System binaries
        '/var/log',   # Log files
        '/tmp'        # Temporary files
    ]

    def is_path_allowed(path):
        """Check if path is within allowed directories, including subdirs of working dir"""
        try:
            abs_path = os.path.abspath(path)
            # Allow: (1) Exact allowed paths, (2) Subdirs of working directory
            return (any(abs_path.startswith(os.path.abspath(allowed)) for allowed in ALLOWED_PATHS) or 
                    abs_path.startswith(os.getcwd()))
        except:
            return False

    def validate_command(cmd):
        if not cmd:
            return False
            
        parts = shlex.split(cmd)  # Safer than simple split()
        if not parts:
            return False
            
        base_cmd = parts[0]
        
        # Block disallowed commands
        if base_cmd not in ALLOWED_COMMANDS:
            return False
           
        # Block dangerous characters
        dangerous_chars = [';', '&', '|', '`', '', '>', '<', '(', ')', '{', '}', '[', ']', '\\']
        if any(char in cmd for char in dangerous_chars):
            return False
            
        # Block dangerous patterns
        dangerous_patterns = [
            'sudo', 'su', 'bash', 'sh', 'python', 'perl', 'nc', 'netcat',
            'ssh', 'scp', 'wget', 'curl', 'ftp', 'telnet', 'rm', 'mv',
            'chmod', 'chown', 'dd', 'kill', 'exec', 'system'
        ]
        if any(pattern in base_cmd.lower() for pattern in dangerous_patterns):
            return False
            
        # Validate file paths for file operations
        file_commands = ['head', 'tail', 'ls', 'cat', 'file', 'stat', 'wc']
        if base_cmd in file_commands and len(parts) > 1:
            # Get the last argument (assumed to be file path)
            file_path = parts[-1]
            
            # Handle relative paths
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
                
            if not is_path_allowed(file_path):
                return False
                
            # Additional check for parent directory traversal
            if '../' in file_path or '/..' in file_path:
                return False
                
        return True

    output = ""
    if request.method == 'POST':
        command = request.form.get('command', '').strip()
        
        if not validate_command(command):
            output = f"Error: Command not allowed or invalid - {command}"
        else:
            try:
                # Execute with restricted permissions
                result = subprocess.run(
                    ['sudo', '-u', 'restricted_user', 'bash', '-c', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                    cwd=os.getcwd()  # Set working directory
                )
                output = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
                
            except subprocess.TimeoutExpired:
                output = "Error: Command timed out (max 3 seconds)"
            except Exception as e:
                output = f"Error: {str(e)}"
                
        log_action('ADMIN_COMMAND', {
            'user': session.get('username'),
            'command': command,
            'output': output[:200],  # Truncate long outputs
            'allowed': validate_command(command),
            'ip': request.remote_addr
        })

    return render_template(
        'admin.html',
        output=output,
        allowed_commands=ALLOWED_COMMANDS,
        current_directory=os.getcwd(),
        allowed_paths=", ".join(ALLOWED_PATHS)
    )