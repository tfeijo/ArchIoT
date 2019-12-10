
class User:
    def __init__(self, name, login, password, group):
        self.__name = name
        self.__login = login
        self.__password = password
        self.__group = group

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, nome):
        self.__nome = nome

    @property
    def login(self):
        return self.__login

    @login.setter
    def login(self, login):
        login = login.islower()
        login = login.replace(" ", "")
        self.__login = login

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = password

    @property
    def group(self):
        return self.__group

    @group.setter
    def group(self, group):
        self.__group = group



class Group:
    def __init__(self, name, list_key, list_user):
        self.__name = name
        self.__list_key = list_key
        self.__list_user = list_user

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def list_key(self):
        return self.__list_key

    @list_key.setter
    def list_key(self, list_key):
        self.__list_key = list_key

    @property
    def list_user(self):
        return self.__list_user

    @list_user.setter
    def list_user(self, list_user):
        self.__list_user = list_user
