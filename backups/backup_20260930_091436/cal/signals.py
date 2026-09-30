from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Categoria

@receiver(post_save, sender=User)
def create_user_categories(sender, instance, created, **kwargs):
    if created:
        # Busca todas as categorias globais
        global_categories = Categoria.objects.filter(is_global=True, is_active=True)
        
        # Cria uma cópia de cada categoria global para o novo usuário
        user_categories = [
            Categoria(
                user=instance,
                nome=cat.nome,
                is_global=False,
                is_active=True
            ) for cat in global_categories
        ]
        
        if user_categories:
            Categoria.objects.bulk_create(user_categories)
