from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notification.views.app_not_view import NotificationViewSet
from notification.views.push_notf_view import register_device, test_push
from django.shortcuts import render

router = DefaultRouter()
router.register('app', NotificationViewSet, basename='app-notification')

urlpatterns = [
    path('', include(router.urls)),
    path('device/register/', register_device, name='register-device'),
    path('push/test/', test_push, name='test-push'),
    path('push/tester/', lambda req: render(req, 'push_test.html'), name='push-tester'),
]
