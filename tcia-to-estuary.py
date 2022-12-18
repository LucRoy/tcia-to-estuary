import argparse
import tcia_utils
import os
import shutil
import time

from pestuary.collections import collection_create
from estuary_client import MainCreateCollectionBody

from pestuary import Pestuary

pestuary = Pestuary()
collectionsApi = pestuary.get_collections_api()
contentApi = pestuary.get_content_api()


def rename(arr):
    # Position : Field
    # 1: Series UID
    # 2: Collection
    # 3: 3rd Party Analysis
    # 4: Data Description URI
    # 5: Subject ID
    # 6: Study UID
    # 7: Study Description
    # 8: Study Date
    # 9: Series Description
    # 10: Manufacturer
    # 11: Modality
    # 12: SOP Class UID
    # 13: Number of Images
    # 14: File Size
    # 15: File Location
    # 16: Series Number
    # 17: License Name
    # 18: License URL
    # 19: Annotation Size
    return arr[2] + "_" + arr[5] + "_" + arr[8] + "_" + arr[9] + "_" + arr[11] + "_" + arr[1]


def cleanup(col):
    shutil.rmtree(col)
    os.remove(col + ".csv")


def dataprep(collection):
    os.rename("tciaDownload", collection)
    with open(collection + ".csv") as f:
        next(f)
        for line in f:
            split = line.split(",")
            path = collection + "/" + split[1] + "/"

            for file in os.listdir(path):
                name = rename(split) + "_" + file
                os.rename(os.path.join(path, file), os.path.join(path, name))


def download_collection(col):
    series = tcia_utils.getSeries(col)
    tcia_utils.downloadSampleSeries(series, api_url="", input_type="", csv_filename=col)


def get_collection():
    return tcia_utils.getCollections()


def upload_all_collections():
    for item in get_collection():
        collection = item['Collection']
        upload_collection(collection)


def collection_create(name, description=''):
    body = MainCreateCollectionBody(name=name, description=description)
    return collectionsApi.collections_post(body)


def _add_file(path, collection_uuid='', root_collection_path=''):
    # get only relevant parts of path for directory inside collection and filename
    # /tmp/mydir/subdir/current-file -> [collection_path: /subdir/, filename: current-file]
    collection_path = ''
    if collection_uuid:
        if not root_collection_path:
            print(f"empty root collection path")
            return
        collection_path = '/' + os.path.relpath(path, start=root_collection_path)
    print("Calling api", path, collection_uuid)
    return contentApi.content_add_post(path, coluuid=collection_uuid, dir=collection_path)


def _add_dir(path, collection_uuid='', root_collection_path=''):
    responses = []
    if len(os.listdir(path)) == 0:
        print(f"empty directory '{path}'")
        return responses

    for entry in os.listdir(path):
        fullpath = os.path.join(path, entry)
        if os.path.isfile(fullpath):
            responses.append(_add_file(fullpath, collection_uuid, root_collection_path))
        else:
            responses += _add_dir(fullpath, collection_uuid, root_collection_path)

    return responses


def content_add(col, collection_uuid):
    tries = 20
    for i in range(tries):
        try:
            _add_dir(col, collection_uuid=collection_uuid, root_collection_path=col)
        except Exception as e:
            if i < tries - 1: # i is zero indexed
                time.sleep(5)
                continue
            else:
                raise
        break


def upload_collection(col):
    print("### Fetching Collection " + col)
    series = tcia_utils.getSeries(col)

    collection_name = os.path.basename(os.path.normpath(col))
    collection = collection_create(collection_name)
    collection_uuid = collection.uuid

    print("collection_uuid", collection_uuid)
    for item in series:
        tcia_utils.downloadSeries([item], api_url="", input_type="", csv_filename=col)
        dataprep(col)
        content_add(col, collection_uuid)
        cleanup(col)


def main(options):
    if options.collection is not None:
        print("### Uploading collection " + options.collection)
        upload_collection(options.collection)
    else:
        print("### Uploading all collection")
        upload_all_collections()
    print("### END")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCIA Data preparation for uploading to Estuary")
    parser.add_argument("--collection", dest='collection', help='Name of the collection to be uploaded.')
    args = parser.parse_args()
    main(args)