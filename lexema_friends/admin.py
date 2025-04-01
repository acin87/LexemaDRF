from django.contrib import admin

from lexema_friends.models import Friends

# Register your models here.



@admin.register(Friends)
class FriendsAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'status')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение в админке"""
        if change:
            old_obj = Friends.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                # Вызываем сигнал вручную при изменении статуса
                obj.save()  # Вызовет post_save сигнал
                return
        super().save_model(request, obj, form, change)