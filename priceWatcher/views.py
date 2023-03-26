from django.shortcuts import render, redirect

from CryptoWatcher.functions.Coloring import red, bright, green
from priceWatcher.models import Pair


# Create your views here.
def pair_list(request):
    pairs: list[Pair] = Pair.objects.all().values()
    return render(request, 'pair_list.html', {'pairs': pairs})


def new_pair(request):
    return render(request, 'new_pair.html', {})


def add_pair(request):
    data = request.GET.dict()

    try:
        Pair.objects.get(currency=data['currency'].upper(), base=data['base'].upper())
        print(red("Already Exists"))
    except Pair.DoesNotExist:
        pair = Pair()
        pair.currency = data['currency'].upper()
        pair.base = data['base'].upper()
        pair.save()
        print(green("New Pair Added"))
    except Exception as e:
        print(red(e))

    pairs: list[Pair] = Pair.objects.all().values()
    return redirect('/pair_list', {'pairs': pairs})
