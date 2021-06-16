import xml.etree.ElementTree as ET
import os, glob

XMP_NS_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XMP_NS_XAP = "http://ns.adobe.com/xap/1.0/"

def get_rating(metadata_file):
    ext = os.path.splitext(metadata_file)[1][1:]
    if ext in ('xmp', 'XMP'):
        return get_rating_xmp(metadata_file)
    elif ext in ('pp3', 'PP3'):
        return get_rating_pp3(metadata_file)
    return 0

def get_rating_xmp(xmp_file):
    desc_with_rating = ET.parse(xmp_file).getroot().find("./{"+XMP_NS_RDF+"}RDF/{"+XMP_NS_RDF+"}Description/[@{"+XMP_NS_XAP+"}Rating]")
    if desc_with_rating is None:
        return 0
    return int(desc_with_rating.get("{"+XMP_NS_XAP+"}Rating"))

def get_rating_pp3(pp3_file):
    with open(pp3_file,'r') as file:
        for line in file:
            if line.startswith("InTrash") and line.rstrip('\n').split('=')[1] == 'true':
                return -1

        file.seek(0)
        for line in file:
            if line.startswith("Rank"):
                return int(line.rstrip('\n').split('=')[1])

    return 0

def is_deleted_pp3(pp3_file):
    file = open(pp3_file,'r')
    for line in file:
        if line.startswith("InTrash"):
            return line.rstrip('\n').split('=')[1] == 'true'

    return False

def get_related_files(metadata_file, local_repo_path):
    files = []
    filename = os.path.splitext(metadata_file)[0]
    for file_to_upload in glob.iglob(filename + '*'):
        rel_path = os.path.relpath(file_to_upload, local_repo_path)
        files.append(rel_path)
    return files