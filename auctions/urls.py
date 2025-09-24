from django.urls import path

from . import views
# app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add/",views.addlisting,name="listing"),
    path("watchlist/",views.view_watchlist,name="watchlist"),
    path("list/<str:listname>",views.show_item,name="list"),
    path("comment/",views.comments,name="comment"),
    path("bidding/",views.bidding,name="bid")
]
