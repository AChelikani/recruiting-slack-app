from flask import Flask, render_template, request
import secrets
import requests
from requests.auth import HTTPBasicAuth
import os
import tokens
from slack_sdk import WebClient

tokens.set_app_client_id_and_secret()

app = Flask(__name__)

# TODO: Make this a session to state map.
state_map = {}


@app.route("/callback")
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
    state = request.args["state"]
    code = request.args["code"]

    if state not in state_map:
        return render_template("callback.html", access_token="FAILURE")

    slack_oauth_url = "https://api.slack.com/methods/oauth.v2.access"

    client = WebClient()
    resp = client.oauth_v2_access(
        client_id=os.environ["SLACK_BOT_CLIENT_ID"],
        client_secret=os.environ["SLACK_BOT_CLIENT_SECRET"],
        code=code,
        redirect_uri="http://localhost:8000/callback",
    )

    access_token = resp["access_token"]
    bot_user_id = resp["bot_user_id"]
    app_id = resp["app_id"]

    return render_template("callback.html", access_token=access_token)


@app.route("/")
def home():
    """
    Home page has Add to Slack button with scopes embedded.
    Random state is generated and stored in memory and appended to direct install URL.
    User is redirected to Slack App consent screen.
    On approval (or rejection), user is redirected to callback URL with state param and code.
    """
    state = secrets.token_hex(8)
    state_map[state] = True
    redirect_uri = "http://localhost:8000/callback"
    return render_template("index.html", state=state, redirect_uri=redirect_uri)


if __name__ == "__main__":
    app.run(port=8000)