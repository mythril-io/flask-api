# import os, sys
from extensions import db
from PIL import Image
from io import BytesIO
import base64

def get_auto_increment(table_name):
    """
    Get auto increment for specified table
    :param table_name: String
    :return: String
    """
    DB_NAME = db.session.bind.url.database
    result = db.engine.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = \"{}\" AND TABLE_NAME = \"{}\"".format(DB_NAME, table_name))
    return [dict(r) for r in result][0].get("AUTO_INCREMENT")

# Convert a Base64 String to a Pillow Image
def base64_to_pillow_img(base64_string, max_width=2560, **kwargs):
    """
    Convert a Base64 String to a Pillow Image
    :param base64_string: String
    :return: Pillow Image
    """
    # Create Pillow Image instance
    pillow_image = Image.open(BytesIO(base64.b64decode(base64_string)))

    # Resize (maintain aspect ratio)
    if pillow_image.size[0] > max_width:
        width_percent = (max_width/float(pillow_image.size[0]))
        height = int((float(pillow_image.size[1])*float(width_percent)))
        resized_pillow_image = pillow_image.resize((max_width, height), Image.ANTIALIAS)
        return resized_pillow_image

    return pillow_image

def pillow_img_to_bytes(im, file_type='jpeg'):
    """
    Convert a Pillow Image instance to BytesIO
    :param im: Pillow Image
    :return: BytesIO
    """
    out_img = BytesIO()

    try:
        im.save(out_img, format=file_type, subsampling=0, quality=90)
    except IOError:
        print("cannot convert", infile)

    out_img.seek(0)
    return out_img

def get_base64_file_size(base64_string):
    """
    Retrieve Base 64 String's file size
    :param base64_string: String
    :return: Int
    """
    byte_size = (len(base64_string) * 3) / 4 - base64_string.count('=', -2)
    return byte_size

def get_base64_file_type(base64_string):
    """
    Retrieve Base 64 String's file type
    :param base64_string: String
    :return: String
    """
    first_char = base64_string[0]

    if first_char == 'i':
        return 'png'
    if first_char == '/':
        return 'jpeg'
    if first_char == 'R':
        return 'gif'

    return None

def base64_validation(base64_string, max_file_size):
    """
    Validate Base 64 String's image type and file size
    :param base64_string: String
    :param max_file_size: String
    :return: Boolean
    """
    file_size = get_base64_file_size(base64_string)
    file_type = get_base64_file_type(base64_string)

    if file_size > max_file_size:
        return False

    if file_type != 'jpeg' and file_type != 'png':
        return False

    return True