from math import sqrt
from commonknowledge.django.images import get_aspect_ratio, render_image_grid

MAX_IMAGE_GRID_DIMENSION = 4


def generate_thumbnail(images, fileslug):
    '''
    Generate an appropriate thumbnail image value (or None) by combining 0 or more
    source images. This can be saved to a django imagefield and then accessed by templates.
    '''
    num_images = len(images)

    # Text only, no image
    if num_images == 0:
        return None

    # Only one image, no need to do any processing
    elif num_images == 1:
        return images[0]

    # If 2 images, we don't need a perfect square, so derive the aspect ratio from the constituent images
    elif num_images == 2:
        dims = {
            'rows': 2,
            'cols': 1,
            'width': sum((get_aspect_ratio(img) for img in images)) / 2 * 400,
            'height': 400
        }

    # If 2 more, we want to enforce a power of 2 number of images to produce a square and not have too many
    else:
        image_dims = min(int(sqrt(num_images)),
                         MAX_IMAGE_GRID_DIMENSION)
        num_images = image_dims ** 2

        dims = {
            'rows': image_dims,
            'cols': image_dims
        }

    return render_image_grid(
        images[:num_images],
        filename=f'{fileslug}.jpeg',
        format='JPEG',
        **dims
    )
