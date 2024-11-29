import os
import boto3
from PIL import Image
from io import BytesIO

s3 = boto3.client("s3")
sns = boto3.client("sns")

bucket_1 = "input-bucket-needs-resizing"
bucket_2 = "output-bucket-resized"
sns_topic_arn = "arn:aws:sns:us-east-1:637423466308:Image-resizing-topic" 

def lamda_handler(event,context):
    if "Records" in event:
        for record in event["Records"]:
            handle_s3_record(record)
    else:
        handle_s3_record(event)

def handle_s3_record(record):
    if 's3' in record and 'bucket' in record['s3'] and 'name' in record["s3"]['bucket'] and 'object' in record['s3'] and 'key' in record['s3']['object']:
        source_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        response = s3.get_object(Bucket=source_bucket,Key=object_key)
        content_type = response['ContentType']
        image_data = response['Body'].read()

        resized_image = resize_and_compress_image(image_data)

        destination_key = f"resized/{object_key}"
        s3.put_object(Bucket=bucket_2,Key=destination_key,ContentType=content_type,Body=resized_image)

        message = f"Image {object_key} has been resized and uploaded to {bucket_2}"
        sns.publish(TopicArn=sns_topic_arn,Message=message)

    else:
        print("Error: Invalid S3 event record structure")

def resize_and_compress_image(image_data,quality=75):
    image = Image.open(BytesIO(image_data))

    image_io = BytesIO()
    image.save(image_io,format=image.format,quality=quality)

    return image_io.getvalue()
