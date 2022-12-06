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
    return arr[2] + "_" + arr[4] + "_" + arr[5] + "_" + arr[8] + "_" + arr[9] + "_" + arr[11] + "_" + arr[1]


def cleanup(col):
    shutil.rmtree(col)
    os.remove(col + ".csv")


def dataprep(folder, manifest):
    os.rename("tciaDownload", folder)
    for line in manifest[1:]:
        split = line.split(",")
        path = folder + "/" + split[1] + "/"

        for file in os.listdir(path):
            name = rename(split) + "_" + file
            os.rename(os.path.join(path, file), os.path.join(path, name))


def get_collection_with_manifest_list(collection):
    series = tcia_utils.getSeries(collection)
    tcia_utils.downloadSampleSeries(series, api_url="", input_type="", csv_filename=collection)
    return tcia_utils.manifestToList(collection + ".csv")


def get_collection():
    return tcia_utils.getCollections()


for item in get_collection():
    col_name = item['Collection']
    print("### Fetching Collection " + col_name)
    manifest_list = get_collection_with_manifest_list(col_name)

    print("### Preparing Collection Data")
    dataprep(col_name, manifest_list)

    print("### Adding Content to Estuary")
    responses = content_add(col_name, create_collection=True)

    print("### Clean up")
    cleanup(col_name)

print("### END")
