import cx_Oracle
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from flask import Flask,abort
from flask import request, jsonify

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
min_overlap=20

@app.route("/findPlotWithCoordinates", methods=['POST', 'GET'])
def find_plot_with_coordinates():
    if request.method == 'GET' and request.args:
        json_request = jsonify(request.args)
    elif request.method == 'POST' and request.json:
        json_request = jsonify(request.json)
    else:
        abort(400)
    connection = cx_Oracle.connect("mjolap", "mjolap", "45.116.107.29/ORCL")
    cursor = connection.cursor()
    query = "SELECT * FROM plot_gps %s" % get_where_clause(json_request)
    cursor.execute(query)
    #{"lat":26.882203,"long":84.596085,"vill_code":305,"sea":"2016-17"}
    result = cursor.fetchall()
    return jsonify(result)
    point = Point(float(json_request.json['lat']), float(json_request.json['long']))

    for row in result:
        if Polygon([(row[2], row[3]), (row[4], row[5]), (row[6], row[7]),
                    (row[8], row[9])]).contains(point):
            break

    if Polygon([(row[2], row[3]), (row[4], row[5]), (row[6], row[7]), (row[8], row[9])]).contains(point):
        return jsonify({"status": 1, "data": {"vill_code": row[0], "plot_id": row[1]}}), 200
    else:
        return jsonify({"status": 0, "data": {}})


@app.route("/findOverlappingPlots", methods=['POST', 'GET'])
def find_overlapping_plots():
    if request.method == 'GET' and request.args:
        json_request = jsonify(request.args)
    elif request.method == 'POST' and request.json:
        json_request = jsonify(request.json)
    else:
        abort(400)
    connection = cx_Oracle.connect("mjolap", "mjolap", "45.116.107.29/ORCL")
    cursor = connection.cursor()
    query = "SELECT * FROM plot_gps %s" % get_where_clause(json_request)
    cursor.execute(query)
    # {"lat":26.882203,"long":84.596085,"vill_code":305,"sea":"2016-17"}
    result = cursor.fetchall()
    overlap_plots = []
    for row1 in result:
        for row2 in result:
            if row1[1] != row2[1] and get_polygon(row1).intersects(get_polygon(row2))\
                   and (get_polygon(row1).intersection(get_polygon(row2)).area/get_polygon(row1).area)*100 > min_overlap:

                overlap_plots.append({"plot1_id": row1[1], "plot2_id": row2[1]
                                         , "plot1_lat1": row1[2], "plot1_lon1": row1[3], "plot1_lat2": row1[4]
                                         , "plot1_lon2": row1[5], "plot1_lat3": row1[6], "plot1_lon3": row1[7]
                                         , "plot1_lat4": row1[8], "plot1_lon4": row1[9], "plot2_lat1": row2[2]
                                         , "plot2_lon1": row2[3], "plot2_lat2": row2[4], "plot2_lon2": row2[5]
                                         , "plot2_lat3": row2[6], "plot2_lon3": row2[7], "plot2_lat4": row2[8]
                                         , "plot2_lon4": row2[9]
                                         , "area": (get_polygon(row1).intersection(get_polygon(row2)).area/get_polygon(row1).area)*100})

    return jsonify(overlap_plots)


def get_where_clause(json_request):
        #if 'sea' in json_request.json and json_request.json['sea'] is not None:
        return "where sea='%s' AND gps_acVill=%d" % (json_request.json['sea'], int(json_request.json['vill_code']))


def get_polygon(row):
    return Polygon([(row[2], row[3]), (row[4], row[5]), (row[6], row[7]), (row[8], row[9])]).buffer(0)

if __name__ == "__main__":
    app.run()





