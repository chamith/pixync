
from libxmp.utils import file_to_dict
from libxmp import consts
xmp = file_to_dict( "/home/chamith/Pictures/alwis_paule_avurudu_ulela_2019_04_20/img/dng/20190420_M50_0455.DNG.xmp" )
dc = xmp[consts.XMP_NS_DC]
print(dc[0][1])
