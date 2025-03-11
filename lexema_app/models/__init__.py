"""Модуль для моделей"""

from .profiles.Profile import Profiles as _Profiles

from .friends.Friends import Friends as _Friends
from .groups.Groups import LexemaGroups as _Groups
from .posts.Posts import Posts as _Posts
from .posts.Comment import Comment as _Comment
from .posts.PostImage import PostImage as _PostImage


__all__ = ["_Profiles", "_Friends", "_Groups", "_Posts", "_Comment", "_PostImage"]
