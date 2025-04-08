from django.contrib import admin

from lexema_comment.models import Comment, CommentImages

# Register your models here.
admin.site.register(Comment)
admin.site.register(CommentImages)
