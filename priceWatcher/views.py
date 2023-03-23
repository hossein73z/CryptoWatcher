from django.shortcuts import render

from priceWatcher.models import Pair


# Create your views here.
def pair_list(request):
    pairs = Pair.objects.all().values()
    return render(request, 'pair_list.html', {'pairs': pairs})
