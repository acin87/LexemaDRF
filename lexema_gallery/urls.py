from django.urls import path

from lexema_gallery import views

urlpatterns = [path("gallery/", views.GalleryView.as_view(), name="gallery")]
