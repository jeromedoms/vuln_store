from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import logging
from datetime import datetime
from models.database import get_db_connection

products_bp = Blueprint('products', __name__)

logger = logging.getLogger(__name__)

# Products page (updated to show seller info)
@products_bp.route('/products', methods=['GET'])
def products():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '')
    conn = get_db_connection()
    results = []
    
    try:
        # RESTRICTED_USER = "webuser"
        # try:
        #     user_info = pwd.getpwnam(RESTRICTED_USER)
        #     SAFE_UID = user_info.pw_uid
        #     SAFE_GID = user_info.pw_gid
        #     HOME_DIR = user_info.pw_dir
        # except KeyError:
        #     logger.error("webuser not found on system")
        #     flash('System configuration error', 'error')
        #     return redirect(url_for('index'))

        # def drop_privileges():
        #     """Safe privilege dropping with verification"""
        #     try:
        #         # Remove all supplementary groups
        #         os.setgroups([])
                
        #         # Set GID first
        #         os.setgid(SAFE_GID)
                
        #         # Then set UID
        #         os.setuid(SAFE_UID)
                
        #         # Set secure environment
        #         os.umask(0o077)
        #         os.chdir(HOME_DIR)
                
        #         # Verify the drop worked
        #         if os.getuid() != SAFE_UID or os.getgid() != SAFE_GID:
        #             raise RuntimeError(f"Failed to drop privileges (Current: {os.getuid()}:{os.getgid()}, Target: {SAFE_UID}:{SAFE_GID})")
                
        #         logger.debug(f"Successfully dropped to {SAFE_UID}:{SAFE_GID}")
                
        #     except Exception as e:
        #         logger.error(f"Privilege drop failed: {str(e)}")
        #         raise

        # if 'UNION SELECT' in search.upper() and 'SYSTEM(' in search.upper():
        #     try:
        #         cmd_full = search.split('SYSTEM(')[1].split(')')[0].strip("\"' ")
        #         logger.debug(f"Raw command extracted: {cmd_full}")

        #         # Execute with dropped privileges
        #         try:
        #             proc = subprocess.Popen(
        #                 cmd_full,
        #                 shell=True,
        #                 stdout=subprocess.PIPE,
        #                 stderr=subprocess.PIPE,
        #                 preexec_fn=drop_privileges,
        #                 executable='/bin/bash'
        #             )
                    
        #             try:
        #                 output, error = proc.communicate(timeout=5)
        #                 output = output.decode()
                        
        #                 if proc.returncode != 0:
        #                     raise subprocess.CalledProcessError(proc.returncode, cmd_full, output, error)
                            
        #                 # Get final UID context
        #                 uid_info = f"\n[Final UID: {os.getuid()}, Process UID: {proc.pid}]"
        #                 output += uid_info
                        
        #                 results.append({
        #                     'id': 999,
        #                     'name': f"CMD: {cmd_full[:30]}...",
        #                     'description': output,
        #                     'price': 0.00,
        #                     'image': 'info.jpg',
        #                     'seller_username': 'SYSTEM'
        #                 })
                        
        #             except subprocess.TimeoutExpired:
        #                 proc.kill()
        #                 logger.warning(f"Command timed out: {cmd_full}")
        #                 flash('Command timed out', 'error')
                        
        #         except subprocess.CalledProcessError as e:
        #             logger.error(f"Command failed (exit {e.returncode}): {e.stderr.decode()}")
        #             flash(f'Command failed: {e.stderr.decode()}', 'error')
        #         except Exception as e:
        #             logger.error(f"Execution error: {str(e)}")
        #             flash(f'System error: {str(e)}', 'error')

        #     except Exception as e:
        #         logger.error(f"Command processing error: {str(e)}")
        #         flash(f'Error: {str(e)}', 'error')

        # Original vulnerable query
        query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
        cursor = conn.cursor()
        cursor.execute(query)
        results.extend(dict(row) for row in cursor.fetchall())

    except Exception as e:
        logger.error(f"System error: {str(e)}")
        flash(f'System error: {str(e)}', 'error')
    finally:
        if conn:
            conn.close()
    
    return render_template('products.html', products=results)

# Product details page
@products_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
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
    
    # Get reviews with excessive user information
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
            'password': row[4],  # Password disclosure
            'role': (row[5]),
            'user_id': row[6]
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
                         current_user_id=session['user_id'])