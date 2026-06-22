from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

class ProgressRepository:
    def __init__(self, conn: connection):
        self.__conn = conn

    # Cartas ------------------
    def set_card(self, user_id, card_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
               INSERT INTO "user_cards"
                   (user_id, card_id)
               VALUES (%s, %s)
           """, (
                user_id,
                card_id
            )
        )
        self.__conn.commit()
        cursor.close()

    def get_all_cards_id(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT card_id
            FROM "user_cards"
            WHERE user_id = %s
            """,
            (user_id,),
        )
        data = cursor.fetchall()
        cursor.close()
        return [row[0] for row in data]
    
    # SETS ---------------
    def get_all_sets(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT set_id
            FROM "user_sets"
            WHERE user_id = %s
            """,
            (user_id,),
        )
        data = cursor.fetchall()
        cursor.close()
        return [row[0] for row in data]
    
    def set_set(self, user_id, set_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
               INSERT INTO user_sets
                   (user_id, set_id)
               VALUES (%s, %s)
           """, (
                user_id,
                set_id
            )
        )
        self.__conn.commit()
        cursor.close()

    # Deck -------------------
    def get_deck(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT card_id FROM user_deck_cards
            WHERE user_id = %s
            """,
            (user_id,)
        )
        data = cursor.fetchall()
        cursor.close()

        return [row[0] for row in data]

    def add_card_to_deck(self, user_id, card_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_deck_cards (user_id, card_id)
            VALUES (%s, %s)
            """,
            (user_id, card_id)
        )
        self.__conn.commit()
        cursor.close()

    def clear_deck(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            "DELETE FROM user_deck_cards WHERE user_id = %s",
            (user_id,)
        )
        self.__conn.commit()
        cursor.close()

    # Icones ----------------------
    def get_user_icons(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT icon_id FROM user_icons
            WHERE user_id = %s
            """,
            (user_id,)
        )
        data = cursor.fetchall()
        cursor.close()

        return [row[0] for row in data]

    def set_icon(self, user_id, icone_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
               INSERT INTO user_icons
                   (user_id, icon_id)
               VALUES (%s, %s)
           """, (
                user_id,
                icone_id
            )
        )
        self.__conn.commit()
        cursor.close()
    
    # Pacotaço -----------
    def get_user_prom(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT promotion_id FROM user_promotion
            WHERE user_id = %s
            """,
            (user_id,)
        )
        data = cursor.fetchall()
        cursor.close()

        return [row[0] for row in data]

    def set_user_prom(self, user_id, promotion_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
               INSERT INTO user_promotion
                   (user_id, promotion_id)
               VALUES (%s, %s)
           """, (
                user_id,
                promotion_id
            )
        )
        self.__conn.commit()
        cursor.close()

    
    def get_vault_cards(self, user_id, vault_id):
        cursor = self.__conn.cursor()

        cursor.execute("""
            SELECT card_id, has_purchased
            FROM user_vault
            WHERE user_id = %s AND vault_id = %s
        """, (user_id, vault_id))

        data = cursor.fetchall()
        cursor.close()
        print(data)
        return data
    
    def set_vault_item(self, user_id, vault_id, card_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
               INSERT INTO user_vault
                   (user_id, vault_id, card_id, has_purchased)
               VALUES (%s, %s, %s, %s)
           """, (
                user_id,
                vault_id,
                card_id,
                False
            )
        )
        self.__conn.commit()
        cursor.close()

    def delete_user_vault(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            "DELETE FROM user_vault WHERE user_id = %s",
            (user_id,)
        )
        self.__conn.commit()
        cursor.close()

    def set_vault_card(self, user_id, card_id):
        cursor = self.__conn.cursor()
        cursor.execute(
        """
            UPDATE "user_vault"
            SET has_purchased = %s
            WHERE user_id = %s AND card_id = %s
        """, (
            True,
            user_id,
            card_id
        )
        )
        self.__conn.commit()
        cursor.close()