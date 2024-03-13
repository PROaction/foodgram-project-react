from django.contrib import admin
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'display_subscribers',
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')

    def display_subscribers(self, obj):
        return obj.subscribers.count()

    display_subscribers.short_description = 'Подписчики'
