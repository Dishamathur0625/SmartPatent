import mysql.connector.pooling
from config import Config

# Initialize connection pool globally as None, to be populated lazily
db_pool = None

def get_db_connection():
    """Returns a connection from the global MySQL connection pool, initializing it lazily."""
    global db_pool
    if db_pool is None:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=Config.MYSQL_POOL_NAME,
            pool_size=Config.MYSQL_POOL_SIZE,
            pool_reset_session=True,
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE
        )
    return db_pool.get_connection()