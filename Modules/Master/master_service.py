from pm4pydistr.master.master_service import MasterSocketListener
from pm4pydistr import configuration
from flask import jsonify, request
import requests


@MasterSocketListener.app.route("/performTraining", methods=["GET"])
def perform_training():
    keyphrase = request.args.get('keyphrase', type=str)
    if keyphrase == configuration.KEYPHRASE:
        print("aaaaaa")
    return jsonify({})