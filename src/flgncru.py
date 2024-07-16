from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import pickle as p
import json
import keras
import Parser
import os
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
model = keras.models.load_model("predhyb.h5")
url = os.getenv("MONITORING_IP", "http://0.0.0.0:5000/data")
component_list = []

SWAGGER_URL = "/swagger"
API_URL = "http://0.0.0.0/forecasting/doc"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


def timestamp_format(component_results, length):
    timestamps = []
    metrics_results = component_results.get("metrics")
    if int(length) < len(metrics_results):
        items_to_be_removed = len(metrics_results) - int(length)
        for i in range(items_to_be_removed):
            metrics_results.pop()
    for metric in metrics_results:
        timestamps.append(metric.get("timestamp"))
    size_timestamps = len(timestamps)
    last_timestamp = timestamps[size_timestamps - 1]
    last_timestamp_1 = timestamps[size_timestamps - 2]
    unix_timestamp_last = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S").timestamp()
    unix_timestamp_last_1 = datetime.strptime(last_timestamp_1, "%Y-%m-%d %H:%M:%S").timestamp()
    difference = unix_timestamp_last - unix_timestamp_last_1
    first_new_timestamp = unix_timestamp_last + difference
    timestamps.clear()
    for i in range(size_timestamps):
        if i == 0:
            timestamps.append(first_new_timestamp)
        else:
            timestamps.append(timestamps[i - 1] + difference)
    i = 0
    for metric in metrics_results:
        date_time = datetime.fromtimestamp(timestamps[i])
        formatted_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
        metric['timestamp'] = formatted_date
        i = i + 1
    reversed_list = []
    for item in metrics_results:
        reversed_list.insert(0, item)
    component_results["metrics"] = reversed_list


@app.route('/forecasting/doc', methods=['GET'])
def doc():
    with open('swagger.json') as f:
        # Load the JSON data
        data = json.load(f)
    return data


@app.route('/forecasting/metrics/', methods=['POST', 'GET', ])
def makecalc():
    if request.method == 'POST':
        data = request.get_json()
        for item in data:
            id = item.get("xrApplicationId")
            # Check if the component with the same ID already exists in component_list
            existing_index = next(
                (index for index, x in enumerate(component_list) if x.get("xrApplicationId") == id), None)
            if existing_index is not None:
                # Update existing component in component_list
                component_list[existing_index].update(item)
            else:
                # Add new component to component_list
                component_list.append(item)
        return "components received"
    if request.method == 'GET':
        length = request.args.get('length')
        metric_results = Parser.read(url, component_list)
        logging.info(metric_results)
        component_results = []
        for component in metric_results:
            input_model = []
            metrics = component.get("metrics")
            logging.info(metrics)
            if metrics:
                for entry in metrics:
                    if entry.get("value") == 'NULL':
                        input_model.append(float('4'))
                    if entry.get("value") != 'NULL':
                        if float(entry.get("value")) >= 4:
                            input_model.append(float(entry.get("value")))
                        if float(entry.get("value")) < 4:
                            input_model.append(float('4'))
                logging.info(input_model)
                input_model = np.array(input_model)
                input_model = input_model.reshape((1, 6, 1))
                predictions = model.predict(input_model)
                logging.info(predictions)
                # prediction = np.array2string(predictions[0][0])
                # Create a NumPy array
                arr = np.array(predictions)
                # Convert the values to strings
                predictions_string = arr.astype(str)
                # remove [[[]]]
                predictions_to_list = predictions_string.tolist()
                predictions_to_list_proper_format = []
                for sublist in predictions_to_list:
                    for subsublist in sublist:
                        for value in subsublist:
                            predictions_to_list_proper_format.append(value)
                for i in range(len(predictions_to_list_proper_format)):
                    entry = predictions_to_list_proper_format[i]
                    json_item = metrics[i]
                    json_item["value"] = entry
                component_results.append(component)
                timestamp_format(component, length)
        return jsonify(component_results)


@app.route('/forecasting/metrics/<xrApplicationId>', methods=['GET', 'DELETE'])
def set2(xrApplicationId):
    if request.method == "DELETE":
        for component in component_list:
            if component.get("xrApplicationId") == xrApplicationId:
                component_list.remove(component)
        message = xrApplicationId + " deleted"
        return message
    if request.method == "GET":
        length = request.args.get('length')
        metric_results = Parser.read(url, component_list)
        logging.info(metric_results)
        component_results = []
        input_model = []
        for component in metric_results:
            if component.get("xrApplicationId") == xrApplicationId:
                metrics = component.get("metrics")
                if metrics:
                    for entry in metrics:
                        if entry.get("value") == 'NULL':
                            input_model.append(float('4'))
                        if entry.get("value") != 'NULL':
                            if float(entry.get("value")) >= 4:
                                input_model.append(float(entry.get("value")))
                            if float(entry.get("value")) < 4:
                                input_model.append(float('4'))

                logging.info(input_model)
                input_model = np.array(input_model)
                input_model = input_model.reshape((1, 6, 1))
                predictions = model.predict(input_model)
                logging.info(predictions)
                # prediction = np.array2string(predictions[0][0])
                # Create a NumPy array
                arr = np.array(predictions)
                # Convert the values to strings
                predictions_string = arr.astype(str)
                # remove [[[]]]
                predictions_to_list = predictions_string.tolist()
                predictions_to_list_proper_format = []
                for sublist in predictions_to_list:
                    for subsublist in sublist:
                        for value in subsublist:
                            predictions_to_list_proper_format.append(value)
                for i in range(len(predictions_to_list_proper_format)):
                    entry = predictions_to_list_proper_format[i]
                    json_item = metrics[i]
                    json_item["value"] = entry
                component_results.append(component)
                for component in component_results:
                    timestamp_format(component, length)
        return jsonify(component_results)


if __name__ == '__main__':
    # modelfile = 'gcnru_pkl'
    # model = p.load(open(modelfile, 'rb'))
    app.run(host='0.0.0.0', port=4003)
