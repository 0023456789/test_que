from django.urls import path
from .views import ChatRAGView, ProductActionSignalView

urlpatterns = [
    path('api/chat/', ChatRAGView.as_view(), name='chat_api'),
    path('api/signal/action/', ProductActionSignalView.as_view(), name='signal_action'),
]