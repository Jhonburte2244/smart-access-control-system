from django.urls import path

from . import views


app_name = "rfid_cards"


urlpatterns = [

    path(
        "",
        views.rfid_card_list,
        name="rfid_card_list"
    ),

    path(
        "add/",
        views.rfid_card_add,
        name="rfid_card_add"
    ),

    path(
        "<int:card_id>/edit/",
        views.rfid_card_edit,
        name="rfid_card_edit"
    ),

    path(
        "<int:card_id>/toggle-status/",
        views.rfid_card_toggle_status,
        name="rfid_card_toggle_status"
    ),

    path(
        "<int:card_id>/delete/",
        views.rfid_card_delete,
        name="rfid_card_delete"
    ),
]