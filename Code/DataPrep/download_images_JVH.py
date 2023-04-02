import os
import os.path
from io import BytesIO
import glob
import json
import argparse

from PIL import Image
import requests
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

# Argparse.
parser = argparse.ArgumentParser()
parser.add_argument('input_object_directory', type=str)
parser.add_argument('output_image_directory', type=str)
args = parser.parse_args()

input_object_directory = os.path.realpath(args.input_object_directory)
object_filepaths = glob.glob(os.path.join(input_object_directory, '*.json'))

output_image_directory = os.path.realpath(args.output_image_directory)

def download_image(object_filepath):
    # Load object.
    with open(object_filepath, 'r') as fp:
        entity = json.load(fp)

    object_filename = os.path.basename(object_filepath)
    image_url = entity['primary_transcode_location']
    image_filename = entity['primary_transcode']

    # Sanity checks.
    if not image_filename :
        tqdm.write(f'No primary image available. Skipping {object_filename}')
        return

    if not image_filename.endswith(('.jpg', '.jpeg', '.png')):
        tqdm.write(f'Invalid file type. Skipping {image_filename}')
        return

    # Check if file is already downloaded.
    image_filepath = os.path.join(output_image_directory, image_filename)

    if os.path.isfile(image_filepath):
        tqdm.write(f'Image already downloaded. Skipping {image_filename}')
        return

    # Download image from server.
    tqdm.write(f'Downloading {image_filename}')
    res = requests.get(image_url)

    # Handle errors.
    if res.status_code != 200:
        tqdm.write(f'Error while downloading image from server. Skipping {image_filename}')
        return

    # Handle response.
    try:
        img = Image.open(BytesIO(res.content))
    except:
        tqdm.write(f'Error while opening downloaded image. Skipping {image_filename}')
        return

    # Store image
    img.save(image_filepath)

thread_map(download_image, object_filepaths, max_workers=4)