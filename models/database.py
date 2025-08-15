import sqlite3
import bcrypt
from datetime import datetime
import subprocess
from config import Config

# Custom function to execute system commands
def execute_command(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
    except Exception as e:
        return str(e)

# Database connection factory with our custom function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    
    # Create system command execution function
    def system(cmd):
        try:
            return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        except Exception as e:
            return str(e)
    
    conn.create_function("system", 1, system)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create users table with role column
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT,
                 role TEXT DEFAULT 'customer')''')
    
    # Create products table with seller_id
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 description TEXT,
                 price REAL,
                 image TEXT,
                 seller_id INTEGER,
                 status TEXT DEFAULT 'active',
                 created_at TEXT,
                 FOREIGN KEY (seller_id) REFERENCES users (id))''')
    
    # Create cart table
    c.execute('''CREATE TABLE IF NOT EXISTS cart
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 product_id INTEGER,
                 quantity INTEGER)''')
    
    # Create orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 product_id INTEGER,
                 quantity INTEGER,
                 price REAL,
                 status TEXT)''')
    
    # Create reviews table
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_id INTEGER,
                 user_id INTEGER,
                 review TEXT,
                 rating INTEGER,
                 created_at TEXT)''')
    

    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    # Add users with different roles including sellers
    try:
        SALT = Config.SALT
        passwords = {
            'user': bcrypt.hashpw('orionuser'.encode('utf-8'), SALT),
            'admin': bcrypt.hashpw('admin'.encode('utf-8'), SALT),
            'vip': bcrypt.hashpw('vipcustomer'.encode('utf-8'), SALT),
            'test': bcrypt.hashpw('password'.encode('utf-8'), SALT),
            'seller1': bcrypt.hashpw('sellpass'.encode('utf-8'), SALT),
            'seller2': bcrypt.hashpw('merchant123'.encode('utf-8'), SALT)
        }
        
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('user', passwords['user'], 'customer'))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('admin', passwords['admin'], 'admin'))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('test', passwords['test'], 'customer'))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('seller1', passwords['seller1'], 'seller'))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('seller2', passwords['seller2'], 'seller'))
    except sqlite3.IntegrityError:
        pass
    
    # Enhanced mock products from both sellers
    products = [
        # Seller 1 products (seller_id = 4)
        ('Gaming Laptop', 'High-performance gaming laptop with RTX 4070', 1899.99, 'https://images.unsplash.com/photo-1603302576837-37561b2e2302', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Wireless Headphones', 'Premium noise-canceling wireless headphones', 299.99, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('4K Monitor', '27-inch 4K UHD monitor with HDR support', 449.99, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Mechanical Keyboard', 'RGB backlit mechanical gaming keyboard', 129.99, 'https://images.unsplash.com/photo-1541140532154-b024d705b90a', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Gaming Mouse', 'Precision gaming mouse with customizable buttons', 79.99, 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Webcam HD', '1080p HD webcam for streaming and video calls', 89.99, 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        
        # Seller 2 products (seller_id = 5)
        ('Smart Watch', 'Fitness tracking smartwatch with heart rate monitor', 249.99, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Bluetooth Speaker', 'Portable waterproof Bluetooth speaker', 149.99, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Phone Case', 'Premium leather phone case with card holder', 39.99, 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Power Bank', '20000mAh fast charging power bank', 59.99, 'https://images.unsplash.com/photo-1609592424717-d1b6f9143bd2', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('USB-C Cable', 'Fast charging USB-C to USB-C cable 6ft', 19.99, 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Tablet Stand', 'Adjustable aluminum tablet and phone stand', 29.99, 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Car Charger', 'Dual port fast car charger with LED display', 24.99, 'https://images.unsplash.com/photo-1586953208448-b95a79798f07', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Screen Protector', 'Tempered glass screen protector pack of 3', 14.99, 'https://images.unsplash.com/photo-1616410011236-7a42121dd981', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        
        # Original products (keeping for compatibility)
        ('Smartphone', 'Latest model smartphone', 599.99, 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd', 4, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Laptop', 'High performance laptop', 1299.99, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853', 5, 'active', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    for product in products:
        try:
            # c.execute("INSERT INTO products (name, description, price, image, seller_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", product)
            c.execute("INSERT OR IGNORE INTO products (name, description, price, image, seller_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", product)
        except sqlite3.IntegrityError:
            pass
    
    # Add some sample reviews
    sample_reviews = [
        # User reviews (user_id = 1)
        (1, 1, "Amazing gaming laptop! Runs all my games smoothly at high settings. Great build quality and the keyboard feels premium.", 5, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (7, 1, "The smartwatch is fantastic! Battery life is excellent and the fitness tracking is very accurate.", 5, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (2, 1, "Great headphones with excellent noise cancellation. Perfect for work from home.", 4, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        
        # Admin reviews (user_id = 2)
        (8, 2, "Good portable speaker with clear sound quality. The waterproof feature works as advertised.", 4, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (3, 2, "Beautiful 4K monitor with vibrant colors. Great for both work and entertainment.", 5, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        
        # Test user reviews (user_id = 3)
        (4, 3, "Love the RGB lighting and the tactile feel of the keys. Perfect for gaming and typing.", 4, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (10, 3, "Fast charging power bank that actually delivers on its promises. Compact and reliable.", 5, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    
    for review in sample_reviews:
        try:
            c.execute("INSERT INTO reviews (product_id, user_id, review, rating, created_at) VALUES (?, ?, ?, ?, ?)", review)
        except sqlite3.IntegrityError:
            pass
    
    # Add some items to cart for testing
    sample_cart = [
        (1, 2, 1),  # user has wireless headphones in cart
        (1, 7, 1),  # user has smartwatch in cart
        (3, 4, 2),  # test user has 2 mechanical keyboards in cart
    ]
    
    for cart_item in sample_cart:
        try:
            c.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", cart_item)
        except sqlite3.IntegrityError:
            pass
    
    # Add some sample orders
    sample_orders = [
        (1, 5, 1, 79.99, 'completed'),   # user bought gaming mouse
        (1, 11, 1, 29.99, 'completed'),  # user bought tablet stand
        (3, 9, 1, 39.99, 'pending'),    # test user ordered phone case
        (2, 1, 1, 1899.99, 'completed') # admin bought gaming laptop
    ]
    
    for order in sample_orders:
        try:
            c.execute("INSERT INTO orders (user_id, product_id, quantity, price, status) VALUES (?, ?, ?, ?, ?)", order)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()