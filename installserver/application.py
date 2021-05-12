from flask import Flask, render_template, request, url_for
import secrets
import requests
from requests.auth import HTTPBasicAuth
import os
from slack_sdk import WebClient
from twilio.rest import Client


twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_access_token = os.getenv("TWILIO_ACCESS_TOKEN")
client = Client(twilio_account_sid, twilio_access_token)


def send_msg(msg):
    client.messages.create(body=msg, to="+12242794668", from_="+19163827393")


application = Flask(__name__)

if not os.getenv("PRODUCTION"):
    application.config["SERVER_NAME"] = "localhost:5000"
    import tokens

    tokens.set_app_client_id_and_secret()
else:
    application.config["SERVER_NAME"] = "getolive.xyz"
    application.config["PREFERRED_URL_SCHEME"] = "https"

# TODO: Make this a session to state map.
state_map = {}


@application.route("/interactivity_callback", methods=["POST"])
def interactivity_callback():
    """
    Required callback that Slack will POST a request to when a user clicks on a button
    in the bot's messages. Must respond with a 200.

    https://github.com/slackapi/node-slack-sdk/issues/869
    """
    return "Success"


@application.route("/callback")
def callback():
    """
    Verify state param value matches value held in memory.
    Make request to https://api.slack.com/methods/oauth.v2.access with client ID, client secret, and code received on callback.
    Response from Slack will contain access token for org doing installation.
    Ping access token via. some secure channel.
        - Upload to another S3 bucket to be manually added to lambda env variables.
        -
    Show successful landing page.
    """
    state = request.args.get("state")
    code = request.args.get("code")

    if state not in state_map:
        return render_template("callback.html", access_token="FAILURE")

    slack_oauth_url = "https://api.slack.com/methods/oauth.v2.access"

    client = WebClient()
    resp = client.oauth_v2_access(
        client_id=os.environ["SLACK_BOT_CLIENT_ID"],
        client_secret=os.environ["SLACK_BOT_CLIENT_SECRET"],
        code=code,
        redirect_uri=url_for("callback", _external=True),
    )

    access_token = resp["access_token"]
    bot_user_id = resp["bot_user_id"]
    app_id = resp["app_id"]

    send_msg(access_token)

    # Log all this junk until we can save it in the config directly
    print(resp)

    return render_template("callback.html")


@application.route("/")
def home():
    """
    Home page has Add to Slack button with scopes embedded.
    Random state is generated and stored in memory and appended to direct install URL.
    User is redirected to Slack App consent screen.
    On approval (or rejection), user is redirected to callback URL with state param and code.
    """
    state = secrets.token_hex(8)
    state_map[state] = True
    redirect_uri = url_for("callback", _external=True)
    scopes = [
        "channels:history",
        "channels:manage",
        "chat:write",
        "groups:write",
        "users:read",
        "users:read.email",
    ]
    scopes = ",".join(scopes)
    client_id = os.environ["SLACK_BOT_CLIENT_ID"]
    return render_template(
        "index.html",
        state=state,
        redirect_uri=redirect_uri,
        client_id=client_id,
        scopes=scopes,
    )


if __name__ == "__main__":
    application.run()
