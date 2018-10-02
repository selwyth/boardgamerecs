from django.db import models

# Create your models here.
class BoardGame(models.Model):
    title = models.CharField(max_length=256)
    bgg_id = models.IntegerField()
    is_expansion = models.BooleanField(default=False)
    board_game_family = models.CharField(max_length=255, default='')
    genre = models.ManyToManyField('Genre')
    mechanism = models.ManyToManyField('Mechanism')
    game_format = models.ManyToManyField('GameFormat')

    def __str__(self):
        return self.title


class Genre(models.Model):
    genre = models.CharField(max_length=255)
    description = models.CharField(max_length=2500, default='')

    def __str__(self):
        return self.genre


class Mechanism(models.Model):
    mechanism = models.CharField(max_length=255)
    description = models.CharField(max_length=2500, default='')

    def __str__(self):
        return self.mechanism


class GameFormat(models.Model):
    game_format = models.CharField(max_length=255)
    code = models.CharField(max_length=6, default='')
    board_game = models.ManyToManyField(BoardGame)

    def __str__(self):
        return self.game_format


class BGGUser(models.Model):
    userid = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    bgg_collection = models.OneToOneField('BGGCollection', on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class BGGCollection(models.Model):
    boardgame = models.ForeignKey(BoardGame, on_delete=models.CASCADE)
    rating = models.FloatField(default=0, null=True)
    owned = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
