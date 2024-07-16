import requests
import logging

logging.basicConfig(level=logging.DEBUG)


def read(url, component_list):
    temp_cpu_metrics_results = []
    # read from monitoring
    response = requests.get(url)
    json_data = response.json()
    for component in json_data:
        if component.get("metricName") == "cpu":
            metrics_list = component.get("metrics")
            component["metrics"] = metrics_list[0]
            temp_cpu_metrics_results.append(component)
    for component in component_list:
        if component.get("metricName") == "cpu":
            for component_cpu in temp_cpu_metrics_results:
                if component.get("xrApplicationId") == component_cpu.get("xrApplicationId"):
                    logging.info(component_cpu.get("metrics"))
                    component["metrics"] = component_cpu.get("metrics")
    logging.info(component_list)
    return component_list
