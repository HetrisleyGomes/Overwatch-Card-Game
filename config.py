import os
from dotenv import load_dotenv

load_dotenv()

class DbConnectionHandler:
    def __init__(self) -> None:
        self.__connection_string = os.getenv("DATABASE_URL")
        self.__conn = None

        if self.__connection_string:
            print("DATABASE_URL carregado.")
        else:
            print("DATABASE_URL NÃO foi carregado.")

    def get_connection_string(self) -> str:
        return self.__connection_string

db_connection_handler = DbConnectionHandler()
