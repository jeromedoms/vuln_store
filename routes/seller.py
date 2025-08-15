from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
import os
import logging
from datetime import datetime
from models.database import get_db_connection
from utils.validation import allowed_file

seller_bp = Blueprint('seller', __name__)

# Seller Dashboard
@seller_bp.route('/seller_dashboard')
def seller_dashboard():
    if 'user_id' not in session or session.get('role') != 'seller':
        flash('Access denied. Seller account required.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get seller's products
    c.execute('''SELECT id, name, description, price, image, status, created_at 
                 FROM products WHERE seller_id = ? ORDER BY created_at DESC''', 
              (session['user_id'],))
    products = c.fetchall()
    
    # Get order statistics
    c.execute('''SELECT COUNT(*) as total_orders, SUM(orders.quantity * orders.price) as total_revenue
                 FROM orders 
                 JOIN products ON orders.product_id = products.id 
                 WHERE products.seller_id = ?''', (session['user_id'],))
    stats = c.fetchone()
    
    conn.close()
    
    return render_template('seller_dashboard.html', 
                         products=products, 
                         stats=stats or {'total_orders': 0, 'total_revenue': 0})

# Add new product (VULNERABLE file upload)
@seller_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session.get('role') != 'seller':
        flash('Access denied. Seller account required.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_type = request.form['image_type']  # 'file' or 'url'
        
        image_path = ''
        
        if image_type == 'url':
            image_path = request.form['image_url']
        else:
            # File upload handling - VULNERABLE
            if 'image_file' not in request.files:
                flash('No file selected', 'error')
                return render_template('add_product.html')
            
            file = request.files['image_file']
            
            if file.filename == '':
                flash('No file selected', 'error')
                return render_template('add_product.html')
            
            # VULNERABILITY: Weak file validation
            if file and allowed_file(file.filename):
                # VULNERABILITY: Using original filename without proper sanitization
                filename = file.filename
                
                # VULNERABILITY: No duplicate filename handling
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    file.save(file_path)
                    image_path = f'/uploads/{filename}'
                    
                    # Log the upload for demonstration
                    logging.info(f"FILE_UPLOAD - User: {session.get('username')} | "
                               f"Filename: {filename} | "
                               f"Path: {file_path} | "
                               f"IP: {request.remote_addr}")
                    
                except Exception as e:
                    flash(f'File upload failed: {str(e)}', 'error')
                    return render_template('add_product.html')
            else:
                flash('Invalid file type. Only images are allowed.', 'error')
                return render_template('add_product.html')
        
        # Save product to database
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO products (name, description, price, image, seller_id, status, created_at) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (name, description, price, image_path, session['user_id'], 'active', 
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('seller.seller_dashboard'))
            
        except sqlite3.Error as e:
            flash('Database error occurred', 'error')
            current_app.logger.error(f"Product creation error: {e}")
        finally:
            conn.close()
    
    return render_template('add_product.html')

# Edit product
@seller_bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('role') != 'seller':
        flash('Access denied. Seller account required.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verify ownership
    c.execute("SELECT * FROM products WHERE id = ? AND seller_id = ?", 
              (product_id, session['user_id']))
    product = c.fetchone()
    
    if not product:
        flash('Product not found or access denied', 'error')
        conn.close()
        return redirect(url_for('seller.seller_dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        status = request.form['status']
        
        try:
            c.execute('''UPDATE products SET name = ?, description = ?, price = ?, status = ? 
                         WHERE id = ? AND seller_id = ?''',
                     (name, description, price, status, product_id, session['user_id']))
            conn.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('seller.seller_dashboard'))
            
        except sqlite3.Error as e:
            flash('Update failed', 'error')
            current_app.logger.error(f"Product update error: {e}")
    
    conn.close()
    return render_template('edit_product.html', product=product)

# Seller Orders - view orders for seller's products
@seller_bp.route('/seller_orders')
def seller_orders():
    if 'user_id' not in session or session.get('role') != 'seller':
        flash('Access denied. Seller account required.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get orders for seller's products
    c.execute('''SELECT o.id, p.name, u.username as buyer, o.quantity, o.price, 
                 (o.quantity * o.price) as total, o.status
                 FROM orders o
                 JOIN products p ON o.product_id = p.id
                 JOIN users u ON o.user_id = u.id
                 WHERE p.seller_id = ?
                 ORDER BY o.id DESC''', (session['user_id'],))
    seller_orders = c.fetchall()
    
    conn.close()
    return render_template('seller_orders.html', orders=seller_orders)