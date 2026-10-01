from datetime import timedelta
from pathlib import Path


from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Max, Q, Sum
from django.http import Http404, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from PIL import Image, UnidentifiedImageError

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


VIEW_COOLDOWN_HOURS = 6
VIDEOS_PER_PAGE = 15

MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_THUMBNAIL_SIZE = 5 * 1024 * 1024

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".ogg",
}

ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/webm",
    "video/ogg",
    "application/ogg",
}

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def validate_video_upload(video_file):

    if not video_file:
        return "Você precisa selecionar um arquivo de vídeo."

    if video_file.size > MAX_VIDEO_SIZE:
        return "O vídeo deve ter no máximo 100 MB."

    extension = Path(
        video_file.name
    ).suffix.lower()

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        return (
            "Formato de vídeo não permitido. "
            "Use MP4, WebM ou OGG."
        )

    content_type = getattr(
        video_file,
        "content_type",
        ""
    ).lower()

    if (
        content_type
        and content_type
        not in ALLOWED_VIDEO_CONTENT_TYPES
    ):
        return (
            "O arquivo selecionado não parece ser "
            "um vídeo compatível."
        )

    return None


def validate_thumbnail_upload(thumbnail):

    if not thumbnail:
        return None

    if thumbnail.size > MAX_THUMBNAIL_SIZE:
        return "A thumbnail deve ter no máximo 5 MB."

    extension = Path(
        thumbnail.name
    ).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return (
            "Formato de thumbnail não permitido. "
            "Use JPG, JPEG, PNG ou WEBP."
        )

    content_type = getattr(
        thumbnail,
        "content_type",
        ""
    ).lower()

    if (
        content_type
        and content_type
        not in ALLOWED_IMAGE_CONTENT_TYPES
    ):
        return (
            "O arquivo selecionado não parece ser "
            "uma imagem compatível."
        )

    try:

        image = Image.open(
            thumbnail
        )

        image.verify()

    except (
        UnidentifiedImageError,
        OSError
    ):

        return (
            "A thumbnail enviada não é uma "
            "imagem válida."
        )

    finally:

        try:
            thumbnail.seek(0)
        except Exception:
            pass

    return None


def get_video_categories():
    return Video.Category.choices


def normalize_playlist_positions(playlist):
    items = list(
        playlist.items.order_by(
            "position",
            "added_at",
            "id"
        )
    )

    changed = []

    for index, item in enumerate(items, start=1):
        if item.position != index:
            item.position = index
            changed.append(item)

    if changed:
        PlaylistItem.objects.bulk_update(changed, ["position"])

    return items


def register_video_view(request, video):

    now = timezone.now()

    cooldown_limit = now - timedelta(
        hours=VIEW_COOLDOWN_HOURS
    )

    should_count = False

    if request.user.is_authenticated:

        view_record, created = VideoView.objects.get_or_create(
            user=request.user,
            video=video
        )

    else:

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        view_record, created = VideoView.objects.get_or_create(
            user=None,
            session_key=session_key,
            video=video
        )

    if created:

        should_count = True

    elif view_record.last_viewed <= cooldown_limit:

        view_record.last_viewed = now

        view_record.save(
            update_fields=["last_viewed"]
        )

        should_count = True

    if should_count:

        Video.objects.filter(
            id=video.id
        ).update(
            views=F("views") + 1
        )

        video.refresh_from_db(
            fields=["views"]
        )


def index(request):

    videos_queryset = Video.objects.select_related(
        "channel",
        "channel__owner"
    ).order_by(
        "-created_at"
    )

    paginator = Paginator(
        videos_queryset,
        VIDEOS_PER_PAGE
    )

    page_number = request.GET.get(
        "page"
    )

    videos = paginator.get_page(
        page_number
    )

    return render(
        request,
        "videos/index.html",
        {
            "videos": videos
        }
    )


def search(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "recent")
    category = request.GET.get("category", "").strip()
    channel_filter = request.GET.get("channel", "").strip()
    date_filter = request.GET.get("date", "").strip()
    min_views_raw = request.GET.get("min_views", "").strip()

    if sort not in ["recent", "views"]:
        sort = "recent"

    valid_categories = {value for value, _ in Video.Category.choices}
    if category not in valid_categories:
        category = ""

    if date_filter not in ["", "today", "week", "month", "year"]:
        date_filter = ""

    try:
        min_views = max(int(min_views_raw), 0) if min_views_raw else None
    except ValueError:
        min_views = None
        min_views_raw = ""

    has_filters = any([query, category, channel_filter, date_filter, min_views is not None])
    videos_queryset = Video.objects.select_related("channel", "channel__owner")
    channels = Channel.objects.none()

    if query:
        videos_queryset = videos_queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(channel__name__icontains=query)
            | Q(channel__owner__username__icontains=query)
        )
        channels = Channel.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(owner__username__icontains=query)
        ).select_related("owner").distinct().order_by("name")

    if category:
        videos_queryset = videos_queryset.filter(category=category)
    if channel_filter:
        videos_queryset = videos_queryset.filter(
            Q(channel__name__icontains=channel_filter)
            | Q(channel__owner__username__icontains=channel_filter)
        )

    now = timezone.now()
    if date_filter == "today":
        videos_queryset = videos_queryset.filter(created_at__gte=now - timedelta(days=1))
    elif date_filter == "week":
        videos_queryset = videos_queryset.filter(created_at__gte=now - timedelta(days=7))
    elif date_filter == "month":
        videos_queryset = videos_queryset.filter(created_at__gte=now - timedelta(days=30))
    elif date_filter == "year":
        videos_queryset = videos_queryset.filter(created_at__gte=now - timedelta(days=365))

    if min_views is not None:
        videos_queryset = videos_queryset.filter(views__gte=min_views)

    videos_queryset = videos_queryset.distinct()
    if not has_filters:
        videos_queryset = Video.objects.none()
    elif sort == "views":
        videos_queryset = videos_queryset.order_by("-views", "-created_at")
    else:
        videos_queryset = videos_queryset.order_by("-created_at")

    paginator = Paginator(videos_queryset, VIDEOS_PER_PAGE)
    videos = paginator.get_page(request.GET.get("page"))
    pagination_params = request.GET.copy()
    pagination_params.pop("page", None)

    return render(request, "videos/search.html", {
        "query": query,
        "videos": videos,
        "channels": channels,
        "sort": sort,
        "category": category,
        "channel_filter": channel_filter,
        "date_filter": date_filter,
        "min_views_value": min_views_raw,
        "categories": get_video_categories(),
        "has_filters": has_filters,
        "pagination_query": pagination_params.urlencode(),
    })

def csrf_token_refresh(request):

    return JsonResponse(
        {
            "csrfToken": get_token(request)
        }
    )


@ensure_csrf_cookie
def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "videos:index"
            )

        return render(
            request,
            "videos/login.html",
            {
                "message":
                    "Nome de usuário ou senha inválidos."
            }
        )

    return render(
        request,
        "videos/login.html"
    )


def logout_view(request):

    logout(request)

    return redirect(
        "videos:index"
    )


@ensure_csrf_cookie
def register(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:

            return render(
                request,
                "videos/register.html",
                {
                    "message":
                        "As senhas não coincidem."
                }
            )

        try:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            user.save()

        except IntegrityError:

            return render(
                request,
                "videos/register.html",
                {
                    "message":
                        "Esse nome de usuário já está sendo utilizado."
                }
            )

        login(
            request,
            user
        )

        return redirect(
            "videos:index"
        )

    return render(
        request,
        "videos/register.html"
    )


@login_required
def create_channel(request):

    if request.user.has_channel:

        return redirect(
            "videos:channel",
            username=request.user.username
        )

    if request.method == "POST":

        name = request.POST["name"].strip()

        description = request.POST[
            "description"
        ].strip()

        avatar = request.FILES.get(
            "avatar"
        )

        if not name:

            return render(
                request,
                "videos/create_channel.html",
                {
                    "message":
                        "O canal precisa ter um nome."
                }
            )

        if Channel.objects.filter(
            name__iexact=name
        ).exists():

            return render(
                request,
                "videos/create_channel.html",
                {
                    "message":
                        "Já existe um canal com esse nome."
                }
            )

        Channel.objects.create(
            owner=request.user,
            name=name,
            description=description,
            avatar=avatar
        )

        return redirect(
            "videos:channel",
            username=request.user.username
        )

    return render(
        request,
        "videos/create_channel.html"
    )


@login_required
def edit_channel(request):

    if not request.user.has_channel:

        return redirect(
            "videos:create_channel"
        )

    channel = request.user.channel

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        avatar = request.FILES.get(
            "avatar"
        )

        if not name:

            return render(
                request,
                "videos/edit_channel.html",
                {
                    "channel": channel,
                    "message":
                        "O canal precisa ter um nome."
                }
            )

        existing_channel = Channel.objects.filter(
            name__iexact=name
        ).exclude(
            id=channel.id
        )

        if existing_channel.exists():

            return render(
                request,
                "videos/edit_channel.html",
                {
                    "channel": channel,
                    "message":
                        "Já existe um canal com esse nome."
                }
            )

        channel.name = name
        channel.description = description

        if avatar:
            channel.avatar = avatar

        channel.save()

        return redirect(
            "videos:channel",
            username=request.user.username
        )

    return render(
        request,
        "videos/edit_channel.html",
        {
            "channel": channel
        }
    )


@ensure_csrf_cookie
def channel_view(request, username):
    owner = get_object_or_404(User, username=username)
    channel = get_object_or_404(Channel, owner=owner)
    tab = request.GET.get("tab", "videos")
    if tab not in ["videos", "playlists", "about"]:
        tab = "videos"
    sort = request.GET.get("sort", "recent")
    if sort not in ["recent", "views"]:
        sort = "recent"

    videos = channel.videos.all()
    videos = videos.order_by("-views", "-created_at") if sort == "views" else videos.order_by("-created_at")

    playlists_queryset = Playlist.objects.filter(owner=owner).prefetch_related("items", "items__video")
    is_owner = request.user.is_authenticated and request.user == owner
    if not is_owner:
        playlists_queryset = playlists_queryset.filter(is_private=False)

    channel_stats = channel.videos.aggregate(total_views=Sum("views"))
    video_count = channel.videos.count()
    total_views = channel_stats["total_views"] or 0
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(subscriber=request.user, channel=channel).exists()

    return render(request, "videos/channel.html", {
        "channel": channel,
        "videos": videos,
        "playlists": playlists_queryset,
        "is_subscribed": is_subscribed,
        "subscriber_count": channel.subscribers.count(),
        "video_count": video_count,
        "total_views": total_views,
        "sort": sort,
        "tab": tab,
        "is_owner": is_owner,
    })

@login_required
def toggle_subscription(request, username):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    owner = get_object_or_404(
        User,
        username=username
    )

    channel = get_object_or_404(
        Channel,
        owner=owner
    )

    if channel.owner == request.user:

        return JsonResponse(
            {
                "error":
                    "Você não pode se inscrever no próprio canal."
            },
            status=400
        )

    subscription = Subscription.objects.filter(
        subscriber=request.user,
        channel=channel
    ).first()

    if subscription:

        subscription.delete()

        subscribed = False

    else:

        Subscription.objects.create(
            subscriber=request.user,
            channel=channel
        )

        if channel.owner != request.user:

            Notification.objects.create(
                recipient=channel.owner,
                actor=request.user,
                kind="subscription"
            )

        subscribed = True

    return JsonResponse(
        {
            "subscribed": subscribed,

            "subscriber_count":
                channel.subscribers.count()
        }
    )


@login_required
def subscriptions_feed(request):

    subscribed_channels = Channel.objects.filter(
        subscribers__subscriber=request.user
    )

    videos_queryset = Video.objects.filter(
        channel__in=subscribed_channels
    ).select_related(
        "channel",
        "channel__owner"
    ).order_by(
        "-created_at"
    )

    paginator = Paginator(
        videos_queryset,
        VIDEOS_PER_PAGE
    )

    page_number = request.GET.get(
        "page"
    )

    videos = paginator.get_page(
        page_number
    )

    return render(
        request,
        "videos/subscriptions.html",
        {
            "videos": videos
        }
    )


@login_required
def history(request):

    history_queryset = WatchHistory.objects.filter(
        user=request.user
    ).select_related(
        "video",
        "video__channel",
        "video__channel__owner"
    ).order_by(
        "-watched_at"
    )

    paginator = Paginator(
        history_queryset,
        VIDEOS_PER_PAGE
    )

    page_number = request.GET.get(
        "page"
    )

    history_items = paginator.get_page(
        page_number
    )

    return render(
        request,
        "videos/history.html",
        {
            "history_items": history_items
        }
    )


@login_required
def clear_history(request):

    if request.method == "POST":

        WatchHistory.objects.filter(
            user=request.user
        ).delete()

        messages.success(
            request,
            "Histórico limpo com sucesso."
        )

    return redirect(
        "videos:history"
    )


@login_required
def remove_history_item(request, video_id):
    if request.method == "POST":
        WatchHistory.objects.filter(user=request.user, video_id=video_id).delete()
        messages.success(request, "Vídeo removido do histórico.")
    return redirect("videos:history")


@login_required
def liked_videos(request):

    likes_queryset = Like.objects.filter(
        user=request.user
    ).select_related(
        "video",
        "video__channel",
        "video__channel__owner"
    ).order_by(
        "-created_at"
    )

    paginator = Paginator(
        likes_queryset,
        VIDEOS_PER_PAGE
    )

    page_number = request.GET.get(
        "page"
    )

    likes = paginator.get_page(
        page_number
    )

    return render(
        request,
        "videos/liked_videos.html",
        {
            "likes": likes
        }
    )


@login_required
def mark_notifications_read(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return JsonResponse(
        {
            "success": True,
            "unread_count": 0
        }
    )


@login_required
def notifications(request):

    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        "actor",
        "video",
        "comment"
    )[:50]

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return render(
        request,
        "videos/notifications.html",
        {
            "notifications":
                user_notifications
        }
    )


@login_required
def watch_later(request):

    items_queryset = WatchLater.objects.filter(
        user=request.user
    ).select_related(
        "video",
        "video__channel",
        "video__channel__owner"
    ).order_by(
        "-added_at"
    )

    paginator = Paginator(
        items_queryset,
        VIDEOS_PER_PAGE
    )

    page_number = request.GET.get(
        "page"
    )

    items = paginator.get_page(
        page_number
    )

    return render(
        request,
        "videos/watch_later.html",
        {
            "items": items
        }
    )


@login_required
def toggle_watch_later(request, video_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    video = get_object_or_404(
        Video,
        id=video_id
    )

    item = WatchLater.objects.filter(
        user=request.user,
        video=video
    ).first()

    if item:

        item.delete()
        saved = False

    else:

        WatchLater.objects.create(
            user=request.user,
            video=video
        )

        saved = True

    return JsonResponse(
        {
            "saved": saved
        }
    )


@login_required
def remove_watch_later(
    request,
    video_id
):

    if request.method == "POST":

        WatchLater.objects.filter(
            user=request.user,
            video_id=video_id
        ).delete()

        messages.success(
            request,
            "Vídeo removido de Assistir mais tarde."
        )

    return redirect(
        "videos:watch_later"
    )


@login_required
def playlists(request):

    user_playlists = Playlist.objects.filter(
        owner=request.user
    ).prefetch_related(
        "items",
        "items__video"
    )

    return render(
        request,
        "videos/playlists.html",
        {
            "playlists": user_playlists
        }
    )


@login_required
def create_playlist(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        is_private = (
            request.POST.get(
                "is_private"
            ) == "on"
        )

        if not name:

            return render(
                request,
                "videos/create_playlist.html",
                {
                    "message":
                        "A playlist precisa ter um nome."
                }
            )

        playlist = Playlist.objects.create(
            owner=request.user,
            name=name,
            description=description,
            is_private=is_private
        )

        messages.success(
            request,
            "Playlist criada com sucesso."
        )

        return redirect(
            "videos:playlist_detail",
            playlist_id=playlist.id
        )

    return render(
        request,
        "videos/create_playlist.html"
    )


def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    is_owner = request.user.is_authenticated and request.user == playlist.owner
    if playlist.is_private and not is_owner:
        raise Http404("Playlist privada.")
    if is_owner:
        normalize_playlist_positions(playlist)
    items = playlist.items.select_related(
        "video", "video__channel", "video__channel__owner"
    ).order_by("position", "added_at", "id")
    return render(request, "videos/playlist_detail.html", {
        "playlist": playlist,
        "items": items,
        "is_owner": is_owner,
    })

@login_required
def edit_playlist(request, playlist_id):

    playlist = get_object_or_404(
        Playlist,
        id=playlist_id,
        owner=request.user
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        is_private = (
            request.POST.get(
                "is_private"
            ) == "on"
        )

        if not name:

            return render(
                request,
                "videos/edit_playlist.html",
                {
                    "playlist": playlist,
                    "message":
                        "A playlist precisa ter um nome."
                }
            )

        playlist.name = name
        playlist.description = description
        playlist.is_private = is_private

        playlist.save()

        messages.success(
            request,
            "Playlist atualizada."
        )

        return redirect(
            "videos:playlist_detail",
            playlist_id=playlist.id
        )

    return render(
        request,
        "videos/edit_playlist.html",
        {
            "playlist": playlist
        }
    )


@login_required
def delete_playlist(request, playlist_id):

    playlist = get_object_or_404(
        Playlist,
        id=playlist_id,
        owner=request.user
    )

    if request.method == "POST":

        playlist.delete()

        messages.success(
            request,
            "Playlist excluída."
        )

        return redirect(
            "videos:playlists"
        )

    return render(
        request,
        "videos/delete_playlist.html",
        {
            "playlist": playlist
        }
    )


@login_required
def add_video_to_playlist(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method != "POST":
        return redirect("videos:watch", video_id=video.id)
    playlist_id = request.POST.get("playlist_id")
    if not playlist_id:
        return redirect("videos:watch", video_id=video.id)
    playlist = get_object_or_404(Playlist, id=playlist_id, owner=request.user)
    existing = PlaylistItem.objects.filter(playlist=playlist, video=video).first()
    if existing:
        messages.info(request, f'O vídeo já está na playlist "{playlist.name}".')
    else:
        next_position = (PlaylistItem.objects.filter(playlist=playlist).aggregate(max_position=Max("position"))["max_position"] or 0) + 1
        PlaylistItem.objects.create(playlist=playlist, video=video, position=next_position)
        playlist.save()
        messages.success(request, f'Vídeo adicionado à playlist "{playlist.name}".')
    return redirect("videos:watch", video_id=video.id)

@login_required
def remove_video_from_playlist(
    request,
    playlist_id,
    video_id
):

    playlist = get_object_or_404(
        Playlist,
        id=playlist_id,
        owner=request.user
    )

    video = get_object_or_404(
        Video,
        id=video_id
    )

    if request.method == "POST":

        deleted_count, _ = PlaylistItem.objects.filter(
            playlist=playlist,
            video=video
        ).delete()

        playlist.save()

        if deleted_count:
            messages.success(
                request,
                "Vídeo removido da playlist."
            )

    return redirect(
        "videos:playlist_detail",
        playlist_id=playlist.id
    )


@login_required
def move_playlist_item(request, playlist_id, item_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, owner=request.user)
    item = get_object_or_404(PlaylistItem, id=item_id, playlist=playlist)
    if request.method == "POST":
        direction = request.POST.get("direction")
        with transaction.atomic():
            items = normalize_playlist_positions(playlist)
            current_index = next((i for i, current in enumerate(items) if current.id == item.id), -1)
            target_index = current_index
            if direction == "up" and current_index > 0:
                target_index = current_index - 1
            elif direction == "down" and 0 <= current_index < len(items) - 1:
                target_index = current_index + 1
            if current_index >= 0 and target_index != current_index:
                other = items[target_index]
                item.position, other.position = other.position, item.position
                PlaylistItem.objects.bulk_update([item, other], ["position"])
    return redirect("videos:playlist_detail", playlist_id=playlist.id)


@login_required
def studio(request):
    if not request.user.has_channel:
        return redirect("videos:create_channel")
    category = request.GET.get("category", "").strip()
    valid_categories = {value for value, _ in Video.Category.choices}
    if category not in valid_categories:
        category = ""
    videos_queryset = Video.objects.filter(channel=request.user.channel).order_by("-created_at")
    if category:
        videos_queryset = videos_queryset.filter(category=category)
    paginator = Paginator(videos_queryset, 20)
    videos = paginator.get_page(request.GET.get("page"))
    return render(request, "videos/studio.html", {
        "videos": videos,
        "category": category,
        "categories": get_video_categories(),
    })


@login_required
def upload_video(request):
    if not request.user.has_channel:
        return redirect("videos:create_channel")
    context = {
        "title_value": "",
        "description_value": "",
        "category_value": Video.Category.OTHER,
        "categories": get_video_categories(),
    }
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", Video.Category.OTHER)
        valid_categories = {value for value, _ in Video.Category.choices}
        if category not in valid_categories:
            category = Video.Category.OTHER
        video_file = request.FILES.get("video_file")
        thumbnail = request.FILES.get("thumbnail")
        context.update(title_value=title, description_value=description, category_value=category)
        if not title:
            context["message"] = "O vídeo precisa ter um título."
            return render(request, "videos/upload.html", context)
        if len(title) > 200:
            context["message"] = "O título deve ter no máximo 200 caracteres."
            return render(request, "videos/upload.html", context)
        video_error = validate_video_upload(video_file)
        if video_error:
            context["message"] = video_error
            return render(request, "videos/upload.html", context)
        thumbnail_error = validate_thumbnail_upload(thumbnail)
        if thumbnail_error:
            context["message"] = thumbnail_error
            return render(request, "videos/upload.html", context)
        video = Video.objects.create(
            channel=request.user.channel,
            title=title,
            description=description,
            category=category,
            video_file=video_file,
            thumbnail=thumbnail,
        )
        messages.success(request, "Vídeo publicado com sucesso.")
        return redirect("videos:watch", video_id=video.id)
    return render(request, "videos/upload.html", context)

@ensure_csrf_cookie
def watch_video(request, video_id):
    video = get_object_or_404(Video.objects.select_related("channel", "channel__owner"), id=video_id)
    register_video_view(request, video)
    if request.user.is_authenticated:
        WatchHistory.objects.update_or_create(user=request.user, video=video)

    comment_sort = request.GET.get("comments", "recent")
    comments_queryset = video.comments.select_related("user").prefetch_related("replies__user").annotate(like_total=Count("likes"))
    if comment_sort == "oldest":
        comments_queryset = comments_queryset.order_by("created_at")
    elif comment_sort == "top":
        comments_queryset = comments_queryset.order_by("-like_total", "-created_at")
    else:
        comment_sort = "recent"
        comments_queryset = comments_queryset.order_by("-created_at")
    comments = list(comments_queryset)

    user_liked = user_disliked = user_saved_for_later = is_subscribed = False
    user_playlists = []
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, video=video).exists()
        user_disliked = Dislike.objects.filter(user=request.user, video=video).exists()
        user_saved_for_later = WatchLater.objects.filter(user=request.user, video=video).exists()
        is_subscribed = Subscription.objects.filter(subscriber=request.user, channel=video.channel).exists()
        user_playlists = Playlist.objects.filter(owner=request.user).order_by("-updated_at")
        for comment in comments:
            comment.user_liked = CommentLike.objects.filter(user=request.user, comment=comment).exists()
            comment.user_disliked = CommentDislike.objects.filter(user=request.user, comment=comment).exists()
    else:
        for comment in comments:
            comment.user_liked = False
            comment.user_disliked = False

    related_primary = list(Video.objects.filter(category=video.category).exclude(id=video.id).select_related("channel", "channel__owner").order_by("-views", "-created_at")[:8])
    related_videos = related_primary
    if len(related_primary) < 8:
        related_ids = [related.id for related in related_primary]
        related_extra = list(Video.objects.exclude(id__in=related_ids + [video.id]).select_related("channel", "channel__owner").order_by("-views", "-created_at")[:8-len(related_primary)])
        related_videos = related_primary + related_extra

    return render(request, "videos/watch.html", {
        "video": video,
        "comments": comments,
        "comment_sort": comment_sort,
        "user_liked": user_liked,
        "user_disliked": user_disliked,
        "user_saved_for_later": user_saved_for_later,
        "like_count": video.likes.count(),
        "dislike_count": video.dislikes.count(),
        "is_subscribed": is_subscribed,
        "subscriber_count": video.channel.subscribers.count(),
        "user_playlists": user_playlists,
        "related_videos": related_videos,
    })

@login_required
def edit_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, channel__owner=request.user)
    context = {
        "video": video,
        "title_value": video.title,
        "description_value": video.description,
        "category_value": video.category,
        "categories": get_video_categories(),
    }
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", Video.Category.OTHER)
        valid_categories = {value for value, _ in Video.Category.choices}
        if category not in valid_categories:
            category = Video.Category.OTHER
        thumbnail = request.FILES.get("thumbnail")
        video_file = request.FILES.get("video_file")
        context.update(title_value=title, description_value=description, category_value=category)
        if not title:
            context["message"] = "O vídeo precisa ter um título."
            return render(request, "videos/edit_video.html", context)
        if len(title) > 200:
            context["message"] = "O título deve ter no máximo 200 caracteres."
            return render(request, "videos/edit_video.html", context)
        if video_file:
            video_error = validate_video_upload(video_file)
            if video_error:
                context["message"] = video_error
                return render(request, "videos/edit_video.html", context)
        if thumbnail:
            thumbnail_error = validate_thumbnail_upload(thumbnail)
            if thumbnail_error:
                context["message"] = thumbnail_error
                return render(request, "videos/edit_video.html", context)
        video.title = title
        video.description = description
        video.category = category
        if thumbnail:
            video.thumbnail = thumbnail
        if video_file:
            video.video_file = video_file
        video.save()
        messages.success(request, "Vídeo atualizado com sucesso.")
        return redirect("videos:watch", video_id=video.id)
    return render(request, "videos/edit_video.html", context)

@login_required
def delete_video(request, video_id):

    video = get_object_or_404(
        Video,
        id=video_id,
        channel__owner=request.user
    )

    if request.method == "POST":

        username = video.channel.owner.username

        video.delete()

        return redirect(
            "videos:channel",
            username=username
        )

    return render(
        request,
        "videos/delete_video.html",
        {
            "video": video
        }
    )


@login_required
def toggle_like(request, video_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    video = get_object_or_404(
        Video,
        id=video_id
    )

    like = Like.objects.filter(
        user=request.user,
        video=video
    ).first()

    if like:

        like.delete()
        liked = False

    else:

        Dislike.objects.filter(
            user=request.user,
            video=video
        ).delete()

        Like.objects.create(
            user=request.user,
            video=video
        )

        if video.channel.owner != request.user:

            Notification.objects.get_or_create(
                recipient=video.channel.owner,
                actor=request.user,
                kind="like",
                video=video
            )

        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "disliked": False,
            "like_count":
                video.likes.count(),
            "dislike_count":
                video.dislikes.count()
        }
    )


@login_required
def toggle_dislike(request, video_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    video = get_object_or_404(
        Video,
        id=video_id
    )

    dislike = Dislike.objects.filter(
        user=request.user,
        video=video
    ).first()

    if dislike:

        dislike.delete()
        disliked = False

    else:

        Like.objects.filter(
            user=request.user,
            video=video
        ).delete()

        Dislike.objects.create(
            user=request.user,
            video=video
        )

        disliked = True

    return JsonResponse(
        {
            "liked": False,
            "disliked": disliked,
            "like_count":
                video.likes.count(),
            "dislike_count":
                video.dislikes.count()
        }
    )


@login_required
def add_comment(request, video_id):

    video = get_object_or_404(
        Video,
        id=video_id
    )

    if request.method == "POST":

        text = request.POST.get(
            "comment",
            ""
        ).strip()

        if text:

            comment = Comment.objects.create(
                user=request.user,
                video=video,
                text=text
            )

            if video.channel.owner != request.user:

                Notification.objects.create(
                    recipient=video.channel.owner,
                    actor=request.user,
                    kind="comment",
                    video=video,
                    comment=comment
                )

            messages.success(
                request,
                "Comentário publicado."
            )

    return redirect(
        "videos:watch",
        video_id=video.id
    )


@login_required
def edit_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        user=request.user
    )

    if request.method == "POST":

        text = request.POST.get(
            "comment",
            ""
        ).strip()

        if not text:

            return render(
                request,
                "videos/edit_comment.html",
                {
                    "comment": comment,
                    "message":
                        "O comentário não pode ficar vazio."
                }
            )

        comment.text = text

        comment.save(
            update_fields=["text"]
        )

        messages.success(
            request,
            "Comentário atualizado."
        )

        return redirect(
            "videos:watch",
            video_id=comment.video.id
        )

    return render(
        request,
        "videos/edit_comment.html",
        {
            "comment": comment
        }
    )


@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        user=request.user
    )

    video_id = comment.video.id

    if request.method == "POST":

        comment.delete()

        messages.success(
            request,
            "Comentário excluído."
        )

    return redirect(
        "videos:watch",
        video_id=video_id
    )


@login_required
def add_comment_reply(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    if request.method == "POST":

        text = request.POST.get(
            "reply",
            ""
        ).strip()

        if text:

            CommentReply.objects.create(
                user=request.user,
                comment=comment,
                text=text
            )

            if comment.user != request.user:

                Notification.objects.create(
                    recipient=comment.user,
                    actor=request.user,
                    kind="reply",
                    video=comment.video,
                    comment=comment
                )

            messages.success(
                request,
                "Resposta publicada."
            )

    return redirect(
        "videos:watch",
        video_id=comment.video.id
    )


@login_required
def edit_comment_reply(request, reply_id):
    reply = get_object_or_404(CommentReply, id=reply_id, user=request.user)
    if request.method == "POST":
        text = request.POST.get("reply", "").strip()
        if not text:
            return render(request, "videos/edit_reply.html", {"reply": reply, "message": "A resposta não pode ficar vazia."})
        reply.text = text
        reply.save(update_fields=["text"])
        messages.success(request, "Resposta atualizada.")
        return redirect("videos:watch", video_id=reply.comment.video.id)
    return render(request, "videos/edit_reply.html", {"reply": reply})


@login_required
def delete_comment_reply(request, reply_id):

    reply = get_object_or_404(
        CommentReply,
        id=reply_id,
        user=request.user
    )

    video_id = reply.comment.video.id

    if request.method == "POST":
        reply.delete()

        messages.success(
            request,
            "Resposta excluída."
        )

    return redirect(
        "videos:watch",
        video_id=video_id
    )


@login_required
def toggle_comment_like(request, comment_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    like = CommentLike.objects.filter(
        user=request.user,
        comment=comment
    ).first()

    if like:

        like.delete()
        liked = False

    else:

        CommentDislike.objects.filter(
            user=request.user,
            comment=comment
        ).delete()

        CommentLike.objects.create(
            user=request.user,
            comment=comment
        )

        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "disliked": False,
            "like_count":
                comment.likes.count(),
            "dislike_count":
                comment.dislikes.count()
        }
    )


@login_required
def toggle_comment_dislike(request, comment_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método inválido."
            },
            status=405
        )

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    dislike = CommentDislike.objects.filter(
        user=request.user,
        comment=comment
    ).first()

    if dislike:

        dislike.delete()
        disliked = False

    else:

        CommentLike.objects.filter(
            user=request.user,
            comment=comment
        ).delete()

        CommentDislike.objects.create(
            user=request.user,
            comment=comment
        )

        disliked = True

    return JsonResponse(
        {
            "liked": False,
            "disliked": disliked,
            "like_count":
                comment.likes.count(),
            "dislike_count":
                comment.dislikes.count()
        }
    )
