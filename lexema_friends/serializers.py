from rest_framework import serializers
from lexema_friends.models import Friends
from lexema_group.models import GroupMembership
from lexema_post.models import Post
from lexema_profile.serializers import ProfileForFriendFeedSerializer, ProfileUpcomingBirthdaySerializer


class FriendsSerializer(serializers.ModelSerializer):
    profile = ProfileForFriendFeedSerializer(source="friend.profile", read_only=True)
    friends_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()
    friends_avatars = serializers.SerializerMethodField()

    class Meta:
        model = Friends
        fields = [
            "profile",
            "friends_count",
            "posts_count",
            "groups_count",
            "friend",
            "friends_avatars",
        ]

    def get_friends_count(self, obj):
        return Friends.objects.filter(user=obj.friend, status="accepted").count()

    def get_posts_count(self, obj):
        return Post.objects.filter(author=obj.friend).count()

    def get_groups_count(self, obj):
        return GroupMembership.objects.filter(user=obj.friend).count()

    def get_friends_avatars(self, obj):
        # Получаем друзей друга с предзагрузкой профилей и изображений
        friend_friends = (
            Friends.objects.filter(user=obj.friend, status="accepted")
            .select_related("friend")
            .prefetch_related("friend__profile__images")[:5]
        )  # Ограничиваем количество друзей

        friends_data = []
        for friend in friend_friends:
            # Получаем данные друга из связанной модели User
            friend_user = friend.friend
            friend_data = {
                "id": friend_user.id,  # ID пользователя
                "first_name": friend_user.first_name,  # Имя пользователя
                "last_name": friend_user.last_name,  # Фамилия пользователя
                "avatar_image": None,  # По умолчанию аватар отсутствует
            }

            # Получаем аватар друга (первое изображение, если есть)
            profile_images = friend_user.profile.images.all()
            for image in profile_images:
                if image.avatar_image:
                    friend_data["avatar_image"] = image.avatar_image.url
                    break  # Используем только первый аватар

            friends_data.append(friend_data)

        return friends_data


class UpcomingBirthDayFriendsSerializer(serializers.ModelSerializer):
    profile = ProfileUpcomingBirthdaySerializer(source="friend.profile", read_only=True)

    class Meta:
        model = Friends
        fields = ["profile"]
