import os.path
import json
import argparse
import math

import requests
from tqdm import tqdm

# Argparse.
parser = argparse.ArgumentParser()
parser.add_argument('output_object_directory', type=str)
parser.add_argument('--limit', default=10, type=int)
parser.add_argument('--skip', default=0, type=int)
parser.add_argument('--relation', default=None, type=str)
args = parser.parse_args()

output_object_directory = os.path.realpath(args.output_object_directory)
global_limit = args.limit
global_skip = args.skip
global_relation = args.relation

# Prepare query.
query = '''
    query getEntities($limit: Int, $skip: Int, $searchValue: SearchFilter!) {
        Entities(limit: $limit, skip: $skip, searchValue: $searchValue) {
            count
            limit
            results { ...fullEntity  __typename }
            __typename
        }
    }

    fragment fullEntity on Entity {
        id
        object_id
        ldesResource
        type
        objectNumber: metadata(key: [object_number]) { key value __typename }
        title: metadata(key: [title]) { key value __typename }
        description: metadata(key: [description]) { key value __typename }
        scopeNote: metadata(key: [scopeNote]) { key value __typename }
        publicationStatus: metadata(key: [publication_status]) { key value __typename }
        metadataCollection(key: [title, description, scopeNote], label: []) { ...MetadataCollectionFields __typename }
        primary_mediafile
        primary_mediafile_location
        primary_transcode
        primary_transcode_location
        mediafiles { ...fullMediafile __typename }
        relations { key type label value __typename }
        __typename
    }

    fragment MetadataCollectionFields on MetadataCollection {
        label
        nested
        data {
            value
            unMappedKey
            label
            nestedMetaData {
                ...NestedEntity
                metadataCollection(key: [title, description, object_number, scopeNote] label: []) {
                    label
                    nested
                    data {
                        value
                        unMappedKey
                        label
                        nestedMetaData { ...nestedEndEntity __typename }
                        __typename
                    }
                    __typename
                }
                __typename
            }
            __typename
        }
        __typename
    }

    fragment NestedEntity on Entity {
        id
        type
        title: metadata(key: [title]) { key value __typename }
        description: metadata(key: [description]) { key value __typename }
        objectNumber: metadata(key: [object_number]) { key value __typename }
        mediafiles {
            _id
            filename
            original_file_location
            transcode_filename
            transcode_file_location
            mimetype
            mediatype { type mime image audio video pdf __typename }
            __typename
        }
        relations { key type label value __typename }
        __typename
    }

    fragment nestedEndEntity on Entity {
        id
        type
        title: metadata(key: [title]) { key value __typename }
        description: metadata(key: [description]) { key value __typename }
        objectNumber: metadata(key: [object_number]) { key value __typename }
        metadataCollection(key: [title, description, object_number, scopeNote] label: []) {
            label
            nested
            data { value unMappedKey label __typename }
            __typename
        }
        mediafiles {
            _id
            filename
            original_file_location
            transcode_filename
            transcode_file_location
            mimetype
            mediatype { type mime image audio video pdf __typename }
            __typename
        }
        relations { key type label value __typename }
        __typename
    }

    fragment fullMediafile on MediaFile {
        _id
        filename
        original_file_location
        transcode_filename
        transcode_file_location
        thumbnail_file_location
        mimetype
        mediatype { type mime image audio video pdf __typename }
        metadata { key value __typename }
        __typename
    }
'''

searchValue = {
    'and_filter': False,
    'has_mediafile': True, # When set to False, it does only return the ones without media, not the combination of both.
    'isAsc': False,
    'key': 'title',
    'randomize': False,
    'relation_filter': [],
    'skip_relations': False,
    'value': ''
}

if global_relation is not None:
    searchValue['relation_filter'].append(global_relation)

# We can only fetch 100 entities per request, so split the download over multiple requests.
frac, whole = math.modf(global_limit/100)
limit_per_request = [100]*int(whole) + [round(frac*100)]*math.ceil(frac)
skip_per_request = [global_skip + 100*i for i in range(math.ceil(whole+frac))]

for limit, skip in tqdm(list(zip(limit_per_request, skip_per_request))):
    # Request data.
    request = requests.post('https://data.collectie.gent/api/graphql', json={'query': query, 'variables': {'limit': limit, 'skip': skip, 'searchValue': searchValue}})

    if request.status_code == 200:
        response = request.json()
    else:
        raise Exception()

    if 'errors' in response:
        raise Exception(request.content)

    entities = response.get('data', {}).get('Entities', {}).get('results', [])

    # Check if response contains expected amount of entities.
    if len(entities) != limit:
        raise Exception(f'The response does not contain the expected amount of entities: {len(entities)} != {limit}')

    # Store data.
    for entity in entities:
        # entity_id = entity['id'] # Don't use this id since there are some with "noid".
        entity_id = entity['object_id'].replace(':', '--', 1) # Filename can't contain :, so replace with double dash.
        filename = f'{entity_id}.json'
        filepath = os.path.join(output_object_directory, filename)

        if os.path.isfile(filepath):
            tqdm.write(f'File already exists. Overwriting {filename}')

        with open(filepath, 'w') as fp:
            json.dump(entity, fp)