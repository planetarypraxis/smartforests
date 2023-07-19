from wagtail.core.models import Page
from wagtail.core.rich_text import get_text_for_indexing
from wagtailseo.models import SeoMixin


class SeoMetadataMixin(SeoMixin, Page):

    class Meta:
        abstract = True

    promote_panels = SeoMixin.seo_panels

    seo_image_sources = [
        "og_image",  # Explicit sharing image
        "default_seo_image"
    ]

    seo_description_sources = [
        "search_description",  # Explicit sharing description
    ]

    @property
    def default_seo_image(self):
        from smartforests.wagtail_settings import SocialMediaSettings
        settings = SocialMediaSettings.for_site(site=self.get_site())
        return settings.default_seo_image

    @property
    def seo_description(self) -> str:
        """
        Middleware for seo_description_sources
        """
        for attr in self.seo_description_sources:
            if hasattr(self, attr):
                text = getattr(self, attr)
                if text:
                    # Strip HTML if there is any
                    return get_text_for_indexing(text)
        return ""
