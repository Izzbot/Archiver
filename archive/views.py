from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import URL
from .forms import URLForm
from bs4 import BeautifulSoup
import requests
# import wayback

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
                url.wback_url = ''
                url.wback_date = ''
                url.final_url = url.init_url
                url.save()
                url = get_object_or_404(URL, pk=url.pk)
                return redirect('archive.views.url_detail', pk=url.pk)

            # assign data
            url.status = req.status_code
            url.final_url = req.url

            # Use bs4 to parse the data
            soup = BeautifulSoup(req.text)
            if soup is not None:
                url.title = soup.title.string
            else:
                url.title = ''

            # Use wayback to grab the data
            try:
                wb_json = requests.request('GET', 'http://timetravel.mementoweb.org/api/json/' + timezone.now().strftime('%Y%m%d') + url.final_url)
                url.wback_url = wb_json.mementos.closest.uri[0]
                url.wback_date = wb_json.mementos.closest.datetime
            except:
                url.wback_url = ''
                url.wback_date = timezone.now()

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
