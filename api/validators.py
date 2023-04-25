import phonenumbers

def isPhoneNumber(number):
    """
    Используется для поля класса CharField
    модели Django. Проверяет значение телефонного 
    номера на возможность перевода в международный
    формат 

    Parameters
    ----------
    number : str
        Телефонный номер
        
    Returns
    -------
    number: str или False
        Возможность записи - телефонный номер в 
        международном формате, в противном случае - False
    """
    try:
        phone_number = phonenumbers.parse(number)
    except phonenumbers.NumberParseException:
        return False
    else:
        return ''.join(('+', phone_number.country_code, phone_number.national_number))