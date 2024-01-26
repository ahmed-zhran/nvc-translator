from flask import Flask, session, request, jsonify, render_template
import openai
import os
from flask_frozen import Freezer
from slackeventsapi import SlackEventAdapter
from slack import WebClient
##################### global settings
openai.api_key = os.getenv("OPENAI_API_KEY")

SESSION_KEY = "json"

#######################freeze app
# Initialize Flask app
app = Flask(__name__)
app.config.update(
    ENV='development',
    SECRET_KEY=os.getenv("SECRET_KEY"),
    FREEZER_DESTINATION = './build',
    FREEZER_BASE_URL = 'https://nvctranslator.com',  # set to your domain in production
    FREEZER_REMOVE_EXTRA_FILES = False,  # careful with this in production
)

# Initialize Freezer before defining routes
freezer = Freezer(app)

@app.route('/')
def home():
   return render_template("index.html", src="mobile")

@app.route('/privacy-policy.html')
def privacy_policy():
   return render_template("privacy-policy.html", src="mobile")

# This is the part where we initialize the freezing process
if __name__ == '__main__':
    # Uncomment to run your application normally with Flask
    # app.run(debug=True) 

    # If you want to freeze your application and generate static files, uncomment below
    freezer.freeze()

########################################### flask app
# Initialize Flask app
app = Flask(__name__)
app.config.update(
    ENV='development',
    SECRET_KEY=os.getenv("SECRET_KEY"),
)

@app.route('/')
def home():
   return render_template("index.html", src="web")

@app.route('/privacy-policy')
def privacy_policy():
   return render_template("privacy-policy.html", src="web")

@app.route("/translate", methods=["GET"])
def get():
    # get = session.get(SESSION_KEY)
    text = request.args.get("text")
    response = jsonify(__default_message(text), 200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/post", methods=["POST"])
def post():
    post = request.get_json()
    print(post)
    
    if post is not None:
        session[SESSION_KEY] = post
        return jsonify(__default_message(post["text"]), 201)
    else:
        return jsonify(__default_message(message="wrong payload"), 400)
    
########## slack integeration
# Initialize the Slack event adapter
signing_secret = os.getenv("SLACK_SIGNING_SECRET")
slack_token = os.getenv("SLACK_TOKEN")
slack_event_adapter = SlackEventAdapter(signing_secret, endpoint="/slack/events", server=app)
slack_client = WebClient(token=slack_token)

# Define routes for Slack events
# Example responder to bot mentions
############ old model
# @slack_event_adapter.on("app_mention")
# def handle_mentions(event_data):
#     print(event_data)
#     event = event_data["event"]
#     text = event["text"]
#     translation = "translation: " + text
#     slack_client.chat_postMessage(
#         channel=event["channel"],
#         text=f">{translation}",
#     )
############ new model
@slack_event_adapter.on("app_mention")
def handle_mentions(event_data):
    print(event_data)
    event = event_data["event"]
    channel_id = event["channel"]
    user_id = event["user"]
    message_text = event["text"]

    # Check if the bot user ID is mentioned in the message
    bot_user_id = os.getenv("SLACK_BOT_ID")  # Replace with your bot user ID
    message_text = message_text.replace(f"<@{bot_user_id}>", "")

    # Create a private channel with the user (if it doesn't exist)
    response = slack_client.conversations_open(users=[user_id])

    if response["ok"]:
        private_channel_id = response["channel"]["id"]
        translated_text = __slack_message(message_text)
        
        # Send the response to the private channel
        slack_client.chat_postMessage(
            channel=private_channel_id,
            text=f"You said privately:\n>{message_text}\n\nI translated it to:\n>{translated_text}",
        )
    return


# Example responder to greetings
# @slack_event_adapter.on("message")
# def handle_message(event_data):
#     print(event_data)
#     message = event_data["event"]
#     # If the incoming message contains "hi", then respond with a "Hello" message
#     # if message.get("subtype") is None and "hi" in message.get('text'):
#     channel = message["channel"]
#     message = "Hello <@%s>! :tada:" % message["user"]
#     slack_client.chat_postMessage(channel=channel, text=message)

########## functions
            
def __slack_message(message:str):
    ################# new model
    result = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages= [
            {
                "role": "system",
                "content": "Rephrase the following in NVC Language. Be careful to distinguish pseudofeelings from feelings. and Ignore the text that matches the following regex in translation '<@[^>]+>' which is slack mentions and emped them back to the response as it is."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        # max_tokens=3000,
        temperature=1.2
    )
    print(result)
    return result["choices"][0]["message"]["content"]

def __default_message(message:str):
    # new_prompt = "Rephrase in NVC language " + message
    # new_prompt = "Rephrase the following in NVC Language. Be careful to distinguish pseudofeelings from feelings. \n" + message
    # new_prompt = "I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [Observations, Feelings, Needs,  Requests] after the rephrased text. here is the original text to rephrase: \""+ message + "\". I need the full response in json object including [original_txt, rephrased_txt, Observations, Feelings, Needs,  Requests]"
    # new_prompt = "I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [Observations, Feelings, Needs,  Requests] after the rephrased text. here is the original text to rephrase: \""+ message + "\". I need each of those [original_txt, rephrased_txt, Observations, Feelings, Needs,  Requests] in a seperate line without gab lines or prefix or postfix response explanation or start ."
    # new_prompt = 'I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [observations, feelings, needs,  requests] after the rephrased text. here is the original text to rephrase: "'+ message + '". I need each of those keys [original_txt, rephrased_txt, observations, feelings, needs,  requests] in the json object format and for each of the these keys [Observations, Feelings, Needs,  Requests] the value must be a valid array format even for single values ex(["val 1", "val 2"], ["val 1"], []) - without gab lines or prefix or postfix response explanation (example valid response: ' "original_txt:\"somevalue\"\nrephrased_txt: \"somevalue.\"\n\nobservations: somevaluesArray\nfeelings: somevaluesArray\nneeds: somevaluesArray\nrequests: somevaluesArray"')'
    new_prompt = 'I will give you a text rephrase in NVC Language. Be careful to distinguish pseudofeelings from feelings. Rephrase it and then list down those [observations, feelings, needs,  requests] after the rephrased text. here is the original text to rephrase: "'+ message + '". I need each of those keys [original_txt, rephrased_txt, observations, feelings, needs,  requests] in the json object format and for each of the these keys [observations, feelings, needs,  requests] the value must be a valid array format even for single values ex(["val 1", "val 2"], ["val 1"], []) '
    ##########3###### old model
    # result = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=new_prompt,
    #     max_tokens=3000,
    #     temperature=1.2
    # )
    # return {"translation": result["choices"][0]["text"]}
    ################# new model
    result = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "user", "content": new_prompt},
        ],
        # max_tokens=3000,
        temperature=1.2,
        response_format={ "type": "json_object" }
    )
    print(result)
    return {"translation": result["choices"][0]["message"]["content"]}


# app.run(host="127.0.0.1", port=5000, debug=True) # uncomment to run locally #runningLocally #ref


