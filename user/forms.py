from django import forms
from django.core.exceptions import ValidationError
from .models import Contact
import re
from phonenumber_field.formfields import PhoneNumberField


class ContactForm(forms.ModelForm):
    """
    Formulário de contato com validações personalizadas
    """

    nome = forms.CharField(
        label='Nome completo',
        max_length=200,
        strip=True,
        error_messages={
            'required': 'Por favor, informe seu nome.',
            'max_length': 'Nome muito longo (máximo 200 caracteres).'
        }
    )

    email = forms.EmailField(
        label='E-mail',
        error_messages={
            'required': 'Por favor, informe seu e-mail.',
            'invalid': 'Por favor, informe um e-mail válido (ex: nome@dominio.com).'
        }
    )

    telefone = PhoneNumberField(
        label='Telefone / WhatsApp',
        region='BR',
        error_messages={
            'invalid': 'Digite um número válido com DDD.'
        }
    )

    assunto = forms.CharField(
        label='Assunto',
        max_length=200,
        strip=True,
        error_messages={
            'required': 'Por favor, informe o assunto da mensagem.',
            'max_length': 'Assunto muito longo (máximo 200 caracteres).'
        }
    )

    servico = forms.ChoiceField(
        label='Serviço de interesse',
        choices= list(Contact.SERVICO_CHOICES),
        required=True
    )

    mensagem = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea,
        error_messages={
            'required': 'Por favor, escreva sua mensagem.'
        }
    )

    class Meta:
        model = Contact
        fields = ['nome', 'email', 'telefone', 'assunto', 'servico', 'mensagem']

    # 🎨 Aplicar CSS de forma centralizada (MUITO melhor)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_class = 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white placeholder-gray-500 transition-all duration-300'

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': base_class
            })

        # Placeholders específicos
        self.fields['nome'].widget.attrs.update({'placeholder': 'Seu nome completo'})
        self.fields['email'].widget.attrs.update({'placeholder': 'seu@email.com'})
        self.fields['telefone'].widget.attrs.update({'placeholder': '(73) 98168-3277'})
        self.fields['assunto'].widget.attrs.update({'placeholder': 'Ex: Orçamento para site institucional'})
        self.fields['mensagem'].widget.attrs.update({
            'placeholder': 'Conte um pouco sobre seu projeto, ideia ou necessidade...',
            'rows': 5
        })

    # ✅ Validação do nome (melhorada)
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')

        if nome:
            nome = ' '.join(nome.split())

            if len(nome.split()) < 2:
                raise ValidationError('Por favor, informe seu nome completo.')

            if not re.match(r'^[A-Za-zÀ-ÿ\s\-]+$', nome):
                raise ValidationError('O nome deve conter apenas letras.')

        return nome

    # ✅ Validação da mensagem
    def clean_mensagem(self):
        mensagem = self.cleaned_data.get('mensagem')

        if mensagem:
            mensagem = ' '.join(mensagem.split())

            if len(mensagem) < 10:
                raise ValidationError('Mensagem muito curta (mínimo 10 caracteres).')

            if len(mensagem) > 5000:
                raise ValidationError('Mensagem muito longa (máximo 5000 caracteres).')

        return mensagem

    # ✅ Validação geral
    def clean(self):
        cleaned_data = super().clean()

        assunto = cleaned_data.get('assunto')

        if assunto and len(assunto.strip()) < 5:
            self.add_error('assunto', 'Seja mais específico no assunto (mínimo 5 caracteres).')

        return cleaned_data