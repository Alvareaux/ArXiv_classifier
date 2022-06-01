import json
import pandas as pd
import pika
from addons.config import ConfigMaster


config_path_master = '../conf/server.cfg'
config = ConfigMaster(config_path_master)

parameters = pika.URLParameters(f'amqp://{config.username}:{config.password}'
                                f'@{config.server}/?heartbeat={config.heartbeat}')
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.basic_qos(prefetch_count=1)

queue_process_queue = channel.queue_declare(
    config.n_queue_process_queue_bulk,
    durable=True
)

data = pd.read_pickle(r'../data/arxiv.pr.val.pkl')

terms = list(data.columns)

terms.remove('entry_id')
terms.remove('text')

for index, row in data.iterrows():
    print(index)
    entry_id = row['entry_id']
    text = row['text']

    labels = []
    for l in enumerate(row[terms]):
        label_name = int(l[0] + 1)
        if_label = l[1]

        if if_label:
            labels.append(label_name)

    message = {
        'entry_id': entry_id,
        'text': text,
        'original_labels': str(labels)
    }

    channel.basic_publish(exchange='', body=json.dumps(message).encode(encoding='UTF-8'),
                          routing_key=config.n_queue_process_queue_bulk)
