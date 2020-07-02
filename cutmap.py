import os

import numpy
import csv
import math
from PIL import Image, ImageDraw

import getmap


def cut(tif_file, to, polygon):
    # find the bounder of polygon
    max_x = polygon[0][0]
    min_x = polygon[0][0]
    max_y = polygon[0][1]
    min_y = polygon[0][1]
    for poly in polygon:
        max_x = max(max_x, poly[0])
        max_y = max(max_y, poly[1])
        min_x = min(min_x, poly[0])
        min_y = min(min_y, poly[1])
    min_x = math.floor(min_x)
    min_y = math.floor(min_y)
    max_x = math.ceil(max_x)
    max_y = math.ceil(max_y)
    print("\n")
    print(min_x, max_x, min_y, max_y)

    # read image as RGB and add alpha (transparency)
    im = Image.open(tif_file).convert("RGB")

    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)

    # create mask
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape, dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:, :, :3] = imArray[:, :, :3]

    # # transparency (4th column)
    # newImArray[:, :, 3] = mask * 255

    # Clear the color
    newImArray[:, :, 0] *= mask
    newImArray[:, :, 1] *= mask
    newImArray[:, :, 2] *= mask
    newImArray = newImArray[min_y:max_y, min_x:max_x]

    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGB")
    newIm.save(to)


def trans_to_pix(file, pos):
    # get the info of tif
    f = open(file)
    line = f.readline()
    para = []
    while line:
        para.append(float(line))
        line = f.readline()
    f.close()
    A = para[0]
    D = para[1]
    B = para[2]
    E = para[3]
    C = para[4]
    F = para[5]

    # transform the pos to pix
    ploy = []
    for i in range(0, len(pos), 2):
        x = pos[i+1]
        y = pos[i]
        pix_x = B * (y - F) - E * (x - C)
        pix_x /= D * B - A * E
        pix_y = A * (y - F) - D * (x - C)
        pix_y /= A * E - D * B
        ploy.append((pix_x, pix_y))
    return ploy


def get_image(pos, tif_file, twf_file):
    # find the bounder of polygon
    max_x = pos[1]
    min_x = pos[1]
    max_y = pos[0]
    min_y = pos[0]
    for i in range(0, len(pos), 2):
        x = pos[i+1]
        y = pos[i]
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
    x = getmap.getpic(min_y, min_x, max_y, max_x,
                      17, source='google', style='s', outfile=tif_file)
    getmap.my_file_out(x, twf_file, "keep")


def cut_aoi(aoi_file, output, tfw_file, tif_file):
    # create a dir
    if not os.path.exists(output):
        os.makedirs(output)

    # 读取csv至字典
    csvFile = open(aoi_file, "r")
    reader = csv.reader(csvFile)

    # 建立空字典
    for item in reader:
        id = item[0]
        pos_polygon = [float(x) for x in item[3:]]
        get_image(pos_polygon, tif_file, tfw_file)
        polygon = trans_to_pix(tfw_file,
                               pos_polygon)
        cut(tif_file, output + "/" + id + ".tif",
            polygon)
    os.remove(tif_file)
    os.remove(tfw_file)

    csvFile.close()


if __name__ == '__main__':
    cut_aoi("whu_aoi.csv", "whu", "google_17m_whuxx.tfw", "google_17m_whuxx.tif")
