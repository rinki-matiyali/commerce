from django.contrib import admin
from .models import *
# Register your models here.
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user","listing","added_at")
    list_filter = ("added_at",)
    ordering = ("-added_at",)
admin.site.register(User)
admin.site.register(Listings)

admin.site.register(Watchlist,WatchlistAdmin)
admin.site.register(Comments)
admin.site.register(Notification)
admin.site.register(Bidding)