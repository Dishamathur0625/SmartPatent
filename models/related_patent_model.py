from database.db_connection import get_db_connection


class RelatedPatentModel:
    def save_related_patents(self, draft_id, related_patents):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO related_patents
        (draft_id, patent_title, patent_number, patent_url, abstract_text, similarity_percent)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        for item in related_patents:
            cursor.execute(query, (
                draft_id,
                item.get("patent_title", ""),
                item.get("patent_number", ""),
                item.get("patent_url", ""),
                item.get("abstract_text", ""),
                item.get("similarity_percent", 0)
            ))

        conn.commit()
        cursor.close()
        conn.close()