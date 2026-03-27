# user/views/index.py

from django.shortcuts import render, redirect
from django.contrib import messages
from user.forms import ContactForm
from user.views.contact import process_contact
from user.views.portifolio import get_portifolio


def index(request):
    form_contact = ContactForm(request.POST or None)
    portifolio = get_portifolio(request)

    if request.method == "POST":
        if form_contact.is_valid():
            try:
                process_contact(form_contact, request)
                messages.success(request, "Mensagem enviada com sucesso!")
                return redirect("user:index")
            except Exception as e:
                print(f"Erro no contato: {e}")
                messages.error(request, "Erro ao enviar mensagem.")
    context = {
        "form": form_contact,
        "portifolio": portifolio
    }
    print(context)
    return render(request, "user/index.html", context)