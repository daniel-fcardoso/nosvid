from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    @property
    def has_channel(self):
        return hasattr(self, "channel")


class Channel(models.Model):

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="channel"
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    avatar = models.ImageField(
        upload_to="channel_avatars/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Video(models.Model):

    class Category(models.TextChoices):
        MUSIC = "music", "Música"
        GAMING = "gaming", "Jogos"
        TECHNOLOGY = "technology", "Tecnologia"
        EDUCATION = "education", "Educação"
        ENTERTAINMENT = "entertainment", "Entretenimento"
        SPORTS = "sports", "Esportes"
        NEWS = "news", "Notícias"
        FILM_ANIMATION = "film_animation", "Filmes e animação"
        PEOPLE_BLOGS = "people_blogs", "Pessoas e blogs"
        OTHER = "other", "Outros"

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER
    )

    video_file = models.FileField(
        upload_to="videos/"
    )

    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    views = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.title


class VideoView(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="video_views",
        blank=True,
        null=True
    )

    session_key = models.CharField(
        max_length=40,
        blank=True,
        default=""
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="view_records"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    last_viewed = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=["user", "video"],
                condition=models.Q(
                    user__isnull=False
                ),
                name="unique_user_video_view"
            ),

            models.UniqueConstraint(
                fields=["session_key", "video"],
                condition=~models.Q(
                    session_key=""
                ),
                name="unique_session_video_view"
            ),
        ]

    def __str__(self):

        if self.user:
            viewer = self.user.username

        else:
            viewer = self.session_key

        return f"{viewer} -> {self.video.title}"


class Like(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="unique_video_like"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.video.title}"


class Dislike(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dislikes"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="dislikes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="unique_video_dislike"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.video.title}"


class Comment(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    text = models.TextField(
        max_length=1000
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username}: {self.text[:40]}"


class CommentLike(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_likes"
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_comment_like"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> comentário {self.comment.id}"


class CommentDislike(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_dislikes"
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="dislikes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_comment_dislike"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> comentário {self.comment.id}"


class Subscription(models.Model):

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="subscribers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "channel"],
                name="unique_channel_subscription"
            )
        ]

    def __str__(self):
        return f"{self.subscriber.username} -> {self.channel.name}"


class WatchHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watch_history"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="watch_history"
    )

    watched_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="unique_watch_history"
            )
        ]

        ordering = [
            "-watched_at"
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.video.title}"


class Playlist(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="playlists"
    )

    name = models.CharField(
        max_length=120
    )

    description = models.TextField(
        blank=True
    )

    is_private = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-updated_at"
        ]

    def __str__(self):
        return f"{self.name} - {self.owner.username}"


class PlaylistItem(models.Model):

    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name="items"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="playlist_items"
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    position = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "video"],
                name="unique_playlist_video"
            )
        ]

        ordering = [
            "position",
            "added_at"
        ]

    def __str__(self):
        return f"{self.playlist.name} -> {self.video.title}"



class WatchLater(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watch_later"
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="watch_later_users"
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="unique_watch_later"
            )
        ]

        ordering = [
            "-added_at"
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.video.title}"


class CommentReply(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_replies"
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    text = models.TextField(
        max_length=1000
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "created_at"
        ]

    def __str__(self):
        return f"{self.user.username}: {self.text[:40]}"


class Notification(models.Model):

    KIND_CHOICES = [
        ("subscription", "Inscrição"),
        ("comment", "Comentário"),
        ("reply", "Resposta"),
        ("like", "Curtida"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES
    )

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.actor.username} -> "
            f"{self.recipient.username}: {self.kind}"
        )

