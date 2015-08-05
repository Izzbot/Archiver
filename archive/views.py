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
            url = form.save(commit=False)
            url.collected_date = timezone.now()

            # connect up and fetch the website
            try:
                req = requests.request('GET', url.init_url)
            except:
                # if the connection breaks
                url.status = '404'
                url.title = ''
                url.final_url = url.init_url
                url.save()
                url = get_object_or_404(URL, pk=url.pk)
                return redirect('archive.views.url_detail', pk=url.pk)

            # assign data
            url.status = req.status_code
            url.final_url = req.url

            # Use bs4 to parse the data
            soup = BeautifulSoup(req.text)
            if not soup.title.string:
                url.title = ''
            else:
                url.title = soup.title.string

            url.save()
            url = get_object_or_404(URL, pk=url.pk)
            return redirect('archive.views.url_detail', pk=url.pk)
    else:
        form = URLForm()
    return render(request, 'archive/url_new.html', {'form': form})

def url_delete(request, pk):
    url = get_object_or_404(URL, pk=pk)
    url.delete()
    return redirect('archive.views.url_list')
