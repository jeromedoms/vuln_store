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

    # Base commands allowed (arguments can be added freely)
    ALLOWED_BASE_COMMANDS = [
        'whoami',
        'date',
        'pwd',
        'ls',
        'tail',
        'nslookup',
        'base64',
        'man'
    ]

    # Allowed base paths (absolute paths only)
    ALLOWED_BASE_PATHS = [
        '/home/ctfuser',  # CTF user home directory
        '/tmp',  # Temporary directory
        '/var/log'  # Log directory
    ]
    
    # Blocked paths specifically for tail command
    BLOCKED_PATHS_FOR_TAIL = [
        '/home/ctfuser/vulnstore_repo/vuln_store',
        '/vulnstore_repo/vuln_store'
    ]

    def validate_command(cmd):
        print(f"\n[VALIDATION] Checking command: '{cmd}'")
        
        # Block dangerous characters that could enable command chaining
        dangerous_chars = [';', '&', '|', '`', '>', '<', '(', ')', '{', '}', '[', ']', '\\', '$', '\n']
        if any(char in cmd for char in dangerous_chars):
            print(f"[VALIDATION FAILED] Dangerous character detected")
            return False
        
        # Block path traversal
        if '../' in cmd or '/..' in cmd:
            print(f"[VALIDATION FAILED] Path traversal detected")
            return False
            
        # Extract base command
        base_cmd = cmd.split()[0] if cmd else ''
        if base_cmd not in ALLOWED_BASE_COMMANDS:
            print(f"[VALIDATION FAILED] Command not in whitelist")
            return False
            
        # Check all paths in command are allowed
        for part in cmd.split()[1:]:  # Skip command itself
            if part.startswith('-'):
                continue  # Skip command options
                
            # Special check for tail command
            if base_cmd == 'tail' and is_path_blocked_for_tail(part):
                print(f"[VALIDATION FAILED] Tail command not allowed on path: {part}")
                return False
                
            if not is_path_allowed(part):
                print(f"[VALIDATION FAILED] Path not allowed: {part}")
                return False
                
        print("[VALIDATION PASSED] Command allowed")
        return True

    def is_path_allowed(path):
        """Check if path is within allowed directories"""
        try:
            # Handle relative paths
            if not path.startswith('/'):
                path = os.path.normpath(os.path.join('/home/ctfuser', path))
            
            abs_path = os.path.abspath(path)
            
            # Check if path is within any allowed base path
            return any(abs_path.startswith(os.path.abspath(base)) for base in ALLOWED_BASE_PATHS)
        except:
            return False
            
    def is_path_blocked_for_tail(path):
        """Check if path is blocked specifically for tail command"""
        try:
            # Handle relative paths
            if not path.startswith('/'):
                path = os.path.normpath(os.path.join('/home/ctfuser', path))
            
            abs_path = os.path.abspath(path)
            
            # Check if path is within any blocked path for tail
            return any(abs_path.startswith(os.path.abspath(base)) for base in BLOCKED_PATHS_FOR_TAIL)
        except:
            return False
            
    output = ""
    if request.method == 'POST':
        command = request.form.get('command', '').strip()
        print(f"\n[INPUT] Received command: '{command}'")

        if not validate_command(command):
            output = f"Error: Command not allowed - {command}"
            print(f"[REJECTED] {command}")
        else:
            try:
                print(f"[EXECUTING] Running: '{command}'")
                
                # Restrict environment
                env = os.environ.copy()
                env['PATH'] = '/bin:/usr/bin'  # Minimal PATH
                
                result = subprocess.run(
                    ['sudo', '-u', 'kali', 'bash', '-c', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                    env=env,
                    cwd='/home/kali'
                )
                
                output = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
                print(f"[RESULT] {output[:200]}...")  # Truncate long output
                
            except subprocess.TimeoutExpired:
                output = "Error: Command timed out"
            except Exception as e:
                output = f"Error: {str(e)}"

    # Generate help text for UI
    allowed_commands_help = {
        'whoami': 'Print effective user name',
        'date': 'Show current date/time',
        'pwd': 'Print name of current/working directory',
        'ls': 'List information about the FILEs (the current directory by default).',
        'tail': 'Print the last 10 lines of each FILE to standard output.',
        '***': 'Encode/decode data and print to standard output',
        'nslookup':'Query Internet name servers interactively'
    }

    return render_template(
        'admin.html',
        output=output,
        allowed_commands=allowed_commands_help,
        allowed_paths=", ".join(ALLOWED_BASE_PATHS),
        current_directory=os.getcwd()
    )
