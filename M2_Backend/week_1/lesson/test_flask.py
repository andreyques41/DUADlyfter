from flask import Flask
from flask import request, jsonify
import json
from flask import Response
from dataclasses import dataclass

app = Flask(__name__)


@app.route("/hello")
def hello():
    response_body = json.dumps({"msg": "Hello World!"})
    return Response(response_body, status=200, mimetype="application/json")

@dataclass
class HelloResponse:
    msg: str


@app.route("/hello3")
def hello3():
    response = HelloResponse("Hello World!")
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host="localhost", debug=True, port=8000)