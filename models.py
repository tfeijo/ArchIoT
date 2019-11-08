
class User:
    def __init__(self, nome, login, password, group):
        self.__name = nome
        self.__login = login
        self.__password = password
        self.__group = group



class Group:
    def __init__(self, nome, list_key, list_user):
        self.__name = nome
        self.__list_key = list_key
        self.__list_user = list_user