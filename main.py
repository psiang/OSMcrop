import capture
import getmap
import cutmap

if __name__ == '__main__':
    # 59.9055,24.7385,60.3133,25.2727 赫尔基辛
    # 60.1607,24.9191,60.1739,24.9700
    # 60.16446,24.93824,60.16776,24.95096
    # 60.1162,24.7522,60.3041,25.2466
    name = "Helsinki"
    tif_file = "google_17m.tif"
    tfw_file = "google_17m.tfw"
    # lat1, lon1, lat2, lon2 = 60.1162,24.7522,60.3041,25.2466
    key_list = {
        "landuse": ["residential"]
    }

    # # get tif
    # x = getmap.getpic(lat1, lon1, lat2, lon2,
    #            17, source='google', style='s', outfile=tif_file)
    # getmap.my_file_out(x, tfw_file, "keep")

    # get aoi and poi
    capture.get_poi_aoi(name, key_list)
    # cut tif
    cutmap.cut_aoi(name + "_aoi.csv", name, tfw_file, tif_file)
