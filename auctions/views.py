from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Auctionlisting, Bid, Comment, Watchlist
from .forms import CreateForm

global current_bids
current_bids =[]
listings = Auctionlisting.objects.filter(active=True)
for listing in listings:
    if listing.bids.exists():
        bids = listing.bids.all().order_by("id").reverse()
        recent_bid = bids[0].bid_amount
    else:
        recent_bid = listing.starting_bid

    current_bids.append({
        "value": recent_bid,
        "listing": listing.id
        })


def index(request):
    return render(request, "auctions/index.html",{
        "listings":Auctionlisting.objects.filter(active=True),
        "current_bids":current_bids
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def category(request):
    return render(request, "auctions/category.html")

def choices(request, letter):
    choice = Auctionlisting.objects.filter(category=letter)
    if choice:
        for i in choice:
            name = i.get_category_display
    return render(request, "auctions/choice.html",{
        "listings":choice,
        "current_bids":current_bids,
        "name":name
    })

def watchlist(request):
    if hasattr(request.user, 'watchlist'):
        listings = request.user.watchlist.listings.all()

    else:
        listings = []

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "current_bids": current_bids
    })

@login_required
def create(request):
    if request.method == "POST":
        post = request.POST.copy()
        post["user"] = User.objects.get(pk=request.user.id)
        form = CreateForm(post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))

        return render(request, "auctions/create.html", {
            "form": form,
            "messages": form.errors.as_data
        })  
    
    return render(request, "auctions/create.html", {
        "form": CreateForm()
    })


def listing(request, id):
    listing = Auctionlisting.objects.get(pk=id)
    watchlist = False

    if request.user.is_authenticated:
        if hasattr(request.user, 'watchlist') and request.user.watchlist.listings.filter(pk=listing.id).exists():
            watchlist = True

    recent_bid = None 
    if listing.bids.exists():
        bids = listing.bids.all().order_by("id").reverse()
        recent_bid = bids[0].bid_amount
    category = listing.category
    if category:
        name = listing.get_category_display

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, 'Log in to submit comments, place bids and more!')
            return HttpResponseRedirect(reverse("listing", args=[listing.id]))

        else:
            if request.POST["type"] == "comment":
                if not request.POST["content"]:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "current_bid": recent_bid or listing.starting_bid,
                        "watchlisted": watchlist,
                        "comment_error": "Content is required"
                    })
    
                comment = Comment(
                    user = User.objects.get(pk=request.user.id),
                    listing = listing,
                    comment = request.POST["content"]
        
                )

                comment.save()
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))

            elif request.POST["type"] == "bid":
                bid = Bid(
                    user = User.objects.get(pk=request.user.id),
                    listing = listing,
                    bid_amount = float(request.POST["value"])
                )
                
                if bid.bid_amount < listing.starting_bid:
                    messages.warning(request, 'Your bid must be greater or equal to the current bid')
                if listing.bids.exists() and "{:.2f}".format(bid.bid_amount) <= "{:.2f}".format(recent_bid):
                    messages.warning(request, 'Your bid must be greater than the current bid')
                else:
                    bid.save()
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))

            elif request.POST["type"] == "close":
                listing.active = False
                listing.save()
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
            
            elif request.POST["type"] == "watchlist":
                if watchlist:
                    listings = request.user.watchlist.listings
                    listings.remove(listing)
                    print(listings.all())
    
                else:
                    if not hasattr(request.user, 'watchlist'):
                        request.user.watchlist = Watchlist()
                        watchlist = request.user.watchlist
                        watchlist.save()

                    listings = request.user.watchlist.listings
                    listings.add(listing)
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))

    if not listing.active:
        if listing.bids.exists():
            last_bid = listing.bids.all().order_by("id").reverse()[0]
            winner = request.user.id == last_bid.user.id
            
        else:
            winner = False
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "current_bid": recent_bid or listing.starting_bid,
            "watchlisted": watchlist,
            "user_is_winner": winner,
            "name":name,
            "category":category 
            })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_bid":recent_bid or listing.starting_bid,
        "watchlisted": watchlist,
        "name":name,
        "category":category
    }) 

