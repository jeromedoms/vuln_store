from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import bcrypt
from models.database import get_db_connection
from config import Config

auth_bp = Blueprint('auth', __name__)

# Login page
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            
            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    flash('Login successful!', 'success')
                    
                    # Redirect based on role
                    if user['role'] == 'seller':
                        return redirect(url_for('seller.seller_dashboard'))
                    elif user['role'] == 'admin':
                        return redirect(url_for('admin.admin'))
                    else:
                        return redirect(url_for('products.products'))
                else:
                    flash('Wrong password for this username', 'error')
            else:
                flash('Username does not exist', 'error')
        finally:
            conn.close()
    
    return render_template('login.html')

# Registration page with seller option
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'customer')
        
        # Validate role
        if role not in ['customer', 'seller']:
            role = 'customer'
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        try:
            # VULNERABLE: Check all password hashes for matches (very slow but works)
            c.execute("SELECT username, password FROM users")
            existing_users = c.fetchall()
            
            for user in existing_users:
                # Try to verify against each stored hash
                if bcrypt.checkpw(password.encode('utf-8'), user[1]):
                    flash(f'Password has been used by: {user[0]}', 'error')
                    return render_template('register.html')
            
            # Check if username exists
            c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if c.fetchone():
                flash('Username already exists', 'error')
                return render_template('register.html')
            
            # Hash with new random salt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=4))
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                     (username, hashed_password, role))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except sqlite3.Error as e:
            flash('An error occurred during registration', 'error')
            
        finally:
            conn.close()
    
    return render_template('register.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))