from django.core.files.storage import FileSystemStorage

class UserAvatarStorage(FileSystemStorage):
    """
    Класс менеджера для работы с файловой системой
    сервера. Отличается реализацией метода `save`
    в том, что при совпадении пути загружаемого файла
    с существующим не производится запись.

    !!
    Используется для поля `avatar` модели `api.User`
    !!
    """

    def save(self, name, content, max_length=None):
        """
        Сохраняет файл, возвращает путь в строковом представлении

        Parameters
        ----------
        name : str
            Абсолютный путь к загружаемому файлу
        content : django.core.files.Files
            Контент файла
        max_length : int
            Максимальная длина пути для загружаемого файла 

        Returns
        -------
        path : str
            Путь в прямом слэше
        """
        if self.exists(name):
            return name
        return super(UserAvatarStorage, self).save(name, content, max_length=max_length)