import os, sys, gc
import time
import json

import eventlet
import overpy
from pprint import *

nodes_list = {}


# ["aerialway", "aeroway", "amenity", "barrier",
#             "boundary", "building", "craft", "emergency",
#             "geological", "highway", "historic", "landuse",
#             "leisure", "man_made", "military", "natural",
#             "office", "place", "power", "public_transport",
#             "railway", "route", "shop", "sport",
#             "telecom", "tourism", "waterway"]

def osm_request(name, key_list):
    query = "[out:json];\n"
    query += "area[\"name\"=\"{0}\"]->.searchArea;\n".format(name)
    for key in key_list.keys():
        query += "(\n"
        temp = "\"{0}\"".format(key)
        if len(key_list[key]) == 1:
            temp += "=\"{0}\"".format(key_list[key][0])
        else:
            temp += "~\"{0}".format(key_list[key][0])
            for v in range(1, len(key_list[key])):
                temp += "|{0}".format(key_list[key][v])
            temp += "\""
        query += "way[{0}](area.searchArea);\n".format(temp)
        query += "node(w);\n"
        query += ");\n"
    query += "out;\n"
    print(query)
    print("start request")
    osm_op_api = overpy.Overpass()
    result = osm_op_api.query(query)
    # flag = True
    # while flag:
    #     try:
    #         # eventlet.monkey_patch()  # 必须加这条代码
    #         try:
    #             query = ("[out:json];\n"
    #                      "area[\"name\"=\"Helsinki\"]->.searchArea;\n"
    #                      "(\n"
    #                      "way[\"landuse\"=\"residential\"](area.searchArea);\n"
    #                      "node(w);\n"
    #                      ");\n"
    #                      "out;\n")
    #             print("start request" + path, lat1, lon1, lat2, lon2)
    #             osm_op_api = overpy.Overpass()
    #             result = osm_op_api.query(query)
    #         except (ConnectionResetError, eventlet.timeout.Timeout) as e:
    #             print(e)
    #             result = overpy.Result()
    #             if lat2 - lat1 > 1e-7 and lon2 - lon1 > 1e-7:
    #                 dim = 3
    #                 for i in range(dim):
    #                     for j in range(dim):
    #                         temp = osm_request(lat1 + (lat2 - lat1) / dim * i,
    #                                            lon1 + (lon2 - lon1) / dim * i,
    #                                            lat1 + (lat2 - lat1) / dim * (i + 1),
    #                                            lon1 + (lon2 - lon1) / dim * (i + 1),
    #                                            path + "-" + str(i * dim + j + 1))
    #                         result.expand(temp)
    #         flag = False
    #     except (Exception, overpy.exception.OverpassTooManyRequests) as e:
    #         print(e)
    #         time.sleep(120)
    # print("finish request" + path)
    return result


def get_osm(name, key_list):
    result = osm_request(name, key_list)

    print("Nodes: ", len(result.nodes))
    print("Ways: ", len(result.ways))
    print("Relations: ", len(result.relations))
    return result


def node2csv(node, key_list):
    line = ""
    for k in node.tags.keys():
        if k in key_list.keys() and node.tags[k] in key_list[k]:
            line += "%s, %s,%s" % (node.id, k, node.tags[k])
            break
    line += ",%s,%s" % (node.lat, node.lon)
    return line


def way2csv(way, key_list):
    line = ""
    for k in way.tags.keys():
        if k in key_list.keys() and way.tags[k] in key_list[k]:
            line += "%s, %s,%s" % (way.id, k, way.tags[k])
            break
    flag = True
    for id in way._node_ids:
        if id not in nodes_list:
            flag = False
    if flag:
        for id in way._node_ids:
            if id in nodes_list:
                line += ",%s,%s" % (nodes_list[id][0], nodes_list[id][1])
    # else:
    #     nodes = way.get_nodes(resolve_missing=True)
    #     for node in nodes:
    #         line += ",%s,%s" % (node.lat, node.lon)
    return line


def get_poi_aoi(name, key_list):
    result = get_osm(name, key_list)

    # POI获取
    nodeset = result.nodes
    fnode = open("%s_poi.csv" % name, "w+")
    for node in nodeset:
        # 记录结点
        nodes_list[node.id] = [node.lat, node.lon]
        flag = False
        # 判断是否有POI信息
        for k in node.tags.keys():
            if k in key_list.keys() and node.tags[k] in key_list[k]:
                flag = True
                break
        if flag:
            fnode.write(node2csv(node, key_list) + "\n")
    fnode.close()

    # AOI获取
    wayset = result.ways
    fway = open("%s_aoi.csv" % name, "w+")
    for way in wayset:
        flag = False
        # 保证有aoi信息
        for k in way.tags.keys():
            if k in key_list.keys() and way.tags[k] in key_list[k]:
                way_node_list = way._node_ids
                # 保证环形
                if way_node_list[0] == way_node_list[-1]:
                    flag = True
                    # 保证改区域在限制范围内
                    for id in way_node_list:
                        if id not in nodes_list:
                            flag = False
                break
        if flag:
            # print(way)
            # print(way.tags)
            # print("\n")
            fway.write(way2csv(way, key_list) + "\n")
    fway.close()


if __name__ == "__main__":
    # 0.55304,114.32995,30.55920,114.34268
    # 30.5337,114.2831,30.5830,114.3849
    # 30.5538,114.1742,30.6523,114.3778 1km 可行
    # 30.4614,114.1665,30.6586,114.5737 3km 数据太多失败
    # 30.563,114.144,30.637,114.28 硚口区
    # 30.497,114.259,30.63,114.426 武昌区 太大失败，改进后成功
    # 30.3562,113.9399,30.7217,114.7543 武汉大概的主市区
    # 30.3778,114.164738,30.700624,114.654907 洪山区
    # 30.5332,114.2899,30.5446,114.3153 测试
    # 30.525773,114.347530,30.536521,114.360538 武大
    # name = "whu"
    # lat1, lon1, lat2, lon2 = 30.525773,114.347530,30.536521,114.360538
    # get_poi_aoi(name, lat1, lon1, lat2, lon2)
    pass
