from flask import Flask, request, jsonify,Response

import requests
import time
from flask import Flask, render_template, session

from flask_session import Session
import re

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'
Session(app)





chat_history_dict = {}


def get_chat_history(user_id):
    if user_id not in chat_history_dict:
        chat_history_dict[user_id] = [
            {"role": "user", "parts": ["This will the text from the user"]},
            {"role": "model", "parts": ["This is the model generated response"]},
        ]

    print(chat_history_dict)
    return chat_history_dict[user_id]

############# Generate message #################

def gen(message, user_id):
    """
    write your reply generation code here
    also, if there are any changes like, if you dont want user_id , you can customize in your way
    here, the user_id is taken so that it can keep the chat history of each user
    
    """
    
    return message



############## will be connecting the webhhok to the instagram, meta will send the GET request while connecting ##################3

#######call back URL == https://your-site-link/webhook #########
####### Your verify token == "ok" ##########
@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    global response_text
    global message
    message='12'
    response_text=''
    if request.method == 'GET':
        # Handle GET requests (verification)
        mode = request.args.get('hub.mode')
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')
        if mode == 'subscribe' and verify_token == 'ok':
            return challenge
        return 'Failed verification', 403
    
    elif request.method == 'POST':
        webhook_data = request.get_json()
        
        try:
            
            if 'message' in webhook_data['entry'][0]['messaging'][0]:
                message = webhook_data['entry'][0]['messaging'][0]['message']
                print("Incoming message:", message)
                if message!=response_text:
                
                    if 'is_echo' not in message or not message['is_echo']:
                        received_text = message['text']
                        ig_sid = webhook_data['entry'][0]['messaging'][0]['sender']['id']
                        
                        # Append user message to chat history
                        chat_history = get_chat_history(ig_sid)
                        chat_history.append({"role": "user", "parts": [received_text]})
                        
                        
                        response_text = gen(received_text, ig_sid)
                        print("Generated response:", response_text)
                        
                        # Append the model's response to chat history
                        chat_history.append({"role": "model", "parts": [response_text]})
                        
                        # Update the chat history in the dictionary
                        chat_history_dict[ig_sid] = chat_history
                        
                        
                        send_result = send_message(ig_sid, response_text)
                        print("Send result:", send_result)
                        
                        return jsonify({'success': True})
                    else:
                        
                        print("Received echo of our message, ignoring")
                        return jsonify({'success': True})
            
            
            return jsonify({'success': True})
        
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500


############### Sending the response ##############
def send_message(recipient_id, message_text):
    ig_id = 'Enter your instagram id  , which you will get from https://developers.facebook.com'
    access_token='Enter your access token , which you will get from https://developers.facebook.com'
    url = f'https://graph.instagram.com/v20.0/{ig_id}/messages'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    }
    
    #time.sleep(10)
    response = requests.post(url, headers=headers, json=data)
    print("response", response)
    return response.json()

if __name__ == '__main__':
    app.run(port=3000)
