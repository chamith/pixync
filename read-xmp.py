import xml.etree.ElementTree as ET

file_path = "/home/chamith/Pictures/home_2021/img/raw/7D2C1531.CR2.xmp"
ns_rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
ns_xmp = "http://ns.adobe.com/xap/1.0/"
tree = ET.parse(file_path)
root = tree.getroot()
desc_with_rating = root.find("./{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description/[@{http://ns.adobe.com/xap/1.0/}Rating]")
rating = desc_with_rating.get('{http://ns.adobe.com/xap/1.0/}Rating')
print("Rating:", rating)
