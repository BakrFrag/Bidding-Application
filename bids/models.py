from django.db import models

class Bid(models.Model):
    """
    Bid model represents a bid placed by a user.
    """
    name = models.CharField(max_length=255)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Start: {self.initial_price}"
    class Meta:
        ordering = ['-created_at']

class BidHistory(models.Model):
    """
    BidHistory model represents the history of bids associated with a Bid.
    """

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='history')
    bidder_name = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.bidder_name} bid {self.price} on {self.bid.name}"

    class Meta:
        verbose_name_plural = "Bid Histories"
        ordering = ['-price']