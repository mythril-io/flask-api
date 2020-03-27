from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_praetorian import Praetorian
from flask_cors import CORS
from flask_mail import Mail
from flask_marshmallow import Marshmallow
import boto3
import os

db = SQLAlchemy()
migrate = Migrate()
guard = Praetorian()
cors = CORS()
mail = Mail()
ma = Marshmallow()

# boto3 - S3/Digital Ocean Spaces
client = boto3.client('s3',
                      region_name=os.getenv('DO_SPACES_REGION'),
                      endpoint_url='https://{}.digitaloceanspaces.com'.format(os.getenv('DO_SPACES_REGION')),
                      aws_access_key_id=os.getenv('DO_SPACES_KEY'),
                      aws_secret_access_key=os.getenv('DO_SPACES_SECRET'))

def upload_img(f_name, extension, **kwargs):
    _bucket = kwargs.get('Bucket', os.getenv('DO_SPACES_BUCKET'))
    _key = kwargs.get('Key', 'test')
    _prefix = kwargs.get('Prefix', None)
    _extension = 'image/{}'.format(extension)
    if _prefix:
        _key = _prefix + '/' + _key

    f = f_name
    client.put_object(Bucket=_bucket, Key=_key, Body=f, ACL='public-read', ContentType=_extension)

def delete_img(key, **kwargs):
    _bucket = kwargs.get('Bucket', os.getenv('DO_SPACES_BUCKET'))
    _prefix = kwargs.get('Prefix', None)
    if _prefix:
        key = _prefix + '/' + key

    return client.delete_object(Bucket=_bucket, Key=key)