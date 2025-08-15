from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
from models.database import get_db_connection

cart_bp = Blueprint('cart', __name__)

# Add to cart (modified to prevent negative quantities)
@cart_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    product_id = request.form['product_id']
    try:
        quantity = int(request.form['quantity'])
        if quantity <= 0:
            flash('Quantity must be at least 1', 'error')
            return redirect(url_for('cart.cart'))
    except ValueError:
        flash('Invalid quantity', 'error')
        return redirect(url_for('cart.cart'))
    
    # Price manipulation vulnerability remains
    price = float(request.form.get('price', 0))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        # Check if item already in cart
        c.execute("SELECT * FROM cart WHERE user_id = ? AND product_id = ?", 
                 (session['user_id'], product_id))
        item = c.fetchone()
        
        if item:
            new_quantity = item[3] + quantity
            if new_quantity <= 0:
                flash('Quantity must be at least 1', 'error')
            else:
                c.execute("UPDATE cart SET quantity = ? WHERE id = ?", 
                         (new_quantity, item[0]))
                flash('Cart updated!', 'success')
        else:
            if quantity <= 0:
                flash('Quantity must be at least 1', 'error')
            else:
                c.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                          (session['user_id'], product_id, quantity))
                flash('Item added to cart!', 'success')
        
        conn.commit()
    except sqlite3.Error as e:
        flash('An error occurred', 'error')
        current_app.logger.error(f"Cart error: {e}")
    finally:
        conn.close()
    
    return redirect(url_for('cart.cart'))

# Remove from cart (modified)
@cart_bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    product_id = request.form['product_id']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    try:
        # First get current quantity
        c.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?",
                 (session['user_id'], product_id))
        current_qty = c.fetchone()
        
        if current_qty:
            new_quantity = current_qty[0] - 1
            if new_quantity <= 0:
                # Remove item completely if quantity would be 0
                c.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?",
                         (session['user_id'], product_id))
                flash('Item removed from cart', 'success')
            else:
                # Decrease quantity by 1
                c.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                         (new_quantity, session['user_id'], product_id))
                flash('Quantity decreased', 'success')
        else:
            flash('Item not found in cart', 'error')
            
        conn.commit()
    except sqlite3.Error as e:
        flash('An error occurred', 'error')
        current_app.logger.error(f"Cart error: {e}")
    finally:
        conn.close()
    
    return redirect(url_for('cart.cart'))

# Update cart
@cart_bp.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('auth.login'))
    
    # Get and validate action
    action = request.form.get('action')
    if action not in ['update', 'remove']:
        flash('Invalid action', 'error')
        return redirect(url_for('cart.cart'))
    
    # Validate product_id
    product_id = request.form.get('product_id')
    if not product_id:
        flash('Invalid product', 'error')
        return redirect(url_for('cart.cart'))
    
    try:
        product_id = int(product_id)
    except ValueError:
        flash('Invalid product', 'error')
        return redirect(url_for('cart.cart'))
    
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        if action == 'update':
            # Validate quantity
            try:
                quantity = int(request.form.get('quantity', 1))
                if quantity < 1 or quantity > 99:
                    flash('Quantity must be between 1 and 99', 'error')
                    return redirect(url_for('cart.cart'))
                
                # Update quantity in cart
                c.execute("""UPDATE cart SET quantity = ? 
                            WHERE user_id = ? AND product_id = ?""",
                         (quantity, session['user_id'], product_id))
                flash('Cart updated successfully', 'success')
                
            except ValueError:
                flash('Invalid quantity', 'error')
                return redirect(url_for('cart.cart'))
                
        elif action == 'remove':
            # Remove item from cart
            c.execute("""DELETE FROM cart 
                        WHERE user_id = ? AND product_id = ?""",
                     (session['user_id'], product_id))
            flash('Item removed from cart', 'success')
        
        conn.commit()
        
    except sqlite3.Error as e:
        current_app.logger.error(f"Database error in update_cart: {str(e)}")
        flash('An error occurred while updating your cart', 'error')
        if conn:
            conn.rollback()
            
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('cart.cart'))

# View cart
@cart_bp.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''SELECT products.id, products.name, products.price, cart.quantity, 
                 (products.price * cart.quantity) as total
                 FROM cart JOIN products ON cart.product_id = products.id
                 WHERE cart.user_id = ?''', (session['user_id'],))
    cart_items = c.fetchall()
    
    total = sum(item[4] for item in cart_items)
    conn.close()
    
    return render_template('cart.html', cart_items=cart_items, total=total)

# Checkout (vulnerable to price manipulation)
@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Get cart items
        c.execute('''SELECT cart.id, cart.product_id, cart.quantity, products.price
                     FROM cart JOIN products ON cart.product_id = products.id
                     WHERE cart.user_id = ?''', (session['user_id'],))
        cart_items = c.fetchall()
        
        # Process each item (price manipulation possible)
        for item in cart_items:
            # Client could modify the price before checkout
            price = float(request.form.get(f'price_{item[0]}', item[3]))
            
            c.execute("INSERT INTO orders (user_id, product_id, quantity, price, status) VALUES (?, ?, ?, ?, ?)",
                      (session['user_id'], item[1], item[2], price, 'Processing'))
            
            # Remove from cart
            c.execute("DELETE FROM cart WHERE id = ?", (item[0],))
        
        conn.commit()
        conn.close()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('cart.orders'))
    
    # GET request - show checkout page
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''SELECT cart.id, products.id, products.name, products.price, cart.quantity, 
                 (products.price * cart.quantity) as total
                 FROM cart JOIN products ON cart.product_id = products.id
                 WHERE cart.user_id = ?''', (session['user_id'],))
    cart_items = c.fetchall()
    
    total = sum(item[5] for item in cart_items)
    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

# Order history
@cart_bp.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''SELECT orders.id, products.name, orders.quantity, orders.price, 
                 (orders.quantity * orders.price) as total, orders.status, products.image
                 FROM orders JOIN products ON orders.product_id = products.id
                 WHERE orders.user_id = ?''', (session['user_id'],))
    orders = c.fetchall()

    conn.close()
    return render_template('orders.html', orders=orders)
