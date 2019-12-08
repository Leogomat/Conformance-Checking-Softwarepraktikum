from pm4pydistr.slave.slave_service import SlaveSocketListener
from pm4pydistr import configuration
from flask import jsonify, request
import requests

@SlaveSocketListener.app.route("/performTraining", methods=["GET"])
def perform_training():
    keyphrase = request.args.get('keyphrase', type=str)
    if keyphrase == configuration.KEYPHRASE:

    return jsonify({})