import argparse
import tcia_utils
import os
import shutil

from pestuary.content import content_add


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


def get_collection_with_manifest_list(collection):
    series = tcia_utils.getSeries(collection)
    tcia_utils.downloadSampleSeries(series, api_url="", input_type="", csv_filename=collection)


def get_collection():
    return tcia_utils.getCollections()


def upload_all_collections():
    for item in get_collection():
        collection = item['Collection']
        upload_collection(collection)


def upload_collection(collection):
    print("### Fetching Collection " + collection)
    get_collection_with_manifest_list(collection)

    print("### Preparing Collection Data")
    dataprep(collection)

    print("### Adding Content to Estuary")
    # content_add(collection, create_collection=True)

    print("### Clean up")
    cleanup(collection)


def main(options):
    if options.collection is not None:
        upload_collection(options.collection)
    else:
        upload_all_collections()
    print("### END")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCIA Data preparation for uploading to Estuary")
    parser.add_argument("--collection", dest='collection', help='Name of the collection to be uploaded.')
    args = parser.parse_args()
    main(args)
