import mysql.connector.pooling
from config import Config

# Initialize connection pool globally
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name=Config.MYSQL_POOL_NAME,
    pool_size=Config.MYSQL_POOL_SIZE,
    pool_reset_session=True,
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DATABASE
)

def get_db_connection():
    """Returns a connection from the global MySQL connection pool."""
    return db_pool.get_connection()