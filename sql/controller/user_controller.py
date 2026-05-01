from datetime import datetime

class UserController:
    def __init__(self, repository):
        self.__repository = repository

    def create_user(self, user):
        try:
            user['ultimo_login'] = datetime.now().strftime("%Y-%m-%d")
            self.__repository.set_user(user)
            return user['id']
        except Exception as e:
            return str(e)
        
    def get_user(self, id):
        try:
            cursor, columns = self.__repository.get_user(id)
            data = self.dict_convert(cursor, columns)
            return data
        except Exception as e:
            return str(e)
        
    def get_users(self):
        try:
            cursor = self.__repository.get_all_users()
            data = self.dict_convert_list(cursor)
            return data
        except Exception as e:
            return str(e)

    def edit_user(self, id, user):
        try:
            self.__repository.edit_user(id, user)
            return True
        except Exception as e:
            return str(e)
        
    def change_points(self, id, points):
        try:
            self.__repository.set_points(id, points)
            return True
        except Exception as e:
            return str(e)
        
    def set_nome(self, id, nome):
        try:
            self.__repository.set_nome(id, nome)
            return True
        except Exception as e:
            return str(e)
    
    def set_foto(self, id, img):
        try:
            self.__repository.set_img(id, img)
            return True
        except Exception as e:
            return str(e)
        
    def daily_update(self, user):
        try:
            self.__repository.daily_update(user)
            return True
        except Exception as e:
            return str(e)
    
    def delete_user(self, id):
        try:
            self.__repository.delete_ficha(id)
            return True
        except Exception as e:
            return str(e)
        
    def find_user(self, email):
        try:
            cursor, columns = self.__repository.find_login(email)
            data = self.dict_convert(cursor, columns)
            return data
        except Exception as e:
            return str(e)

    
    def dict_convert(self, value, columns):
        data = dict(zip(columns, value))
        return data

    def dict_convert_list(self, value):
        formated = []
        for i in value:
            user = {
                "id": i[0],
                "nome": i[1],
                "pontos": i[2],
                "impetos": i[3],
                "xp": i[4],
                "nivel": i[5],
                "ultimo_login": i[6],
                "streak": i[7],
                "profile_img": i[8],
                "packs_diarios_abertos": i[9],
                "contador_packs_comuns": i[10],
                "packs_comprados_comum": i[11],
                "packs_comprados_raro": i[12],
                "has_already_get_daily_bonus": i[13],
                "packs_evento": i[14],
            }
            formated.append(user)
        return formated