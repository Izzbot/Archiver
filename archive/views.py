from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import URL
from .forms import URLForm
from bs4 import BeautifulSoup
import requests

def url_list(request):
    urls = URL.objects.order_by('collected_date')
    return render(request, 'archive/url_list.html', {'urls': urls})

def url_detail(request, pk):
    url = get_object_or_404(URL, pk=pk)
    return render(request, 'archive/url_detail.html', {'url': url})

def url_new(request):
    if request.method == "POST":
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.save(commit=false)
            url.collected_date = timezone.now()

            # connect up and fetch the website
            req = requests.get(url.init_url)
            url.status = req.status_code
            url.final_url = req.url

            # Use bs4 to parse the data
            data = req.read()
            soup = BeautifulSoup(data)
            url.title = soup.title.string
            url.save()
            url = get_object_or_404(URL, pk=pk)
            return redirect('archive.views.url_detail', pk=url.pk)
    else:
        url = URLForm()
    return render(request, 'archive/url_new.html', {'form': form})

def url_delete(request, pk):
    url = get_object_or_404(URL, pk=pk)
    url.delete()
    urls = URL.objects.order_by('collected_date')
    return redirect('archive.views.url_detail', {'urls': urls})
