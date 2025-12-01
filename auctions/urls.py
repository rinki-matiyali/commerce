from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    # HOME / INDEX PAGE
    path("", views.index, name="index"),

    # AUTH
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # LISTINGS
    path("add/", views.addlisting, name="listing"),
    path("list/<int:listing_id>/", views.show_item, name="list"),
    path("close/<int:listing_id>/", views.close_auction, name="close_auction"),

    # BIDDING + COMMENTS
    path("bidding/", views.bidding, name="bid"),
    path("comment/", views.comments, name="comment"),

    # WATCHLIST
    path("watchlist/", views.view_watchlist, name="watchlist"),
    path("watch/toggle/", views.watchlist_toggle, name="watch_toggle"),

    # PROFILE + MY LISTINGS
    path("profile/<str:username>/", views.profile, name="profile"),
    path("mylistings/", views.my_listings, name="my_listings"),
]


# SERVE MEDIA FILES IN DEBUG MODE (IMAGES)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
