from math import sqrt
from commonknowledge.django.images import get_aspect_ratio, render_image_grid
from PIL import Image

def get_thumbnail_opts(images):
    '''
    Generate an appropriate thumbnail image value (or None) by combining 0 or more
    source images. This can be saved to a django imagefield and then accessed by templates.
    '''

    initial_num_images = len(images)
    final_num_images = len(images)

    # Discard any images that can't be opened
    for i in range(initial_num_images):
        try:
            with images[i].file.open() as d_img:
                with Image.open(d_img) as img:
                    pass
        except:
            final_num_images = final_num_images - 1

    # Text only, no image
    if final_num_images == 0:
        return None

    # If 1 or 2 images, we don't need a perfect square, so derive the aspect ratio from the constituent images
    # so that we get a bit of variation
    elif final_num_images <= 3:
        rows = min(2, final_num_images)
        try:
            aspect_ratio = calculate_aspect_ratio(images)
        except:
            aspect_ratio = 1
        dims = {
            'rows': rows,
            'cols': 1,
            'width': 400,
            'height': int(400 / aspect_ratio)
        }
    else:
        # Otherwise make a symmetric grid like 1x1, 2x2, 3x3, 4x4, etc.
        rows = max(2, int(sqrt(final_num_images) - sqrt(final_num_images) % 2))
        dims = {
            'rows': rows,
            'cols': rows,
            'width': 400,
            'height': 400
        }

    return {
        'format': 'JPEG',
        'images': images[:final_num_images],
        **dims
    }


def calculate_aspect_ratio(images):
    raw_aspect_ratio = sum(map(get_aspect_ratio, images)) / len(images)

    # Not too wide, not too tall...
    return min(
        max(raw_aspect_ratio, 0.5),
        1.5
    )
