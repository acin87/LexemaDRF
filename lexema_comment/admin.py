from django.contrib import admin

from lexema_comment.models import Comments, CommentImages

# Register your models here.
admin.site.register(Comments)
admin.site.register(CommentImages)