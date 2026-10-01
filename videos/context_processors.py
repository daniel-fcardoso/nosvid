from .models import Notification, Subscription


def notifications_context(request):
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "popup_notifications": [],
            "sidebar_subscriptions_primary": [],
            "sidebar_subscriptions_extra": [],
            "has_more_subscriptions": False,
        }
    notifications = list(
        Notification.objects.filter(recipient=request.user).select_related(
            "actor", "actor__channel", "video", "comment"
        )[:20]
    )
    subscriptions = list(
        Subscription.objects.filter(subscriber=request.user).select_related(
            "channel", "channel__owner"
        ).order_by("channel__name")[:20]
    )
    return {
        "unread_notifications_count": Notification.objects.filter(recipient=request.user, is_read=False).count(),
        "popup_notifications": notifications,
        "sidebar_subscriptions_primary": subscriptions[:5],
        "sidebar_subscriptions_extra": subscriptions[5:],
        "has_more_subscriptions": len(subscriptions) > 5,
    }
