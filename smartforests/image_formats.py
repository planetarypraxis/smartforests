from wagtail.images.formats import Format, register_image_format

register_image_format(Format('responsive', 'Responsive',
                      'richtext-image responsive', 'original'))
