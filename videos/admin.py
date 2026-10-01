from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Channel,
    Comment,
    CommentReply,
    CommentDislike,
    CommentLike,
    Dislike,
    Like,
    Notification,
    Playlist,
    PlaylistItem,
    Subscription,
    User,
    Video,
    VideoView,
    WatchHistory,
    WatchLater,
)


admin.site.register(User, UserAdmin)

admin.site.register(Channel)

admin.site.register(Video)
admin.site.register(VideoView)

admin.site.register(Like)
admin.site.register(Dislike)

admin.site.register(Comment)
admin.site.register(CommentReply)
admin.site.register(CommentLike)
admin.site.register(CommentDislike)

admin.site.register(Subscription)
admin.site.register(WatchHistory)

admin.site.register(Playlist)
admin.site.register(PlaylistItem)
admin.site.register(WatchLater)
admin.site.register(Notification)
