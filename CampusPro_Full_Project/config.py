
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']

    DB_SSL_CA = os.getenv(
        'DB_SSL_CA',
        '/etc/ssl/certs/ca-certificates.crt'
    )

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername='mysql+pymysql',
        username=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        port=int(os.getenv('DB_PORT', '4000')),
        database=os.environ['DB_NAME'],
        query={
            'ssl_ca': DB_SSL_CA,
            'ssl_verify_cert': 'true',
            'ssl_verify_identity': 'true'
        }
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
