FROM python:3.10-slim

WORKDIR /forecasting
COPY src/predhyb.h5 src/flgncru.py src/Parser.py src/swagger.json requirements.txt ./


RUN pip install -r requirements.txt

CMD ["python", "/forecasting/flgncru.py"]


