from django.shortcuts import render


def main(request):
    return render(request, 'main/main.html')
    
def catalog(request):
    return render(request, 'main/catalog.html')