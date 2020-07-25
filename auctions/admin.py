from django.contrib import admin

from .models import User, Auctionlisting, Bid, Comment, Watchlist

admin.site.register(User)
admin.site.register(Auctionlisting)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)
