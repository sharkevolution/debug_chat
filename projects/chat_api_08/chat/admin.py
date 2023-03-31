# chat/admin.py

from django.contrib import admin
from .models import Room, Message, CustomUser, User, ParticipanteRoom

# admin.site.register(Room)
# admin.site.register(CustomUser)


@admin.register(ParticipanteRoom)
class ParticipanteRoomAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'user_status', 'timestamp')


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_room')
    # readonly_fields = ('created', )
    # fields = ('name', 'participante', 'updated', 'created')


admin.site.register(Room, RoomAdmin)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Токены пользователя', {
            'classes': ['wide'],
            'fields': ('user', 'token_access', 'token_refresh')
        }),    
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipient', 'status_text', 'room_name', 'content', 'is_read', 'created')