from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Listings, CATEGORY_CHOICES, Watchlist, Bidding, Comments, Notification
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "auctions/login.html")

    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirmation")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "auctions/register.html")

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("index")

        except:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html")

    return render(request, "auctions/register.html")

# HOME PAGE – SEARCH + CATEGORY + SORT + PAGINATION
def index(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', 'all')
    sort = request.GET.get('sort', 'newest')
    page = request.GET.get('page', 1)

    listings = Listings.objects.all()

    # FILTER BY CATEGORY
    if category != "all":
        listings = listings.filter(category=category)

    # SEARCH
    if q:
        listings = listings.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(owner__username__icontains=q)
        )

    # SORT
    if sort == "newest":
        listings = listings.order_by("-created_at")
    elif sort == "oldest":
        listings = listings.order_by("created_at")
    elif sort == "highbid":
        listings = sorted(
            listings,
            key=lambda x: x.bids.order_by("-amount").first().amount if x.bids.exists() else 0,
            reverse=True
        )
    elif sort == "lowbid":
        listings = sorted(
            listings,
            key=lambda x: x.bids.order_by("amount").first().amount if x.bids.exists() else 0
        )

    paginator = Paginator(listings, 8)
    page_obj = paginator.get_page(page)

    return render(request, "auctions/index.html", {
        "listings": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "selected_category": category,
        "selected_sort": sort,
        "categories": CATEGORY_CHOICES
    })


# LISTING PAGE
def show_item(request, listing_id):
    item = get_object_or_404(Listings, id=listing_id)

    comments = Comments.objects.filter(listing = item)
    highest_bid = item.bids.order_by("-amount").first()

    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, listing=item).exists()

    return render(request, "auctions/listing.html", {
        "item": item,
        "comments": comments,
        "highest_bid": highest_bid,
        "in_watchlist": in_watchlist
    })


# ADD LISTING
@login_required
def addlisting(request):
    if request.method == "POST":
        title = request.POST.get("Name")
        description = request.POST.get("description")
        category = request.POST.get("category", "art")

        try:
            starting_bid = float(request.POST.get("starting_bid"))
        except:
            messages.error(request, "Invalid starting bid.")
            return redirect("listing")

        image_file = request.FILES.get("image")

        listing = Listings.objects.create(
            name=title,
            description=description,
            starting_bid=starting_bid,
            category=category,
            owner=request.user,
            bid_open=True
        )

        if image_file:
            listing.image = image_file
            listing.save()

        messages.success(request, "Listing created successfully.")
        return redirect("index")

    return render(request, "auctions/add.html", {"categories": CATEGORY_CHOICES})


# WATCHLIST TOGGLE
@login_required
def watchlist_toggle(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    listing_id = request.POST.get("listing_id")
    listing = get_object_or_404(Listings, id=listing_id)

    entry = Watchlist.objects.filter(user=request.user, listing=listing).first()

    if entry:
        entry.delete()
        messages.success(request, "Removed from watchlist.")
    else:
        Watchlist.objects.create(user=request.user, listing=listing)
        messages.success(request, "Added to watchlist.")

    return redirect("list", listing_id=listing.id)


# VIEW WATCHLIST
@login_required
def view_watchlist(request):
    items = Watchlist.objects.filter(user=request.user).order_by("-added_at")
    return render(request, "auctions/watchlist.html", {"watchlist_items": items})


# BIDDING
@login_required
def bidding(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    listing_id = request.POST.get("listing_id")
    listing = get_object_or_404(Listings, id=listing_id)

    if not listing.bid_open:
        messages.error(request, "This auction is closed.")
        return redirect("list", listing_id=listing.id)

    try:
        bid_value = Decimal(request.POST.get("bid_value"))
    except:
        messages.error(request, "Invalid bid.")
        return redirect("list", listing_id=listing.id)

    highest = listing.bids.order_by("-amount").first()
    minimum = Decimal(str(listing.starting_bid))

    if highest:
        minimum = max(minimum, highest.amount + Decimal("0.01"))

    if bid_value < minimum:
        messages.error(request, f"Your bid must be at least ₹{minimum}.")
        return redirect("list", listing_id=listing.id)

    Bidding.objects.create(
        listing=listing,
        bidder=request.user,
        amount=bid_value
    )

    messages.success(request, f"Your bid of ₹{bid_value} has been placed.")
    return redirect("list", listing_id=listing.id)


# COMMENTS
@login_required
def comments(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    listing_id = request.POST.get("listing_id")
    comment_body = request.POST.get("comment", "").strip()

    if not comment_body:
        messages.error(request, "Comment cannot be empty.")
        return redirect("list", listing_id=listing_id)

    listing = get_object_or_404(Listings, id=listing_id)

    Comments.objects.create(
        listing=listing,
        user=request.user,
        comment=comment_body
    )

    messages.success(request, "Comment posted.")
    return redirect("list", listing_id=listing.id)


# CLOSE AUCTION
@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listings, id=listing_id)

    if request.user != listing.owner:
        messages.error(request, "You cannot close this auction.")
        return redirect("list", listing_id=listing.id)

    if not listing.bid_open:
        messages.info(request, "Auction already closed.")
        return redirect("list", listing_id=listing.id)

    highest = listing.bids.order_by("-amount").first()

    listing.bid_open = False

    if highest:
        listing.winner = highest.bidder
        listing.ending_bid = highest.amount
        Notification.objects.create(
            user=highest.bidder,
            message=f"You won the auction for {listing.name} at ₹{highest.amount}!"
        )
        messages.success(request, f"Auction closed. Winner: {highest.bidder.username}")
    else:
        messages.info(request, "Auction closed. No bids placed.")

    listing.save()

    return redirect("list", listing_id=listing.id)
@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    user_listings = Listings.objects.filter(owner=profile_user)
    user_bids = Bidding.objects.filter(bidder=profile_user)
    user_comments = Comments.objects.filter(user=profile_user)
    auctions_won = Listings.objects.filter(winner=profile_user)

    return render(request, "auctions/profile.html", {
        "profile_user": profile_user,
        "user_listings": user_listings,
        "user_bids": user_bids,
        "user_comments": user_comments,
        "auctions_won": auctions_won
    })
@login_required
def my_listings(request):
    user_listings = Listings.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "auctions/my_listings.html", {
        "listings": user_listings
    })
