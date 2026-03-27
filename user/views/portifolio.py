from user.models import Portifolio







def get_portifolio(request):
    portifolio = Portifolio.objects.all()
    return portifolio