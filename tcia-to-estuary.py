import tcia_utils
import os
import shutil

from pestuary.collections import collection_create
from pestuary.content import content_add

def _rename(item):
    return item[2] + "_" + item[4] + "_" + item[6] + "_" + item[7] + "_" + item[9] + "_" + item[10] + "_" + item[11]

def _dataCleanup(collection):
    shutil.rmtree(collection)
    os.remove(collection + ".csv")

def dataPrep(folderName, manifestList):
    os.rename("tciaDownload", folderName)
    for item in manifestList[1:]:
        split = item.split(",")
        path = collectionName + "/" + split[1] + "/"

        for file in os.listdir(path):
            newName = _rename(split) + "_" + file
            os.rename(os.path.join(path, file), os.path.join(path, newName))

def getCollectionWithManifestList(collection):
    series = tcia_utils.getSeries(collection)
    tcia_utils.downloadSampleSeries(series, api_url = "", input_type = "", csv_filename=collection)
    return tcia_utils.manifestToList(collection + ".csv")

collectionName = "Soft-tissue-Sarcoma"
list = getCollectionWithManifestList(collectionName)
dataPrep(collectionName, list)
responses = content_add(collectionName, create_collection=True)
_dataCleanup(collectionName)
