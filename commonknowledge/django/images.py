import hashlib
import base64
import json
from io import BytesIO

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage


def render_image_grid(images, rows, cols, format, filename='image-grid', width=400, height=400):
    print("render_image_grid")
    new_im = Image.new('RGB', (width, height))
    i = 0

    col_w = width / cols
    row_h = height / rows

    successful_images = []

    for row in range(rows):
        print(row)
        for col in range(cols):
            print(col)
            try:
                image = images[i]
                with image.file.open() as d_img:
                    with Image.open(d_img) as img:
                        print(image, d_img, img)
                        img = ImageOps.fit(img, (int(col_w), int(row_h)),
                                          Image.ANTIALIAS, 0, (0.5, 0.5))
                        new_im.paste(img, (int(col * col_w), int(row * row_h)))
                        successful_images += [images[i]]
            except Exception as e:
                print("Error rendering image", e)
                pass

            i += 1
    
    if successful_images == 1:
        return successful_images[0].file
    
    if successful_images == 0:
        return None

    with BytesIO() as output:
        new_im.save(output, format)

        return ImageFile(
            ContentFile(
                output.getvalue(),
                filename
            )
        )


def get_aspect_ratio(image):
    return image.width / image.height


def generate_imagegrid_filename(images, rows, cols, format, slug, prefix, width, height):
    extension = format.lower()
    hash = hashlib.sha256(
        json.dumps([[img.name for img in images], rows, cols]).encode()
    )
    digest = base64.urlsafe_b64encode(hash.digest()).decode()[:16]

    return f'{prefix}/{slug}{digest}_{width}x{height}.{extension}'
