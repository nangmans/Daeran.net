from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static' #AWS S3 버킷 내에 static 디렉토리 생성 후, 디렉토리에 static 파일 저장

class MediaStorage(S3Boto3Storage):
    location = 'media'  #AWS S3 버킷 내에 media 디렉토리 생성 후, 디렉토리에 media 파일 저장
    file_overwrite = False 