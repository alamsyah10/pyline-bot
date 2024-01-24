import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('zo4LgOR9tL8K0cpYcp1nuvypmo1keq06lhSyIlwcRoNyVR+/2PJ56XOub8CGk5woB+glJIkVql/i5q0bzHgF22+YO0q2L+bTdDXDCJu7/L5gnXmfOTWn6a4oH6SmCQbQTEu7MqB2Iacc+RbrY8v5uwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('230d32d01ad7ede981c9e0f462695941')


@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """ Here's all the messages will be handled and processed by the program """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text + " apa kabar"))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
