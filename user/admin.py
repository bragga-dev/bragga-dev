from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter
from .models import (
    User, Service, Rating, BannerGroup, BannerImage, Contact, Portifolio
)


# ==================== FILTROS PERSONALIZADOS ====================

class StatusFilter(SimpleListFilter):
    """Filtro personalizado para status de usuário"""
    title = _('Status do Usuário')
    parameter_name = 'user_status'
    
    def lookups(self, request, model_admin):
        return (
            ('active', _('Ativos')),
            ('inactive', _('Inativos')),
            ('trusty', _('Confirmados')),
            ('untrusty', _('Não confirmados')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'trusty':
            return queryset.filter(is_trusty=True)
        if self.value() == 'untrusty':
            return queryset.filter(is_trusty=False)
        return queryset


class RatingRangeFilter(SimpleListFilter):
    """Filtro por faixa de avaliação"""
    title = _('Faixa de Avaliação')
    parameter_name = 'rating_range'
    
    def lookups(self, request, model_admin):
        return (
            ('excellent', _('Excelente (4.5 - 5.0)')),
            ('good', _('Bom (3.5 - 4.4)')),
            ('average', _('Médio (2.5 - 3.4)')),
            ('poor', _('Ruim (1.5 - 2.4)')),
            ('terrible', _('Péssimo (0 - 1.4)')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'excellent':
            return queryset.filter(rating__gte=4.5, rating__lte=5.0)
        if self.value() == 'good':
            return queryset.filter(rating__gte=3.5, rating__lte=4.4)
        if self.value() == 'average':
            return queryset.filter(rating__gte=2.5, rating__lte=3.4)
        if self.value() == 'poor':
            return queryset.filter(rating__gte=1.5, rating__lte=2.4)
        if self.value() == 'terrible':
            return queryset.filter(rating__gte=0, rating__lte=1.4)
        return queryset


# ==================== ADMIN PERSONALIZADO ====================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'get_full_name', 'phone', 
        'is_client', 'is_staff', 'is_active', 'is_trusty', 
        'date_joined', 'photo_preview'
    )
    list_filter = (
        'is_client', 'is_staff', 'is_active', 'is_trusty', 
        StatusFilter, 'date_joined'
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name', 'phone'
    )
    readonly_fields = (
        'id', 'slug', 'date_joined', 'last_login', 
        'created_at', 'updated_at', 'photo_preview_large'
    )
    list_per_page = 25
    date_hierarchy = 'date_joined'
    ordering = ['-date_joined']
    
    fieldsets = (
        (_('Informações Pessoais'), {
            'fields': (
                'username', 'email', 'first_name', 'last_name', 
                'phone', 'photo', 'photo_preview_large', 'slug'
            )
        }),
        (_('Permissões'), {
            'fields': (
                'is_client', 'is_staff', 'is_active', 
                'is_superuser', 'is_trusty', 'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Informações do Sistema'), {
            'fields': (
                'id', 'date_joined', 'last_login', 
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'mark_as_trusty']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Nome Completo')
    get_full_name.admin_order_field = 'first_name'
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return _('Sem foto')
    photo_preview.short_description = _('Foto')
    
    def photo_preview_large(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="150" height="150" style="border-radius: 8px; object-fit: cover;" />',
                obj.photo.url
            )
        return _('Sem foto')
    photo_preview_large.short_description = _('Visualização da Foto')
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _('{} usuário(s) ativado(s) com sucesso.').format(updated))
    activate_users.short_description = _("Ativar usuários selecionados")
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _('{} usuário(s) desativado(s) com sucesso.').format(updated))
    deactivate_users.short_description = _("Desativar usuários selecionados")
    
    def mark_as_trusty(self, request, queryset):
        updated = queryset.update(is_trusty=True)
        self.message_user(request, _('{} usuário(s) marcado(s) como confirmado(s).').format(updated))
    mark_as_trusty.short_description = _("Marcar como confirmado")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'average_rate', 'ratings_count', 
        'rating_stars', 'created_at', 'photo_preview'
    )
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'average_rate', 'created_at', 'updated_at', 'photo_preview_large')
    list_per_page = 20
    ordering = ['-average_rate', 'name']
    
    fieldsets = (
        (_('Informações do Serviço'), {
            'fields': (
                'name', 'description', 'photo', 
                'photo_preview_large', 'average_rate'
            )
        }),
        (_('Informações do Sistema'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ratings_count(self, obj):
        count = obj.ratings.count()
        return format_html(
            '<span style="font-weight: bold; color: #8B5CF6;">{}</span> avaliação(ões)',
            count
        )
    ratings_count.short_description = _('Total de Avaliações')
    
    def rating_stars(self, obj):
        """Exibe estrelas baseado na avaliação média"""
        rating = float(obj.average_rate)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars_html = ''
        for i in range(full_stars):
            stars_html += '★'
        if half_star:
            stars_html += '½'
        for i in range(empty_stars):
            stars_html += '☆'
            
        return format_html(
            '<span style="color: #FBBF24; font-size: 16px;">{}</span> <span style="color: #6B7280;">({})</span>',
            stars_html, rating
        )
    rating_stars.short_description = _('Avaliação')
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 4px; object-fit: cover;" />',
                obj.photo.url
            )
        return _('Sem foto')
    photo_preview.short_description = _('Foto')
    
    def photo_preview_large(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="200" height="150" style="border-radius: 8px; object-fit: cover;" />',
                obj.photo.url
            )
        return _('Sem foto')
    photo_preview_large.short_description = _('Visualização')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'service', 'rating', 'rating_stars_display', 
        'comment_preview', 'created', 'service_average'
    )
    list_filter = (RatingRangeFilter, 'created', 'service')
    search_fields = ('user__email', 'user__username', 'comment', 'service__name')
    readonly_fields = ('id', 'created')
    list_per_page = 25
    date_hierarchy = 'created'
    ordering = ['-created']
    
    fieldsets = (
        (_('Informações da Avaliação'), {
            'fields': ('user', 'service', 'rating', 'comment')
        }),
        (_('Informações do Sistema'), {
            'fields': ('id', 'created'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_stars_display(self, obj):
        """Exibe estrelas baseado na avaliação"""
        rating = float(obj.rating)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars_html = ''
        for i in range(full_stars):
            stars_html += '★'
        if half_star:
            stars_html += '½'
        for i in range(empty_stars):
            stars_html += '☆'
            
        return format_html(
            '<span style="color: #FBBF24; font-size: 16px;">{}</span>',
            stars_html
        )
    rating_stars_display.short_description = _('Avaliação')
    
    def comment_preview(self, obj):
        if len(obj.comment) > 50:
            return f"{obj.comment[:50]}..."
        return obj.comment
    comment_preview.short_description = _('Comentário')
    
    def service_average(self, obj):
        return format_html(
            '<span style="color: #8B5CF6; font-weight: bold;">{}</span>',
            obj.service.average_rate
        )
    service_average.short_description = _('Média do Serviço')


class BannerImageInline(admin.TabularInline):
    """Inline para imagens do banner"""
    model = BannerImage
    extra = 1
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="60" style="border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return _('Sem imagem')
    image_preview.short_description = _('Pré-visualização')


@admin.register(BannerGroup)
class BannerGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'banners_count', 'created_at', 'active_badge')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 20
    ordering = ['-is_active', '-created_at']
    inlines = [BannerImageInline]
    
    fieldsets = (
        (_('Informações do Grupo'), {
            'fields': ('name', 'is_active')
        }),
        (_('Informações do Sistema'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def banners_count(self, obj):
        count = obj.images.count()
        return format_html(
            '<span style="color: #10B981; font-weight: bold;">{}</span> imagem(ns)',
            count
        )
    banners_count.short_description = _('Total de Banners')
    
    def active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #10B981; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold;">✓ ATIVO</span>'
            )
        return format_html(
            '<span style="background: #6B7280; padding: 4px 8px; border-radius: 4px; color: white;">INATIVO</span>'
        )
    active_badge.short_description = _('Status')


@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'is_primary', 'image_preview', 'created_at')
    list_filter = ('is_primary', 'group', 'created_at')
    search_fields = ('group__name',)
    readonly_fields = ('id', 'created_at', 'image_preview_large')
    list_per_page = 25
    ordering = ['-is_primary', '-created_at']
    
    fieldsets = (
        (_('Informações do Banner'), {
            'fields': ('group', 'image', 'is_primary', 'image_preview_large')
        }),
        (_('Informações do Sistema'), {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return _('Sem imagem')
    image_preview.short_description = _('Pré-visualização')
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="300" height="200" style="border-radius: 8px; object-fit: cover; border: 2px solid #8B5CF6;" />',
                obj.image.url
            )
        return _('Sem imagem')
    image_preview_large.short_description = _('Visualização Ampliada')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'email', 'telefone', 'assunto', 'servico_badge', 
        'status_badge', 'data_envio', 'data_formatada'
    )
    list_filter = ('status', 'servico', 'data_envio')
    search_fields = ('nome', 'email', 'telefone', 'assunto', 'mensagem')
    readonly_fields = (
        'id', 'ip_origem', 'user_agent', 'data_envio', 
        'mensagem_formatada', 'detalhes_tecnicos'
    )
    list_per_page = 25
    date_hierarchy = 'data_envio'
    ordering = ['-data_envio']
    
    fieldsets = (
        (_('Informações do Contato'), {
            'fields': (
                'nome', 'email', 'telefone', 'assunto', 
                'servico', 'mensagem_formatada'
            )
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Informações Técnicas'), {
            'fields': ('detalhes_tecnicos', 'ip_origem', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Informações do Sistema'), {
            'fields': ('id', 'data_envio'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_lido', 'marcar_como_respondido', 'marcar_como_arquivado']
    
    def servico_badge(self, obj):
        """Exibe o serviço com badge colorido"""
        cores = {
            'sites': '#8B5CF6',
            'ecommerce': '#EC489A',
            'chatbots': '#10B981',
            'api': '#F59E0B',
            'ia': '#EF4444',
            'sistemas': '#3B82F6',
            'outros': '#6B7280',
        }
        cor = cores.get(obj.servico, '#6B7280')
        servico_nome = dict(obj.SERVICO_CHOICES).get(obj.servico, obj.servico)
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            cor, servico_nome
        )
    servico_badge.short_description = _('Serviço')
    
    def status_badge(self, obj):
        """Exibe o status com badge colorido"""
        cores = {
            'novo': '#EF4444',
            'lido': '#F59E0B',
            'respondido': '#10B981',
            'arquivado': '#6B7280',
        }
        cor = cores.get(obj.status, '#6B7280')
        status_nome = dict(obj.STATUS_CHOICES).get(obj.status, obj.status)
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            cor, status_nome
        )
    status_badge.short_description = _('Status')
    
    def data_formatada(self, obj):
        """Formata a data de forma amigável"""
        hoje = timezone.now().date()
        data_envio = obj.data_envio.date()
        
        if data_envio == hoje:
            return format_html(
                '<span style="color: #10B981; font-weight: bold;">Hoje</span> às {}',
                obj.data_envio.strftime('%H:%M')
            )
        elif data_envio == hoje - timezone.timedelta(days=1):
            return format_html(
                '<span style="color: #F59E0B;">Ontem</span> às {}',
                obj.data_envio.strftime('%H:%M')
            )
        else:
            return obj.data_envio.strftime('%d/%m/%Y %H:%M')
    data_formatada.short_description = _('Data/Hora')
    data_formatada.admin_order_field = 'data_envio'
    
    def mensagem_formatada(self, obj):
        """Exibe a mensagem formatada"""
        if obj.mensagem:
            return format_html(
                '<div style="background: #F3F4F6; padding: 12px; border-radius: 8px; border-left: 4px solid #8B5CF6; white-space: pre-wrap;">{}</div>',
                obj.mensagem.replace('\n', '<br>')
            )
        return _('Sem mensagem')
    mensagem_formatada.short_description = _('Mensagem')
    
    def detalhes_tecnicos(self, obj):
        """Exibe detalhes técnicos formatados"""
        return format_html(
            '<div style="background: #F3F4F6; padding: 10px; border-radius: 8px;">'
            '<strong>ID:</strong> {}<br>'
            '<strong>IP:</strong> {}<br>'
            '<strong>Navegador:</strong> {}'
            '</div>',
            obj.id, obj.ip_origem or 'Não informado', 
            obj.user_agent[:100] if obj.user_agent else 'Não informado'
        )
    detalhes_tecnicos.short_description = _('Informações Técnicas')
    
    def marcar_como_lido(self, request, queryset):
        updated = queryset.exclude(status='lido').update(status='lido')
        self.message_user(request, _('{} contato(s) marcado(s) como lido.').format(updated))
    marcar_como_lido.short_description = _("Marcar como lido")
    
    def marcar_como_respondido(self, request, queryset):
        updated = queryset.update(status='respondido')
        self.message_user(request, _('{} contato(s) marcado(s) como respondido.').format(updated))
    marcar_como_respondido.short_description = _("Marcar como respondido")
    
    def marcar_como_arquivado(self, request, queryset):
        updated = queryset.update(status='arquivado')
        self.message_user(request, _('{} contato(s) arquivado(s).').format(updated))
    marcar_como_arquivado.short_description = _("Arquivar selecionados")
    
    def get_queryset(self, request):
        """Otimiza as consultas"""
        return super().get_queryset(request).select_related()


@admin.register(Portifolio)
class PortifolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'photo_preview')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'image')
        }),
        ('Informações do Sistema', {
            'fields': ('id',  'created_at'),
            'classes': ('collapse',)
        }),
    )

    def photo_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.image.url
            )
        return _('Sem foto')
    photo_preview.short_description = _('Foto')
# ==================== PERSONALIZAÇÃO DO ADMIN SITE ====================

admin.site.site_header = _('Bragga Dev - Administração')
admin.site.site_title = _('Bragga Dev Admin')
admin.site.index_title = _('Painel de Controle')