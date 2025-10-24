import os

DATABASE_URL = os.getenv("DATABASE_URL","mysql+pymysql://root:Password%402@localhost:3306/clientsphere")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
