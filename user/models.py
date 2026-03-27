import re
import uuid
from django.db import models, transaction
from django.core import validators
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.deconstruct import deconstructible
from django.urls import reverse
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from user.validators import validate_image_file
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, UniqueConstraint, CheckConstraint
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.formats import date_format

class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError(_('The given username must be set'))
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    username = models.CharField( _('username'), max_length=15, unique=True,
        help_text=_('Required. 15 characters or fewer. Letters, numbers and @/./+/-/_ characters'),
        validators=[validators.RegexValidator(re.compile(r'^[\w.@+-]+$'), _('Enter a valid username.'), _('invalid'))])
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    photo = models.ImageField(upload_to="photos/", default="default/user_img.jpg", blank=True, null=True, validators=[validate_image_file], help_text=_('Formato de arquivo: jpg, jpeg ou png.')) 
    phone = PhoneNumberField(region="BR", unique=True, null=True, blank=True, help_text='Digite um número com DDD. Ex: +55 11 91234-5678')
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    is_client = models.BooleanField(_('client'),  default=False, help_text=_('Designates whether this user is a client.'))  
    is_staff = models.BooleanField(_('staff status'), default=False,  help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,  help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_trusty = models.BooleanField(_('trusty'), default=False, help_text=_('Designates whether this user has confirmed his account.'))
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'uuid': str(self.id), 'slug': self.slug})
    
    
    def has_name_changed(self):
        if not self.id:
            return False            
        old_user = User.objects.filter(id=self.id).first()
        if not old_user:
            return True
            
        return (old_user.first_name != self.first_name or old_user.last_name != self.last_name)

    def save(self, *args, **kwargs):
        # 🔹 Permite controlar validação
        if kwargs.pop("clean", True):
            self.full_clean()

        # 🔹 Geração de slug eficiente (sem loop no banco)
        if not self.slug or self._state.adding or self.has_name_changed():
            base_slug = slugify(self.get_full_name())
            self.slug = f"{base_slug}-{uuid.uuid4().hex}"

        # 🔹 Corrige atribuição de imagem padrão
        if not self.photo:
            self.photo = self._meta.get_field("photo").default

        super().save(*args, **kwargs)



class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    photo = models.ImageField(upload_to="services/", default="default/service_img.jpg", blank=True, null=True, validators=[validate_image_file],
        help_text=_('Formato: JPG, PNG ou WEBP.')
    )

    average_rate = models.DecimalField(
        _('Rate'),
        max_digits=3,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Serviço')
        verbose_name_plural = _('Serviços')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def update_average_rating(self):
        avg = self.ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        self.average_rate = round(avg, 2)
        self.save(update_fields=['average_rate'])


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="ratings",db_index=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="ratings", db_index=True)
    comment = models.TextField(_("Comentário"))
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created = models.DateTimeField(_("Criado"), auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(check=Q(rating__gte=0) & Q(rating__lte=5), name='valid_rate'),
            UniqueConstraint(fields=['user', 'service'], name='unique_user_service_rating')
        ]
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user} - {self.rating}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.service.update_average_rating()



class BannerGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Banner Group"
        verbose_name_plural = "Banner Groups"
        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                condition=Q(is_active=True),
                name='unique_active_banner_group'
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_active:
                BannerGroup.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
            super().save(*args, **kwargs)


class BannerImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    group = models.ForeignKey(
        BannerGroup,
        on_delete=models.CASCADE,
        related_name='images',
        db_index=True
    )

    image = models.ImageField(
        _('Imagem'),
        upload_to='banners/',
        validators=[validate_image_file]
    )

    is_primary = models.BooleanField(_('Imagem Principal'), default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'id']
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        constraints = [
            models.UniqueConstraint(
                fields=['group'],
                condition=Q(is_primary=True),
                name='unique_primary_image_per_group'
            )
        ]
        indexes = [
            models.Index(fields=['group']),
        ]

    def __str__(self):
        return f"Banner for {self.group.name}"

    def clean(self):
        # validação extra (boa prática)
        if self.is_primary:
            exists = BannerImage.objects.filter(
                group=self.group,
                is_primary=True
            ).exclude(pk=self.pk).exists()

            if exists:
                raise ValidationError("Já existe uma imagem principal para este grupo.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_primary:
                BannerImage.objects.filter(
                    group=self.group,
                    is_primary=True
                ).exclude(pk=self.pk).update(is_primary=False)

            super().save(*args, **kwargs)



class Contact(models.Model):
    SERVICO_CHOICES = [
        ('sites', 'Sites Profissionais'),
        ('ecommerce', 'E-commerce Completo'),
        ('chatbots', 'Chatbots Inteligentes'),
        ('api', 'APIs & Integrações'),
        ('ia', 'Inteligência Artificial'),
        ('sistemas', 'Sistemas Web Sob Medida'),
        ('outros', 'Outros / Não sei'),
    ]
    
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('lido', 'Lido'),
        ('respondido', 'Respondido'),
        ('arquivado', 'Arquivado'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(_('Nome'), max_length=200, blank=False, null=False)
    email = models.EmailField(_('E-mail'), max_length=200, blank=False, null=False)
    telefone = PhoneNumberField(_('Telefone'), blank=False, null=False,  region='BR', help_text='Digite um número com DDD. Ex:11 91234-5678')
    assunto = models.CharField(_('Assunto'), max_length=200, blank=False, null=False)
    servico = models.CharField('Serviço de interesse', max_length=50, choices=SERVICO_CHOICES, blank=False, null=False)
    mensagem = models.TextField(_('Mensagem'), default='', blank=False, null=False)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='novo', db_index=True)
    ip_origem = models.GenericIPAddressField(_('IP de origem'), blank=True, null=True)
    user_agent = models.TextField(_('User Agent'), blank=True, null=True)
    data_envio = models.DateTimeField(_('Data de envio'), default=timezone.now, db_index=True)
    
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['-data_envio']


    def __str__(self):
        return f"{self.nome} - {self.assunto} ({date_format(self.data_envio, 'SHORT_DATETIME_FORMAT')})"
        
    def marcar_como_lido(self):
        if self.status != 'lido':
            self.status = 'lido'
            self.save(update_fields=['status'])


class Portifolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="portfolios/", default="default/project_img.jpg", blank=True, null=True, validators=[validate_image_file], help_text=_('Formato de arquivo: jpg, jpeg ou png.'))
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Portifólio"
        verbose_name_plural = "Portifólios"

    def get_absolute_url(self):
        return reverse('portifolio_detail', args=[str(self.id), self.slug])

    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Portifolio.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)