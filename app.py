import os
from flask import Flask, render_template, request, abort, jsonify, send_file
from deepface import DeepFace
import time
from PIL import Image
from io import BytesIO
import io  # Import the io module

import base64  # Import the base64 module
import numpy as np

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi('zo4LgOR9tL8K0cpYcp1nuvypmo1keq06lhSyIlwcRoNyVR+/2PJ56XOub8CGk5woB+glJIkVql/i5q0bzHgF22+YO0q2L+bTdDXDCJu7/L5gnXmfOTWn6a4oH6SmCQbQTEu7MqB2Iacc+RbrY8v5uwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('230d32d01ad7ede981c9e0f462695941')
captured_images_folder = os.path.join("static", "captured_images")
database_images_folder = os.path.join("static", "database")

database = [{
    ""
}]


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

@app.route("/send_message", methods=['POST'])
def send_message():
    try:
        # user_id = request.json.get("user_id")  # Get user ID from the request
        user_id = "U027f30522e854eb3922ab0fd6fa857d3"
        message_text = "send to alamsyahhh"  # Get message text from the request

        # Message to be sent
        message = TextSendMessage(text=message_text)

        # Send the message to the specified user
        line_bot_api.push_message(user_id, messages=message)

        return jsonify({"status": "success", "message": "Message sent successfully."})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "error": str(e)})



@app.route("/")
def dashboard():
    return render_template("dashboard.html")

import requests
import json

def basic_upload(image_data):
    url = "https://api.bytescale.com/v2/accounts/kW15btV/uploads/binary"
    headers = {
        "Authorization": "Bearer public_kW15btVG2Yc8588L6sRg4AERTU8J",
        "Content-Type": "text/plain"  # Change to match the file's MIME type
    }
    data = image_data  # To upload a file: use --data-binary @file.jpg in cURL

    response = requests.post(url, headers=headers, data=data)

# Example usage:
# params = {
#     'accountId': 'your_account_id',
#     'querystring': {'param1': 'value1', 'param2': 'value2'},
#     'requestBody': 'your_request_body',
#     'apiKey': 'your_api_key',
#     'metadata': {'meta1': 'value1', 'meta2': 'value2'}
# }
# result = basic_upload(params)
# print(result)


@app.route("/capture", methods=['POST'])
def capture_image():
    try:
        start_time = time.time()
        image_data = request.get_json().get("image_data")
        image_binary = image_data.split(",")[1].encode("utf-8")
        image_filename = f"captured_image_{int(time.time())}.jpg" 


        image_data_real = image_data.split(",")[1]
        image_binary_real = base64.b64decode(image_data_real)
        image = Image.open(BytesIO(image_binary_real))
        image.save(os.path.join(captured_images_folder, image_filename), "JPEG", quality=95)  # Save as JPEG

        img1 = Image.open("static/captured_images/"+image_filename)
        img1_np = np.array(img1)
        
        model_name = 'Facenet'

        folder_path = "static/database"
        filenames = os.listdir(folder_path)
        print(filenames)
        for filename in filenames:
            img2 = Image.open("static/database/"+filename)
            img2_np = np.array(img2)
            one_response_start_time = time.time()
            response = DeepFace.verify(img1_path=img1_np, img2_path=img2_np, model_name=model_name)
            print(f"1 face recognition time: {time.time() - one_response_start_time}")
            print(response)
            if (response['verified']) :

                print(f"face recognition time : {time.time()-start_time}")
                return jsonify({"status": "success", "image_filename": filename})
        print(f"face recognition time : {time.time()-start_time}")
        # response = DeepFace.verify(img1_path=img1_np, img2_path=img2_np, model_name = model_name)

        return jsonify({"status": "success", "image_filename": "NOT FOUND"})
        


        # return jsonify({"status": "success", "image_filename": image_filename})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "error": str(e)})



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """ Here's all the messages will be handled and processed by the program """
    print(event.source.user_id)
    print()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text + " apa kabar"))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    """ Handle image messages """
    user_id = event.source.user_id
    image_id = event.message.id

    # You can save the image or perform further processing here
    # Example: Save the image with user_id and image_id as the filename
    image_path = os.path.join(captured_images_folder, f"{user_id}_{image_id}.jpg")
    
    # Retrieve the image content from Line server
    message_content = line_bot_api.get_message_content(image_id)
    image_data = message_content.content
    print(image_data)

    with open(image_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # Respond to the user
    response_message = f"Image received and saved as {image_path}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_message))




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
