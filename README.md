# Forecasting

## Endpoints
The forecasting service supports four kind of endpoints:

| Endpoints                                            | Method | description                                                             |
|------------------------------------------------------|--------|-------------------------------------------------------------------------|
| /forecasting/metrics                                 | POST   | add components to component list in which forecasting will be performed |
| /forecasting/metrics                                 | GET    | retrieve the forecasted values for all components                       |
| /forecasting/metrics/?xrApplicationId=component_name | DELETE | delete specified component from the component list                      |
| /forecasting/metrics/?xrApplicationId=component_name | GET    | retrieve the forecasted values for the specified component              |                                                    

## Via Terminal
To add a component:

```bash
curl -L -X POST '{FORECASTING_IP}/forecasting/metrics' \ -H 'accept: application/json' \ -H 'Content-Type: application/json' \ -d '[ { "componentName": "string", "componentType": "string", "metricName": "string", "metricUnit": "string", "thresholdRule": "gt", "thresholdValue": 0, "xrApplicationId": "string" } ]'
```

To delete a component:

```bash
curl -L -X DELETE
  '{FORECASTING_IP}/forecasting/metrics/xrApplicationId' 
  -H 'accept: application/json' 
```

To get all components:

```bash
curl -L -X GET '{FORECASTING_IP}/forecasting/metrics?length=6'
```

To get a component:
```bash
curl -X GET '{FORECASTING_IP}/forecasting/metrics/xrApplicationId?length=6'
```

## Build
Note: The build.sh forecasting version should be set to the same as the docker-compose.yaml forecasting version.
```bash
./build.sh
```
## Docker-Compose
Note: The {MONITORING_IP} should be replaced with the IP of a monitoring system. 
```bash
docker-compose up
```
