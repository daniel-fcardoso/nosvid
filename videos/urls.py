from django.urls import path

from . import views


app_name = "videos"


urlpatterns = [
    path(
        "",
        views.index,
        name="index"
    ),

    path(
        "search/",
        views.search,
        name="search"
    ),

    path(
        "history/",
        views.history,
        name="history"
    ),

    path(
        "history/clear/",
        views.clear_history,
        name="clear_history"
    ),

    path(
        "history/<int:video_id>/remove/",
        views.remove_history_item,
        name="remove_history_item"
    ),

    path(
        "liked/",
        views.liked_videos,
        name="liked_videos"
    ),

    path(
        "notifications/",
        views.notifications,
        name="notifications"
    ),

    path(
        "notifications/read/",
        views.mark_notifications_read,
        name="mark_notifications_read"
    ),

    path(
        "watch-later/",
        views.watch_later,
        name="watch_later"
    ),

    path(
        "watch-later/<int:video_id>/remove/",
        views.remove_watch_later,
        name="remove_watch_later"
    ),

    path(
        "csrf-token/",
        views.csrf_token_refresh,
        name="csrf_token_refresh"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "channel/create/",
        views.create_channel,
        name="create_channel"
    ),

    path(
        "channel/edit/",
        views.edit_channel,
        name="edit_channel"
    ),

    path(
        "channel/<str:username>/",
        views.channel_view,
        name="channel"
    ),

    path(
        "channel/<str:username>/subscribe/",
        views.toggle_subscription,
        name="toggle_subscription"
    ),

    path(
        "subscriptions/",
        views.subscriptions_feed,
        name="subscriptions"
    ),

    path(
        "studio/",
        views.studio,
        name="studio"
    ),

    path(
        "playlists/",
        views.playlists,
        name="playlists"
    ),

    path(
        "playlists/create/",
        views.create_playlist,
        name="create_playlist"
    ),

    path(
        "playlist/<int:playlist_id>/",
        views.playlist_detail,
        name="playlist_detail"
    ),

    path(
        "playlist/<int:playlist_id>/edit/",
        views.edit_playlist,
        name="edit_playlist"
    ),

    path(
        "playlist/<int:playlist_id>/delete/",
        views.delete_playlist,
        name="delete_playlist"
    ),

    path(
        "playlist/<int:playlist_id>/video/<int:video_id>/remove/",
        views.remove_video_from_playlist,
        name="remove_video_from_playlist"
    ),

    path(
        "playlist/<int:playlist_id>/item/<int:item_id>/move/",
        views.move_playlist_item,
        name="move_playlist_item"
    ),

    path(
        "upload/",
        views.upload_video,
        name="upload"
    ),

    path(
        "watch/<int:video_id>/",
        views.watch_video,
        name="watch"
    ),

    path(
        "video/<int:video_id>/edit/",
        views.edit_video,
        name="edit_video"
    ),

    path(
        "video/<int:video_id>/delete/",
        views.delete_video,
        name="delete_video"
    ),

    path(
        "video/<int:video_id>/like/",
        views.toggle_like,
        name="toggle_like"
    ),

    path(
        "video/<int:video_id>/dislike/",
        views.toggle_dislike,
        name="toggle_dislike"
    ),

    path(
        "video/<int:video_id>/playlist/add/",
        views.add_video_to_playlist,
        name="add_video_to_playlist"
    ),

    path(
        "video/<int:video_id>/watch-later/",
        views.toggle_watch_later,
        name="toggle_watch_later"
    ),

    path(
        "video/<int:video_id>/comment/",
        views.add_comment,
        name="add_comment"
    ),

    path(
        "comment/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment"
    ),

    path(
        "comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment"
    ),

    path(
        "comment/<int:comment_id>/like/",
        views.toggle_comment_like,
        name="toggle_comment_like"
    ),

    path(
        "comment/<int:comment_id>/dislike/",
        views.toggle_comment_dislike,
        name="toggle_comment_dislike"
    ),

    path(
        "comment/<int:comment_id>/reply/",
        views.add_comment_reply,
        name="add_comment_reply"
    ),

    path(
        "reply/<int:reply_id>/edit/",
        views.edit_comment_reply,
        name="edit_comment_reply"
    ),

    path(
        "reply/<int:reply_id>/delete/",
        views.delete_comment_reply,
        name="delete_comment_reply"
    ),
]
