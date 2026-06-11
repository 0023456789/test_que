from django.urls import path

from . import views

urlpatterns = [
    path("staff/register/", views.register_staff, name="register-staff"),
    path("staff/login/", views.login_staff, name="login-staff"),
    path("staff/import/<str:item_type>/", views.import_item, name="import-item"),
    path("staff/items/<str:item_type>/<int:item_id>/", views.update_item, name="update-item"),
    path("ui/import/computer/", views.computer_import_ui, name="computer-import-ui"),
    path("ui/import/mobile/", views.mobile_import_ui, name="mobile-import-ui"),
]
