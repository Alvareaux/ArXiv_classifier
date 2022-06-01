FROM python:3.9
WORKDIR /

COPY requirements.txt  ./
RUN pip install -r requirements_server.txt

COPY pipeline ./pipeline
COPY addons ./addons
COPY db ./db

COPY server_neural ./server_neural

EXPOSE 80
EXPOSE 5672

CMD ["python", "/server_neural/master.py"]

# docker build -t alvareaux/diploma_neural_classifier .
# docker push alvareaux/diploma_neural_classifier

# docker pull alvareaux/diploma_neural_classifier
# docker run --network host -it -d --name neural -v /neural/conf/:/conf/:ro -v /neural/models/:/models/:ro -v /root/:/root/:rw alvareaux/neural_classifier
# docker stop neural && docker rm neural