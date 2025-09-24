from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
# HarryPotter 1234
# RonWeasly 12345
# Hermione Granger 12345


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

class Listings(models.Model):
    name = models.CharField()
    # image = models.ImageField()
    bid_open=models.BooleanField()
    starting_bid = models.FloatField(default=0.0)
    # Null = true allows null values to be stored in database
    # blank=true  field is not required in forms 
    ending_bid = models.FloatField(null=True,blank=True)
    description = models.TextField()
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    winner =models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="auctions_won")

    def __str__(self):
        return f"{self.name} by {self.owner.username} "
    
class Watchlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="watchlist_items")
    listing = models.ForeignKey(Listings,on_delete=models.CASCADE,related_name="watched")
    added_at = models.DateTimeField(auto_now_add=True)
# prevents duplicates
    class Meta:
        unique_together =('user','listing')

    def __str__(self):
        return f"{self.listing.name} added on {self.added_at}"
    
class Comments(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    listing = models.ForeignKey(Listings,on_delete=models.CASCADE,related_name="listing")   
    comment = models.TextField(null=True) 
    posted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.comment} made by {self.user}"
    
class Bidding(models.Model):
    listing = models.ForeignKey(Listings,on_delete=models.CASCADE,related_name="bids")
    bidder = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bids")
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"
    

class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default = False)