from django.contrib import admin
from .models import BoardGame, Genre, Mechanism, GameFormat

# Register your models here.
admin.site.register(BoardGame)
admin.site.register(Genre)
admin.site.register(Mechanism)
admin.site.register(GameFormat)