import cx_Oracle
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from flask import Flask,abort
from flask import request, jsonify

from find_overlapping_plots import find_overlapping_plots

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


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
        if get_polygon(row).contains(point):
            break

    if get_polygon(row).contains(point):
        return jsonify({"status": 1, "data": {"vill_code": row[0], "plot_id": row[1]}}), 200
    else:
        return jsonify({"status": 0, "data": {}})


@app.route("/findOverlappingPlots", methods=['POST', 'GET'])
def find_overlapping_plots_route():
        return find_overlapping_plots(request)


def get_where_clause(json_request):
        return "where sea='%s' AND gps_acVill=%d" % (json_request.json['sea'], int(json_request.json['vill_code']))


def get_polygon(row):
    return Polygon([(row[2], row[3]), (row[4], row[5]), (row[6], row[7]), (row[8], row[9])]).buffer(0)


@app.errorhandler(400)
def param_not_found(error):
    return jsonify({"status": 0, "error": {"message": error.description}})


if __name__ == "__main__":
    app.run()





