from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .serializers import ConfigSerializer
from .utils import get_config


class ConfigAPIView(APIView):
    """
    API endpoint for global site configuration.
    Returns all fields of SiteConfiguration singleton.
    """

    def get(self, request, format=None):
        config = get_config()
        if config:
            serializer = ConfigSerializer(config)
            return Response(serializer.data)
        return Response({}, status=404)


class LimitsAPIView(APIView):
    """Return effective limits for the requesting user.

    Response shape:
    {
        "image_max": int,
        "text_limits": {"title": int, "body": int}
    }
    """

    permission_classes = []  # AllowAny
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get(self, request, format=None):
        from .serializers import LimitsSerializer
        from .utils import get_user_image_limit, get_user_text_limits

        user = request.user if request.user.is_authenticated else None

        # Build a safer per-user cache key that includes a few auth flags so
        # that different kinds of users who happen to share numeric PKs
        # (e.g. during tests or odd DB resets) won't collide.
        if user:
            user_key = f"{user.pk}:{int(getattr(user, 'is_superuser', False))}:{int(getattr(user, 'is_staff', False))}"
        else:
            user_key = "anon"

        # Cache per-user (or per-anonymous) effective limits for a short TTL
        cache_key = f"core:limits:{user_key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        image_max = get_user_image_limit(user)
        text_limits = get_user_text_limits(user)

        data = {"image_max": image_max, "text_limits": text_limits}
        # cache for 30 seconds — short TTL to reflect recent admin changes
        try:
            cache.set(cache_key, data, 30)
        except Exception:
            # cache may not be configured; ignore failures
            pass

        serializer = LimitsSerializer(data)
        return Response(serializer.data)
