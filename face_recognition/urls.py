
from django.urls import path

from . import views


app_name = "face_recognition"


urlpatterns = [

    # ========================================================
    # FACE TEMPLATE MANAGEMENT
    # ========================================================

    path(
        "",
        views.face_template_list,
        name="face_template_list",
    ),

    path(
        "add/",
        views.face_template_add,
        name="face_template_add",
    ),

    path(
        "<int:pk>/",
        views.face_template_detail,
        name="face_template_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.face_template_edit,
        name="face_template_edit",
    ),

    path(
        "<int:pk>/delete/",
        views.face_template_delete,
        name="face_template_delete",
    ),

    # ========================================================
    # FACE RECOGNITION TEST
    # ========================================================

    path(
        "test/",
        views.recognize_face,
        name="recognize_face",
    ),
]
