from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import logging
import os
from datetime import datetime
from models.database import get_db_connection
import pwd
import subprocess

products_bp = Blueprint('products', __name__)

logger = logging.getLogger(__name__)

def get_user_role(user_id):
    """Helper function to get user role"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        return result['role'] if result else None
    finally:
        conn.close()

# Products page (role-based SQL injection vulnerability)
@products_bp.route('/products', methods=['GET'])
def products():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '')
    conn = get_db_connection()
    results = []
    
    # Get current user's role
    user_role = get_user_role(session['user_id'])
    
    try:
        # Get ctfuser info for privilege dropping (only for admin command injection)
        RESTRICTED_USER = "kali"
        try:
            user_info = pwd.getpwnam(RESTRICTED_USER)
            SAFE_UID = user_info.pw_uid
            SAFE_GID = user_info.pw_gid
            HOME_DIR = user_info.pw_dir
        except KeyError:
            logger.error("ctfuser not found on system")
            flash('System configuration error', 'error')
            return redirect(url_for('index'))

        # Debug info (only show for admins)
        if user_role == 'admin':
            results.append({
                'id': 999,
                'name': "DEBUG INFO (ADMIN ONLY)",
                'description': f"Search input: '{search}'\nUpper: '{search.upper()}'\nContains UNION SELECT: {'UNION SELECT' in search.upper()}\nContains SYSTEM(: {'SYSTEM(' in search.upper()}\nUser Role: {user_role}",
                'price': 0.00,
                'image': 'info.jpg',
                'seller_username': 'DEBUG',
                'status': 'active'
            })

        # Command injection payload detection - only for admins
        if user_role == 'admin' and 'SYSTEM(' in search.upper():
            try:
                # Find SYSTEM( in the search string
                upper_search = search.upper()
                system_pos = upper_search.find('SYSTEM(')
                if system_pos != -1:
                    # Extract from original search to preserve case
                    after_system = search[system_pos + 7:]  # 7 = len('SYSTEM(')
                    
                    # Find the closing parenthesis
                    paren_pos = after_system.find(')')
                    if paren_pos != -1:
                        cmd_full = after_system[:paren_pos].strip("\"' ")

                        # Execute command with dropped privileges
                        try:
                            proc = subprocess.Popen(
                                cmd_full,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                executable='/bin/bash',
                                user=SAFE_UID,
                                group=SAFE_GID
                            )
                            
                            try:
                                # For netcat reverse shells, don't wait - they run in background
                                if 'nc ' in cmd_full.lower() and ('-e' in cmd_full or '-c' in cmd_full):
                                    # Give it a moment to establish connection
                                    import time
                                    time.sleep(1)
                                    
                                    if proc.poll() is None:  # Process still running
                                        output = f"Reverse shell command executed successfully!\nProcess PID: {proc.pid}\nCommand: {cmd_full}\nConnection should be established to your listener."
                                    else:
                                        output = f"Reverse shell command completed with exit code: {proc.returncode}"
                                else:
                                    # Normal commands - wait for output
                                    output, error = proc.communicate(timeout=10)
                                    
                                    if proc.returncode != 0 and error:
                                        output = f"Error (exit {proc.returncode}): {error}{output}"
                                    elif not output and not error:
                                        output = "Command executed (no output)"
                                
                                results.append({
                                    'id': 999,
                                    'name': f"CMD RESULT: {cmd_full[:30]}",
                                    'description': output,
                                    'price': 0.00,
                                    'image': 'hacked.jpg',
                                    'seller_username': 'SYSTEM'
                                })
                            
                            except subprocess.TimeoutExpired:
                                proc.kill()
                                results.append({
                                    'id': 997,
                                    'name': f"CMD TIMEOUT",
                                    'description': f"Command '{cmd_full}' timed out after 10 seconds",
                                    'price': 0.00,
                                    'image': 'info.jpg',
                                    'seller_username': 'SYSTEM'
                                })
                        
                        except Exception as e:
                            results.append({
                                'id': 996,
                                'name': f"CMD EXEC ERROR",
                                'description': f"Failed to execute '{cmd_full}': {str(e)}",
                                'price': 0.00,
                                'image': 'info.jpg',
                                'seller_username': 'SYSTEM',
                                'status': 'active'
                            })

            except Exception as e:
                results.append({
                    'id': 995,
                    'name': "CMD PARSE ERROR",
                    'description': f"Failed to parse command: {str(e)}",
                    'price': 0.00,
                    'image': 'info.jpg',
                    'seller_username': 'SYSTEM'
                })

        # Role-based SQL query handling
        try:
            cursor = conn.cursor()
            
            if user_role == 'admin':
                # VULNERABLE: SQL injection for admin users
                query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
                cursor.execute(query)
                
                # Show the vulnerable query to admin for debugging
                results.append({
                    'id': 998,
                    'name': "ADMIN SQL DEBUG",
                    'description': f"Vulnerable Query Used: {query}",
                    'price': 0.00,
                    'image': 'info.jpg',
                    'seller_username': 'DEBUG',
                    'status': 'active'
                })
                
            else:
                # SECURE: Parameterized query for non-admin users
                query = "SELECT * FROM products WHERE name LIKE ?"
                cursor.execute(query, (f'%{search}%',))
            
            db_results = cursor.fetchall()
            
            # Convert to dict format
            for row in db_results:
                results.append(dict(row))
                
        except sqlite3.OperationalError as e:
            if user_role == 'admin':
                # Show SQL error to admin for debugging
                results.append({
                    'id': 995,
                    'name': "SQL ERROR (ADMIN)",
                    'description': f"SQL Error: {str(e)}\nQuery: {query}",
                    'price': 0.00,
                    'image': 'info.jpg',
                    'seller_username': 'DEBUG'
                })
            else:
                # Generic error message for non-admin users
                flash('Search error occurred', 'error')

    except Exception as e:
        logger.error(f"System error: {str(e)}")
        if user_role == 'admin':
            flash(f'System error: {str(e)}', 'error')
        else:
            flash('An error occurred', 'error')
    finally:
        if conn:
            conn.close()
    
    # Add role indicator to template context
    return render_template('products.html', 
                         products=results, 
                         user_role=user_role)

# Product details page
@products_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Get current user's role
    user_role = get_user_role(session['user_id'])
    
    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("INSERT INTO reviews (product_id, user_id, review, rating, created_at) VALUES (?, ?, ?, ?, ?)",
                  (product_id, session['user_id'], review, rating, created_at))
        conn.commit()
        flash('Review added!', 'success')
        return redirect(url_for('products.product_detail', product_id=product_id))
    
    # Get product details with seller info
    c.execute("""SELECT p.*, u.username as seller_username, u.role as seller_role 
                 FROM products p 
                 JOIN users u ON p.seller_id = u.id 
                 WHERE p.id = ?""", (product_id,))
    product = c.fetchone()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('products.products'))
    
    # Role-based review information disclosure
    if user_role == 'admin':
        # Get reviews with excessive user information (intentional info disclosure for CTF - admin only)
        c.execute('''SELECT 
                        reviews.review, 
                        users.username,
                        reviews.rating,
                        reviews.created_at,
                        users.password,
                        users.role,
                        users.id
                     FROM reviews 
                     JOIN users ON reviews.user_id = users.id 
                     WHERE product_id = ? 
                     ORDER BY reviews.created_at DESC''', (product_id,))
        
        reviews = []
        for row in c.fetchall():
            reviews.append({
                'review_text': row[0],
                'username': row[1],
                'rating': row[2],
                'created_at': row[3],
                'password': row[4],  # Password disclosure (intentional for CTF - admin only)
                'role': row[5],
                'user_id': row[6]
            })
    else:
        # Secure review query for non-admin users (no password disclosure)
        c.execute('''SELECT 
                        reviews.review, 
                        users.username,
                        reviews.rating,
                        reviews.created_at
                     FROM reviews 
                     JOIN users ON reviews.user_id = users.id 
                     WHERE product_id = ? 
                     ORDER BY reviews.created_at DESC''', (product_id,))
        
        reviews = []
        for row in c.fetchall():
            reviews.append({
                'review_text': row[0],
                'username': row[1],
                'rating': row[2],
                'created_at': row[3],
                'password': None,  # No password for non-admin users
                'role': None,
                'user_id': None
            })
    
    conn.close()
    
    product_dict = {
        'id': product[0],
        'name': product[1],
        'description': product[2],
        'price': product[3],
        'image': product[4],
        'seller_id': product[5],
        'status': product[6],
        'created_at': product[7],
        'seller_username': product[8],
        'seller_role': product[9]
    }
    
    return render_template('product_detail.html', 
                         product=product_dict, 
                         reviews=reviews,
                         current_user_id=session['user_id'],
                         user_role=user_role)
