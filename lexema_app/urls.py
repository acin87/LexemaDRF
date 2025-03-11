from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from lexema_app.views.auth.CustomTokenObtainPairView import CustomTokenObtainPairView
from lexema_app.views.auth.registerView import RegisterView
from lexema_app.views.post.PostsViewSet import PostsViewSet


router = routers.DefaultRouter()
router.register(r"api/posts", PostsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path(
        "api/auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
