from database.db_connection import get_db_connection

class UserModel:

    def create_user(self, name, email, password):

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (name, email, password))
        conn.commit()

        cursor.close()
        conn.close()

    def get_user_by_email(self, email):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"

        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user

    def set_password_reset_token(self, email, token, expiry_dt):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE users
        SET reset_token = %s, reset_token_expiry = %s
        WHERE email = %s
        """
        cursor.execute(query, (token, expiry_dt, email))
        conn.commit()

        cursor.close()
        conn.close()

    def get_user_by_reset_token(self, token):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * FROM users
        WHERE reset_token = %s AND reset_token_expiry > NOW()
        """
        cursor.execute(query, (token,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()
        return user

    def update_password(self, user_id, hashed_password):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE users
        SET password = %s
        WHERE user_id = %s
        """
        cursor.execute(query, (hashed_password, user_id))
        conn.commit()

        cursor.close()
        conn.close()

    def clear_password_reset_token(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE users
        SET reset_token = NULL, reset_token_expiry = NULL
        WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        conn.commit()

        cursor.close()
        conn.close()