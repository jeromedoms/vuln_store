import bcrypt

class Config:
    SECRET_KEY = 'supersecretkey'  # Insecure secret key
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    SALT = bcrypt.gensalt(rounds=4)