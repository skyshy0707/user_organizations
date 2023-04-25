from rest_framework import generics, status
from rest_framework import permissions as rest_perm
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models, serializers
# Create your views here.


class Registration(APIView):

    permission_classes = [rest_perm.AllowAny]

    def post(self, request):
        """
        Parameters
        ----------
        request : rest_framework.request.Request
            Запрос клиента, с json данными для регистрации

            json

                {
                    'email': <email>,
                    'password': <password>,
                    'password2': <password>
                }
                
        Returns
        -------
        json: rest_framework.response.Response
            Данные об успешности регистрации
        """

        email = request.data.get('email')
        password = request.data.get('password')
        password2 = request.data.get('password2')

        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            user = None

        if user:
            return Response({
                'error': 'Such user is exist'
            }, status=status.HTTP_400_BAD_REQUEST)
        if password != password2:
            return Response({
                'error': 'Password\'s inputs don\'t match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = models.User.objects.create(email=email)
        user.set_password(password)
        user.save()

        return Response({'message': 'Registration success'}, status=status.HTTP_201_CREATED)
    
class UserEdit(generics.UpdateAPIView):

    permission_classes = [rest_perm.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        """
        Возвращает экземпляр пользователя `api.models.User`
        по параметру строки запроса

        Returns
        -------
        user: api.models.User
            Экземпляр пользователя для модификации данных
        """
        pk = self.request.query_params.get('pk')
        return models.User.objects.get(pk=pk)
    
    def put(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request : rest_framework.request.Request
            Запрос клиента, с json данными для модификации
            пользователя `api.User` и параметрами строки запроса
            
            headers: 
                {
                    'Authorization': 'Bearer <JWT>',
                    'Content-Type': 'application/json'
                }

            json: 
                {
                    'id': <id пользователя>, 
                    'email': '<email-пользователя@mail.ru>', 
                    'phone': '<Телефонный номер пользователя в международном формате>', 
                    'first_name': '<Имя пользователя>', 
                    'last_name': '<Фамилия пользователя>', 
                    'avatar': '<http://абсолютная/ссылка/на/файл/аватара.ext>', 
                    'organization_set': <Список id организаций [ 1, ..., n]>
                    !NB: Список, переданный в 'organization_set' заменит прежний
                }

            params:
                {
                    'pk': <id пользователя>
                }
            
        Returns
        -------
        json: rest_framework.response.Response
            Сериализованные данные пользователя после модификации

            {
                'id': <id пользователя>, 
                'email': '<email-пользователя@mail.ru>', 
                'phone': '<Телефонный номер пользователя в международном формате>', 
                'first_name': '<Имя пользователя>', 
                'last_name': '<Фамилия пользователя>', 
                'avatar': '<http://абсолютная/ссылка/на/файл/аватара.ext>', 
                'organization_set': <Список организаций [ 'Организация 1', ..., 'Организация n']
            } 
        """
        user = self.get_object()
        serializer = self.get_serializer(user, context={'request': request}, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK,)
        return Response(
            {'error': 'Bad data', 'errors': serializer.errors }, 
            status=status.HTTP_400_BAD_REQUEST
         )
    
class UserView(generics.GenericAPIView):

    permission_classes = [rest_perm.IsAuthenticated]
    serializer_class = serializers.UserSerializerOnlyRead

    def get_object(self):
        """
        Возвращает экземпляр пользователя `api.models.User`
        по параметру строки запроса

        Returns
        -------
        user: api.models.User
            Экземпляр пользователя для модификации данных
        """
        pk = self.request.query_params.get('pk')
        return models.User.objects.get(pk=pk)

    def get(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request : rest_framework.request.Request
            Запрос клиента с параметрами строки запроса

            headers: 
                {
                    'Authorization': 'Bearer <JWT>',
                    'Content-Type': 'application/json'
                }

            params:
                {
                    'pk': <id пользователя>
                }
        Returns
        -------
        json: rest_framework.response.Response
            Сериализованные данные пользователя

            {
                'id': <id пользователя>, 
                'email': '<email-пользователя@mail.ru>', 
                'phone': '<Телефонный номер пользователя в международном формате>', 
                'first_name': '<Имя пользователя>', 
                'last_name': '<Фамилия пользователя>', 
                'avatar': '<http://абсолютная/ссылка/на/файл/аватара.ext>',
                'organization_set': [
                                        {
                                            'id': <id организации>, 
                                            'users': <Список пользователей организации: 
                                                [ "user-email-1@mail.ru", ..., "user-email-n@mail.ru" ]> , 
                                            'name': '<Название организации>', 
                                            'description': 'Описание организации'
                                        }, 
                                         ...
                                    ]
            }
        """
        try: 
            user = self.get_object()
        except models.User.DoesNotExist:
            return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

class Users(generics.ListAPIView):

    permission_classes = [rest_perm.IsAuthenticated]
    serializer_class = serializers.UserSerializerOnlyRead
    queryset = models.User.objects.all()

    def get(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request : rest_framework.request.Request
            Запрос клиента

            headers: 
                {
                    'Authorization': 'Bearer <JWT>'
                }
            
        Returns
        -------
        json: rest_framework.response.Response
            Список сериализованные данных пользователей с разбивкой 
            для постраничного отображения
            {
                'users': [
                            {
                                'id': <id пользователя-1>, 
                                'email': '<email-пользователя-1>', 
                                'phone': '<Телефонный номер пользователя в международном формате>', 
                                'first_name': '<Имя пользователя>', 
                                'last_name': '<Фамилия пользователя>', 
                                'avatar': '<http://абсолютная/ссылка/на/файл/аватара.ext>',
                                'organization_set': [
                                                        {
                                                            'id': <id организации>, 
                                                            'users': <Список email-ов пользователей организации: 
                                                                [ "email-пользователя-1", ..., "email-пользователя-n@" ]> , 
                                                            'name': '<Название организации>', 
                                                            'description': 'Описание организации'
                                                        }, 
                                                        ...
                            },
                            ...
            ]
        """
        paginate_users = self.paginator.paginate_queryset(self.queryset, request)
        srd_users = self.serializer_class(paginate_users, context={'request': request}, many=True)
        context = { 'users': srd_users.data }
        context.update(self.paginator.get_html_context())
        return Response(context, status=status.HTTP_200_OK,)
    
class OrganizationCreate(generics.CreateAPIView):

    permission_classes = [rest_perm.IsAuthenticated]
    serializer_class = serializers.OrganizationSerializer

    def post(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request : rest_framework.request.Request
            Запрос клиента, с json данными для создания
            организации `api.Organization`

            headers: 
                {
                    'Authorization': 'Bearer <JWT>',
                    'Content-Type': 'application/json'
                }

            json:
                {
                    'name': '<Название организации>' (обязательный),
                    'description': '<Описание организации>',
                    'users': <Список id пользователей [ 1, ..., n ]>
                }
            
        Returns
        -------
        json: rest_framework.response.Response
            Сериализованные данные организации после её создания

            {   
                'id': <id организации>, 
                'users': <Список email-ов пользователей организации: 
                            [ "user-email-1@mail.ru", ..., "user-email-n@mail.ru" ]> , 
                'name': '<Название организации>', 
                'description': 'Описание организации'
            }
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': 'Invalid data', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
    
class Organizations(generics.ListAPIView):

    permission_classes = [rest_perm.IsAuthenticated]
    serializer_class = serializers.OrganizationOnlyRead
    queryset = models.Organization.objects.all()

    def get(self, request, *args, **kwargs):
        """
        Parameters
        ----------
        request : rest_framework.request.Request
            Запрос клиента

            headers: 
                {
                    'Authorization': 'Bearer <JWT>',
                    'Content-Type': 'application/json'
                }
            
        Returns
        -------
        json: rest_framework.response.Response
            Список сериализованных данных организаций с разбивкой 
            для постраничного отображения

            { 
                'organizations':   [ 
                    {
                        'id': <id организации 1>, 
                        'users': <Список пользователей [ 
                                    {
                                        'id': <id пользователя 1>, 
                                        'email': 'email пользователя-1@yandex.ru', 
                                        'phone': '<Телефонный номер пользователя-1>', 
                                        'first_name': 'Имя пользователя-1', 
                                        'last_name': 'Фамилия пользователя-1', 
                                        'avatar': '<Путь к аватару пользователя-1>', 
                                        'organization_set': <Список названий организаций пользователя-1 
                                            ['Организация-1', ..., 'Организация-n']
                                    },
                                    ...
                                ]>, 
                        'name': 'Титан', 
                        'description': None
                    },
                    ... 
                ]
            }
        """
        paginate_organizations = self.paginator.paginate_queryset(self.queryset, request)
        srd_organizations = self.serializer_class(paginate_organizations, many=True)
        context = { "organizations": srd_organizations.data }
        context.update(self.paginator.get_html_context())
        return Response(context, status=status.HTTP_200_OK,)