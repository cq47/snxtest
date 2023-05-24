from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/updates/<int:instrument_id>/<str:tf>", consumers.UpdatesConsumer.as_asgi()),
    path("ws/updates/<int:instrument_id>", consumers.IIDUpdatesConsumer.as_asgi()),
    path("ws/updates/list", consumers.ListUpdatesConsumer.as_asgi()),

    path("ws/account/<int:user_id>", consumers.AccountUpdatesConsumer.as_asgi()),
]