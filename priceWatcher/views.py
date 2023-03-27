import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse

from CryptoWatcher.functions.Coloring import red, green
from priceWatcher.models import Pair


# Create your views here.
def pair_list(request):
    pairs: list[Pair] = Pair.objects.all().values()
    return render(request, 'pair_list.html', {'pairs': pairs})


def add_pair(request):
    pair = request.GET.dict()['currency'].split("-")

    currency = pair[0]
    base = pair[1]

    try:
        Pair.objects.get(currency=currency.upper(), base=base.upper())
        print(red("Already Exists"))
    except Pair.DoesNotExist:
        pair = Pair()
        pair.currency = currency.upper()
        pair.base = base.upper()
        pair.save()
        print(green("New Pair Added"))
    except Exception as e:
        print(red(e))

    pairs: list[Pair] = Pair.objects.all().values()
    return redirect('/pair_list', {'pairs': pairs})


def kucoin_symbols(request):
    pair_str = request.GET['pair']

    symbols = []
    with open("CryptoWatcher/statics/all_symbols.json", "r") as f:
        symbols = f.read()
        symbols = json.loads(symbols)
        start = [v for v in symbols if v.startswith(pair_str)]
        start.sort()
        rest = [v for v in symbols if (pair_str in v) and (not v.startswith(pair_str))]
        rest.sort()
        symbols = start + rest

    if symbols:
        return JsonResponse(symbols, safe=False)
    else:
        return JsonResponse(None, safe=False)


def prices(request):
    pairs = Pair.objects.all()

    if pairs:
        pair_dicts = []
        for pair in pairs:
            date = f"{pair.price_date.hour}:{pair.price_date.minute}:{pair.price_date.second}"
            pair_dicts.append({'id': pair.id, 'price': pair.price, 'date': date})

        return JsonResponse(pair_dicts, safe=False)
    else:
        return JsonResponse(None, safe=False)
