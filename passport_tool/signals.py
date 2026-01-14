from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CountryRule, PageMeta
from blog.models import BlogPost

@receiver(pre_save, sender=CountryRule)
def sync_pagemeta_country_rule(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CountryRule.objects.get(pk=instance.pk)
            if old_instance.slug != instance.slug:
                old_path = f"/{old_instance.slug}/"
                new_path = f"/{instance.slug}/"
                PageMeta.objects.filter(path=old_path).update(path=new_path)
        except CountryRule.DoesNotExist:
            pass

@receiver(pre_save, sender=BlogPost)
def sync_pagemeta_blog_post(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = BlogPost.objects.get(pk=instance.pk)
            if old_instance.slug != instance.slug:
                # Blog detail path from blog/urls.py seems to be /blog/<slug>/
                old_path = f"/blog/{old_instance.slug}/"
                new_path = f"/blog/{instance.slug}/"
                PageMeta.objects.filter(path=old_path).update(path=new_path)
        except BlogPost.DoesNotExist:
            pass
