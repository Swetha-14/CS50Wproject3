from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxLengthValidator


CATEGORY_CHOICES = (
    ('F','Fashion'),
    ('T','Toys'),
    ('E','Electronics'),
    ('H','Home'),
    ('O','Other')
)

class User(AbstractUser):
    pass

class Auctionlisting(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, validators=[MaxLengthValidator(1000)])
    starting_bid = models.DecimalField(max_digits=11, decimal_places=2)
    item_slug = models.URLField(blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES,max_length=1, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    """category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="listings")"""

    def __str__(self):
        return (f"{self.title} \t Starting Bid = {self.starting_bid}")
    

class Bid(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey("Auctionlisting", on_delete=models.CASCADE, related_name="bids")
    bid_amount =  models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return (f"{self.listing} - Bid Amount of Rs.{self.bid_amount} by {self.user}")

class Comment(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey("Auctionlisting", on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=500, validators=[MaxLengthValidator(1000)])

    def __str__(self):
        return f" {self.user} - {self.listing} | Comment : {self.comment}"

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Auctionlisting, related_name="watchlist")

    def __str__(self):
        return f"{self.user}'s Watchlist"

