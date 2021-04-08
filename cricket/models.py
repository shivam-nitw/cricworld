from django.db import models

# Create your models here.

class Match(models.Model):
    unique_id = models.IntegerField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30)
    sub_type = models.CharField(max_length=30)
    teamone = models.CharField(max_length=50)
    teamtwo = models.CharField(max_length=50)
    scoreone = models.CharField(max_length=200)
    scoretwo = models.CharField(max_length=200)
    toss_winner_team = models.CharField(max_length=50)
    elected = models.CharField(max_length=10)
    winner_team = models.CharField(max_length=50)
    man_of_the_match = models.CharField(max_length =100)