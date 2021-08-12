from io import BytesIO

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


def render_image_grid(imgs, rows, cols, format, filename='image-grid', width=400, height=400):
    new_im = Image.new('RGB', (width, height))
    i = 0

    col_w = width / cols
    row_h = height / rows

    for row in range(rows):
        for col in range(cols):
            with Image.open(imgs[i].file.file.open()) as img:
                img = ImageOps.fit(img, (int(col_w), int(row_h)),
                                   Image.ANTIALIAS, 0, (0.5, 0.5))
                new_im.paste(img, (int(col * col_w), int(row * row_h)))

            i += 1

    with BytesIO() as output:
        new_im.save(output, format)

        return ImageFile(
            ContentFile(
                output.getvalue(),
                filename
            )
        )


def get_aspect_ratio(image):
    return image.file.width / image.file.height