from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

class UserRepository:
    def __init__(self, conn: connection):
        self.__conn = conn

    def set_user(self, user):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
               INSERT INTO "user"
                (nome, email, senha, pontos, impetos, xp, nivel, ultimo_login, streak, profile_img, packs_diarios_abertos, contador_packs_comuns, packs_comprados_comum, packs_comprados_raro, has_already_get_daily_bonus, packs_evento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           """, (
                user["nome"],
                user["email"],
                user["senha"],
                150,
                0,
                0,
                1,
                user["ultimo_login"],
                1,
                'logo.png',
                2,
                0,
                0,
                1,
                False,
                user["packs_evento"]
            )
        )
        self.__conn.commit()
        cursor.close()

    def get_all_users(self):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM "user"
            """
        )
        data = cursor.fetchall()
        cursor.close()
        return data
    
    def get_user(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT "id", "nome", "pontos", "impetos", "xp", "nivel", "ultimo_login", "streak", "profile_img", "packs_diarios_abertos", "contador_packs_comuns", "packs_comprados_comum", "packs_comprados_raro", "has_already_get_daily_bonus", "packs_evento"
            FROM "user"
            WHERE id = %s
            """,
            (user_id,),
        )
        data = cursor.fetchone()
        cursor.close()
        columns = [col[0] for col in cursor.description]
        return data, columns
    
    def get_user_battle(self, user_id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT "nome", "profile_img"
            FROM "user"
            WHERE id = %s
            """,
            (user_id,),
        )
        data = cursor.fetchone()
        cursor.close()
        columns = [col[0] for col in cursor.description]
        return data, columns
    
    def check_email(self, email):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM "user" WHERE "email" = %s
            )
            """,
            (email,)
        )
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists
    
    def get_id_by_email(self, user_email):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT "id"
            FROM "user"
            WHERE email = %s
            """,
            (user_email,),
        )
        data = cursor.fetchone()
        cursor.close()
        return data

    def find_login(self, email):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            SELECT "id", "nome", "email", "senha", "pontos", "impetos", "xp", "nivel", "ultimo_login", "streak", "profile_img", "packs_diarios_abertos", "contador_packs_comuns", "packs_comprados_comum", "packs_comprados_raro", "has_already_get_daily_bonus", "packs_evento"
            FROM "user"
            WHERE email = %s
            """,
            (email,),
        )
        data = cursor.fetchone()
        cursor.close()
        columns = [col[0] for col in cursor.description]
        return data, columns
    
    def edit_user(self, id, user):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET nome = %s,
            pontos = %s,
            impetos = %s,
            xp = %s,
            nivel = %s,
            ultimo_login = %s,
            streak = %s,
            profile_img = %s,
            packs_diarios_abertos = %s,
            contador_packs_comuns = %s,
            packs_comprados_comum = %s,
            packs_comprados_raro = %s,
            has_already_get_daily_bonus = %s,
            packs_evento = %s
            WHERE id = %s
            """, (
                user["nome"],
                user["pontos"],
                user["impetos"],
                user["xp"],
                user["nivel"],
                user["ultimo_login"],
                user["streak"],
                user["profile_img"],
                user["packs_diarios_abertos"],
                user["contador_packs_comuns"],
                user["packs_comprados_comum"],
                user["packs_comprados_raro"],
                user["has_already_get_daily_bonus"],
                user["packs_evento"],
                id
            )
        )
        self.__conn.commit()
        cursor.close()

    def daily_update(self, user):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET
            pontos = %s,
            ultimo_login = %s,
            streak = %s,
            packs_diarios_abertos = %s,
            packs_comprados_comum = %s,
            packs_comprados_raro = %s,
            has_already_get_daily_bonus = %s,
            packs_evento = %s
            WHERE id = %s
            """, (

                user["pontos"] ,
                user["ultimo_login"],
                user["streak"],
                user["packs_diarios_abertos"],
                user["packs_comprados_comum"],
                user["packs_comprados_raro"],
                user["has_already_get_daily_bonus"],
                user["packs_evento"],
                user['id']
            )
        )
        self.__conn.commit()
        cursor.close()


    def set_nome(self, id, nome):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET nome = %s
            WHERE id = %s
            """,
            (nome, id)
        )
        self.__conn.commit()
        cursor.close()

    def set_img(self, id, value):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET profile_img = %s
            WHERE id = %s
            """,
            (value, id)
        )
        self.__conn.commit()
        cursor.close()
    
    def set_points(self, id, valor):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET pontos = %s
            WHERE id = %s
            """,
            (valor, id)
        )
        self.__conn.commit()
        cursor.close()
    
    def set_contador_packs(self, id, valor):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET contador_packs_comuns = %s
            WHERE id = %s
            """,
            (valor, id)
        )
        self.__conn.commit()
        cursor.close()

    def set_bonus_diario(self, id, valor):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            UPDATE "user"
            SET has_already_get_daily_bonus = %s
            WHERE id = %s
            """,
            (valor, id)
        )
        self.__conn.commit()
        cursor.close()

    def delete_user(self, id):
        cursor = self.__conn.cursor()
        cursor.execute(
            """
            DELETE FROM "user" WHERE id = %s
            """, (id)
        )
        self.__conn.commit()
        cursor.close()