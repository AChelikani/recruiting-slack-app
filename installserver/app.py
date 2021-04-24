from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    """
    Home page has Add to Slack button with scopes embedded.
    Random state is generated and stored in memory and appended to direct install URL.
    User is redirected to Slack App consent screen.
    On approval (or rejection), user is redirected to callback URL with state param and code.
    """
    return "Home"


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
    return "Callback"


if __name__ == "__main__":
    app.run(port=8000)