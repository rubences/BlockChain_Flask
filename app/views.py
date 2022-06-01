import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

# El nodo con el que interactúa nuestra aplicación, puede haber múltiples nodos también.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetch_posts():
    """
    Función para obtener la cadena de un nodo de cadena de bloques, analizar los
    datos y almacenarlos localmente.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'], reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html', title='Transacción descentralizada',
                            subtitle=':  ¿A quién quieres ingresarle el dinero?',
                            posts=posts,
                            node_address=CONNECTED_NODE_ADDRESS,
                            readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Punto final para crear una nueva transacción a través de nuestra aplicación.
    """
    dinero = request.form["dinero"]
    asunto= request.form["asunto"]
    if asunto !="":
        asunto=" Por: "+ asunto
    recibidor=request.form["recibidor"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': dinero +"€ a "+ recibidor,
        'subcontent' :asunto,
    }

    # Enviar la transacción a nuestro nodo de cadena de bloques.
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                    json=post_object,
                    headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
