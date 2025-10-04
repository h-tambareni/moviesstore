from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    amount_left = models.PositiveIntegerField(default=0, null=True, blank=True, help_text="Number of movies left in stock (optional)")
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255, help_text="Title of the movie you want to request")
    movie_description = models.TextField(help_text="Brief description of the movie and why it should be added")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, help_text="Whether the admin has processed this petition")
    
    def __str__(self):
        return f"Petition for: {self.movie_title}"
    
    def get_yes_votes_count(self):
        return self.votes.filter(vote_type='yes').count()
    
    def get_no_votes_count(self):
        return self.votes.filter(vote_type='no').count()
    
    def get_total_votes_count(self):
        return self.votes.count()
    
    def has_user_voted(self, user):
        if user.is_authenticated:
            return self.votes.filter(user=user).exists()
        return False
    
    def get_user_vote(self, user):
        if user.is_authenticated:
            vote = self.votes.filter(user=user).first()
            return vote.vote_type if vote else None
        return None

class Vote(models.Model):
    VOTE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=3, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['petition', 'user']  # Each user can only vote once per petition
    
    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on {self.petition.movie_title}"