from math import sqrt
from commonknowledge.django.images import get_aspect_ratio, render_image_grid


def get_thumbnail_opts(images):
    '''
    Generate an appropriate thumbnail image value (or None) by combining 0 or more
    source images. This can be saved to a django imagefield and then accessed by templates.
    '''

    num_images = len(images)

    # Text only, no image
    if num_images == 0:
        return None

    # If 1 or 2 images, we don't need a perfect square, so derive the aspect ratio from the constituent images
    # so that we get a bit of variation
    elif num_images <= 3:
        rows = min(2, num_images)
        dims = {
            'rows': rows,
            'cols': 1,
            'width': 400,
            'height': int(400 / calculate_aspect_ratio(images))
        }
    else:
        # Otherwise make a symmetric grid like 1x1, 2x2, 3x3, 4x4, etc.
        rows = max(2, int(sqrt(num_images) - sqrt(num_images) % 2))
        dims = {
            'rows': rows,
            'cols': rows,
            'width': 400,
            'height': 400
        }

    return {
        'format': 'JPEG',
        'imgs': images[:num_images],
        **dims
    }


def calculate_aspect_ratio(images):
    raw_aspect_ratio = sum(map(get_aspect_ratio, images)) / len(images)

    # Not too wide, not too tall...
    return min(
        max(raw_aspect_ratio, 0.5),
        1.5
    )
