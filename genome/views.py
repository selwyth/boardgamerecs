from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from .forms import BGGUserForm, GenomeForm
from .models import BoardGame, Genre, Mechanism, BGGUser, BGGCollection

from boardgamegeek import BGGClient
from collections import defaultdict


form = GenomeForm()
user_form = BGGUserForm()

# Create your views here.
def index(request):
    return render(request, 'genome/index.html')


def genome(request):
    form = GenomeForm()
    user_form = BGGUserForm()
    genres = Genre.objects.all()
    mechanisms = Mechanism.objects.all()
    return render(request, 'genome/genome.html', {
        'form': form,
        'user_form': user_form,
        'genres': genres,
        'mechanisms': mechanisms,
    })


def boardgame_detail(request, bgg_id, recs=None):
    boardgame = get_object_or_404(BoardGame, bgg_id=bgg_id)

    combined_score = _recommend_boardgames(boardgame)
    combined_score = sorted(combined_score.items(), key=lambda x: -x[1])

    form = GenomeForm()
    user_form = BGGUserForm()
    return render(request, 'genome/boardgame_detail.html', {
        'boardgame': boardgame,
        'form': form,
        'user_form': user_form,
        'recs': combined_score
    })


def retrieve_recommendations(request):
    form = GenomeForm(request.POST)
    if form.is_valid():
        boardgame = get_object_or_404(BoardGame, title=form.cleaned_data['title'])
        return HttpResponseRedirect(reverse('genome:boardgame_detail', args=(boardgame.bgg_id, )))

    user_form = BGGUserForm()
    return render(request, 'genome/genome.html', {'form': form, 'user_form': user_form})


def _find_and_score_matches(boardgame, attribute):
    """
    Accepts a boardgame and attribute and returns a dict keyed on boardgames with the values
    being what % of genres were matched for each boardgame, with denominator being the longer
    of the two
    """
    bg_attribute = getattr(boardgame, attribute)
    attributes = bg_attribute.all()
    num_attributes = attributes.count()
    related_by_attr = [a.boardgame_set.all() for a in attributes]

    attr_matched_games = defaultdict(float)
    for l_of_g in related_by_attr:
        for matched_game in l_of_g:
            num_attributes_b = getattr(matched_game, attribute).count()
            if matched_game == boardgame:  # Do not match against itself
                continue
            attr_matched_games[matched_game] += 1 / max(num_attributes, num_attributes_b)

    return attr_matched_games


def _combine_two_scores(scores_a, scores_b):
    """
    Takes two dicts keyed on boardgames and valued on score, averages them and ranks them
    in descending order
    """
    combined_score = { k: int((scores_a.get(k, 0) + scores_b.get(k, 0)) * 100 / 2)
                       for k in set(scores_a) | set(scores_b) }
    return combined_score


def _recommend_boardgames(boardgame):
    """
    Given a boardgame object, returns a dict keyed on board games and valued on score,
    in descending order of score
    """
    genre_matched_games = _find_and_score_matches(boardgame, 'genre')
    mechanism_matched_games = _find_and_score_matches(boardgame, 'mechanism')
    return _combine_two_scores(genre_matched_games, mechanism_matched_games)


def retrieve_user_collection(request):
    user_form = BGGUserForm(request.POST)
    if user_form.is_valid():
        return HttpResponseRedirect(reverse('genome:user',
                                    kwargs={'username': user_form.cleaned_data['username'],
                                            'owned': user_form.cleaned_data.get('owned', 0),
                                            'rating': user_form.cleaned_data.get('rating', 7)}))

    form = GenomeForm()
    return render(request, 'genome/genome.html', {'form': form, 'user_form': user_form})


def user(request, username, owned, rating):
    bgg = BGGClient(retries=10, retry_delay=10)
    coll = bgg.collection(username)
    running_score = defaultdict(float)
    n = 0
    for game in coll:
        game_obj, game_created = BoardGame.objects.get_or_create(title=game.name, bgg_id=game.id)
        coll_obj, created = BGGCollection.objects.update_or_create(
            boardgame=game_obj,
            rating=game.rating,
            owned=bool(game.owned),
            comment=game.comment,
        )

        if game_created:  # Newly added board games would not have genre and mechanism
            continue

        if bool(owned) and not bool(game.owned):
            continue

        if game.rating is not None:
            if rating > game.rating:
                continue

        combined_score = _recommend_boardgames(game_obj)
        n += 1

        for k, v in combined_score.items():
            running_score[k] += v

    running_score = {k: v / n for k, v in running_score.items()}
    running_score = sorted(running_score.items(), key=lambda x: -x[1])

    return render(request, 'genome/user.html', {
        'username': username,
        'recs': running_score,
        'form': form,
        'user_form': user_form,
    })