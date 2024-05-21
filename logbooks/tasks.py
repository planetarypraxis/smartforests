from django.core.management import call_command
from wagtail.models import Page
from background_task import background
import requests, os, time

from smartforests.models import Tag
from smartforests.tag_cloud import recalculate_taglinks

@background(schedule=15, remove_existing_tasks=True)
def regenerate_page_thumbnails(page_id: int):
    from logbooks.models.mixins import ThumbnailMixin

    try:
        page = Page.objects.get(pk=page_id).specific
    except Page.DoesNotExist:
        return
    if isinstance(page, ThumbnailMixin):
        page.regenerate_thumbnail()
        page.save(regenerate_thumbnails=False)


@background(schedule=15, remove_existing_tasks=True)
def regenerate_tag_thumbnails(tag_id: int):
    try:
        tag = Tag.objects.get(pk=tag_id)
    except Tag.DoesNotExist:
        return

    tag.regenerate_thumbnail(force=True)
    tag.save()


@background(schedule=15, remove_existing_tasks=True)
def regenerate_tag_cloud(tag_id: int):
    recalculate_taglinks(tag_id=tag_id)


@background(schedule=15, remove_existing_tasks=True)
def publish():
    print(f"Publishing scheduled pages")
    call_command('publish_scheduled_pages')

@background(schedule=5, remove_existing_tasks=True)
def populate_site_cache():
    base_url = os.environ.get('BASE_URL') or 'http://localhost:8000'
    languages = ['en','pt','es','fr','id','hi']
    index_pages = ['logbooks', 'stories', 'map', 'radio', 'radio-archive', 'contributors']
    urls = []
    for language in languages:
        urls.append(f"{base_url}/{language}")
    for language in languages:
        for index_page in index_pages:
            if index_page == 'logbooks':
                if language == 'pt':
                    index_page = 'diarios-de-bordo'
                if language == 'es':
                    index_page = 'bitacoras'
                if language == 'fr':
                    index_page = 'journaux-de-bord'
                if language == 'id':
                    index_page = 'buku-catatan'
            if index_page == 'stories':
                if language == 'pt':
                    index_page = 'historias'
                if language == 'es':
                    index_page = 'historias'
                if language == 'fr':
                    index_page = 'histoires'
                if language == 'id':
                    index_page = 'cerita'
            if index_page == 'map':
                if language == 'pt':
                    index_page = 'mapa'
                if language == 'es':
                    index_page = 'mapa'
                if language == 'fr':
                    index_page = 'carte'
                if language == 'id':
                    index_page = 'peta'
            if index_page == 'contributors':
                if language == 'pt':
                    index_page = 'contribuidores'
                if language == 'es':
                    index_page = 'contribuidores'
                if language == 'fr':
                    index_page = 'contributeurs'
                if language == 'id':
                    index_page = 'kontributor'
            urls.append(f"{base_url}/{language}/{index_page}")
    
    for url in urls:
        response = requests.get(url) 
        time.sleep(2)
        print(url + " " + "OK" if str(response.ok) else "FAILED") 
         
    print(f"Site cache populated for {base_url}") 
