from math import sqrt
from commonknowledge.django.images import get_aspect_ratio, render_image_grid

MAX_IMAGE_GRID_DIMENSION = 4


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
    elif num_images <= 2:
        dims = {
            'rows': num_images,
            'cols': 1,
            'width': 400,
            'height': int(400 / calculate_aspect_ratio(images))
        }

    # If more, we want to enforce a power of 2 number of images to produce a square and not have too many
    else:
        image_dims = min(int(sqrt(num_images)),
                         MAX_IMAGE_GRID_DIMENSION)
        num_images = image_dims ** 2

        dims = {
            'rows': image_dims,
            'cols': image_dims,
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
