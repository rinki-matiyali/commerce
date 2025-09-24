

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from .models import *


def index(request):
    return render(request, "auctions/index.html",{
        "listings":Listings.objects.all()
    })
def show_item(request,listname):
    listing_detail=Listings.objects.get(name=listname)
    return render(request,"auctions/listing.html",{
        "item":listing_detail,
        "comments": listing_detail.listing.all()
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

def  watchlist(request,id):
    if request.method=="POST":
        item = request.POST.get("id")
        listing = get_object_or_404(Listings,id=item)
        watchlist_item = Watchlist.objects.filter(user=request.user,listing=listing)
        if watchlist_item.exists():
            watchlist_item.delete()
        else:
            watchlist.objects.create(user=request.User,listing=listing)
        return redirect('list',listing_id=listing.id)
    
def view_watchlist(request):
    return render(request,'auctions/watchlist.html',{
        "listings": Watchlist.objects.filter(user=request.user)
    })
def bidding(request):
    if request.method=="POST":
        no= int(request.POST.get("hidden"))
        listing_detail= Listings.objects.get( id =no)
        try:
            bid_value = float(request.POST.get('bid_value'))
        except (ValueError,TypeError):
            return redirect('index')
        if bid_value>listing_detail.starting_bid:
            Bidding.objects.create(
                bidder = request.user,
                listing = listing_detail,
                amount = bid_value
            )
        
            print("we are in the if block")
            return redirect('listing')
        else:
            print("we are in the else block")
            return redirect('index')
        # if bid value is greater than ending bid then update it
        # or if it is less or equal than starting bid then dont update it and send a message to the user
        # diplay the user that their bid is the highest bid
        

def addlisting(request):
    if request.method =="POST":
        # username = request.user.username
        user = request.user
        title = request.POST.get('Name')
        description= request.POST.get('description')
        try:
         starting_bid = float(request.POST.get('starting_bid'))
        except (ValueError,TypeError):
            # need to update
            return redirect('listing')
        is_open = 'bid_open' in request.POST
        Listings.objects.create(
            name = title,
            bid_open=is_open,
            starting_bid = starting_bid,
            description = description,
            owner = user
            )
        return redirect('index')
        
        
    else:
         return render(request,"auctions/add.html")
    

def comments(request):
    if request.method=="POST":
        user = request.user
        no= int(request.POST.get("hidden"))
        listing_id = Listings.objects.get( id =no)
        comment = request.POST.get('comment')
        Comments.objects.create(
            user = user,
            comment=comment,
            listing=listing_id
        )
        return  render(request,"auctions/listing.html",{
        "item":listing_id,
        "comments":listing_id.listing.all()
    })
    else:
        pass


    # notifications = request.user.notifications.filter(is_read = False)
    # notification.is_read = True
    # notification.save()
def winner(request,listing):
    highest_bid = listing.bids.order_by('-amount').first()
    if highest_bid:
        winner = highest_bid.bidder
        Notification.objects.create(
            user = winner,
            message=f"You won the auction for {listing.title} at ${highest_bid.amount}!"
        )
        listing.is_closed=True
        listing.winner = winner
        listing.save()