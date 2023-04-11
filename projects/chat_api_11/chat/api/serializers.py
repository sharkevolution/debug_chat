from rest_framework import serializers
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from chat.models import Room, Message, TokenUser

from collections import OrderedDict


import logging
logger = logging.getLogger(__name__)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Save user token to base
        access_token_obj = token.access_token
        user_id = access_token_obj['user_id']
        cur_user = User.objects.get(id=int(user_id))

        # Добавить get or create 10/04/2023 если пользователь был но не создавался token
        acc = TokenUser.objects.get(user=cur_user)
        acc.token_access = str(token.access_token)
        acc.token_refresh = str(token)
        acc.save()

        # logging.warning('refresh: ' + str(token))
        # logging.warning('access: ' + str(str(token.access_token)))

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'token']

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        # ----- Добавляем токены в связанную таблицу ----
        access_token_obj = refresh.access_token
        user_id = access_token_obj['user_id']

        cur_user = User.objects.get(id=int(user_id))
        acc = TokenUser.objects.create(user=cur_user)
        acc.token_access = str(refresh.access_token)
        acc.token_refresh = str(refresh)
        acc.save()
        # ----- Добавляем токены в связанную таблицу ----

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance


class UserListSerializer(serializers.ModelSerializer):
    
    rooms = serializers.SerializerMethodField(method_name='related_rooms')
            
    class Meta:
        model = User
        ordering = ['id', 'rooms']
        fields = ['id', 'username', 'rooms']

    def related_rooms(self, obj):
        related_rooms = obj.participante_in_room.filter()
        user_rooms = {}
        for b in related_rooms:
            user_rooms[b.id] = b.name

        # Добавить сообщение последнее datetime и статус is_read
        return OrderedDict(sorted(user_rooms.items(), key=lambda item: item[0]))
    

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']


class UserListingField(serializers.RelatedField):
    """
        Добавляем полей из User
    """
    def to_representation(self, value):
        return {'id': value.id, 'name': value.username, 'is_staff': value.is_staff}
    

class RoomDetailSerializer(serializers.ModelSerializer):
    # Добавляем помимо username, выборочно поля из User
    participante = UserListingField(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'participante',
                  'created', 'updated', 'limit_users']


class MesageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'repicient', 'status_text',
                  'room_name', 'content', 'created_iso']


class SendMessagesSerializer(serializers.ModelSerializer):
    '''
        Реализовать сохранение в базу и отправку уведомления о новом сообщении
        Проверить и сделать валидацию 26.03.2023

    '''
    class Meta:
        model = Room
        fields = ['name']

    def sendmessage(self, validated_data):
        id_room = validated_data.pop('name', None)
        instance = self.Meta.model(**validated_data)
        logging.warning('ok api')
        if id_room:
            # instance.(id_room)
            # instance.save()
            return instance
