from flask import Flask, request, jsonify
from predict_with_model import predict_transaction

app = Flask(__name__)

@app.route("/mcp/transaction", methods=["POST"])
def mcp_transaction():
    data = request.json  # MCP'den gelen işlem verisi
    result = predict_transaction(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
