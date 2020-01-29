from flask import Flask, jsonify, Response
from flask_cors import CORS, cross_origin
from db.ping import DbPing
from db.downtime import Downtime
import json
import datetime

app = Flask(__name__)

# If you want to activate CORS for all routes, uncomment the next line
# cors = CORS(app)

@app.route('/data', methods=["GET"])
@cross_origin()
def data_action():
    DbPing()
    pings = DbPing.session.query(DbPing).all()
    result = [r.as_dict() for r in pings]

    def generate():
        prepend = ""
        yield '[\n'
        for ping in DbPing.session.query(DbPing).order_by(DbPing.name):
            # ping.data["timestamp"] = ping.timestamp
            yield prepend + ping.data + '\n'
            prepend = ","
        yield ']\n'

    return Response(generate(), mimetype='text/json')

@app.route('/downtimes', methods=["GET"])
@cross_origin()
def downtime_action():
    Downtime()
    pings = Downtime.session.query(Downtime).all()
    result = [r.as_dict() for r in pings]

    def generate():
        prepend = ""
        yield '[\n'
        for downtime in Downtime.session.query(Downtime).order_by(Downtime.timestamp):
            # ping.data["timestamp"] = ping.timestamp
            dataset = {"name": downtime.name, "downtime": downtime.seconds, "date": datetime.datetime.strftime(downtime.timestamp, "%Y-%m-%d %H:%M:%S")}
            yield prepend + json.dumps(dataset) + '\n'
            prepend = ","
        yield ']\n'

    return Response(generate(), mimetype='text/json')


@app.route('/test', methods=["GET"])
@cross_origin()
def test_action():
    import random
    return "Random choice status", random.choice([200, 400, 500])


@app.route('/toggle_mailsend', methods=["GET"])
@cross_origin()
def toggle_mailsend_action():
    import os
    if os.environ['SEND_MAIL'] == "1":
        os.environ['SEND_MAIL'] = "0"
    else:
        os.environ['SEND_MAIL'] = "1"

    return f"Mail-Sendout for status-changes is now {'ON' if os.environ['SEND_MAIL'] == '1' else 'OFF'}"


@app.route('/healthz', methods=["GET"])
def health_action():
    return jsonify({"message": "OK"}), 200


@app.route('/metrics', methods=["GET"])
def metrics_action():
    return jsonify("NYI"), 200
