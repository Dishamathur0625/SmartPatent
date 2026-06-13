from database.db_connection import get_db_connection


class DraftModel:
    def create_draft(
        self,
        user_id,
        title,
        field_of_technology,
        draft_content,
        prior_art_analysis,
        diagram_path,
        diagram_caption,
        drawing_description
    ):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO drafts
        (user_id, title, field, draft_text, prior_art_analysis,
         diagram_path, diagram_caption, drawing_description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            user_id,
            title,
            field_of_technology,
            draft_content,
            prior_art_analysis,
            diagram_path,
            diagram_caption,
            drawing_description
        ))

        conn.commit()
        draft_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return draft_id
    
    def get_draft_by_id(self, draft_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM drafts WHERE id = %s"
        cursor.execute(query, (draft_id,))
        draft = cursor.fetchone()

        cursor.close()
        conn.close()
        return draft
    
    def update_draft_text(self, draft_id, new_text, is_edited=True):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE drafts
        SET draft_text = %s, is_edited = %s
        WHERE id = %s
        """

        cursor.execute(query, (new_text, is_edited, draft_id))
        conn.commit()

        cursor.close()
        conn.close()

    def get_next_version_no(self, draft_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT MAX(version_no) AS max_version FROM draft_versions WHERE draft_id = %s"
        cursor.execute(query, (draft_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        max_version = result["max_version"] if result and result["max_version"] else 0
        return max_version + 1
    
    def save_draft_version(self, draft_id, version_no, draft_text):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO draft_versions (draft_id, version_no, draft_text)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (draft_id, version_no, draft_text))
        conn.commit()

        cursor.close()
        conn.close()

    def update_draft_version_no(self, draft_id, version_no):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "UPDATE drafts SET version_no = %s WHERE id = %s"
        cursor.execute(query, (version_no, draft_id))
        conn.commit()

        cursor.close()
        conn.close()