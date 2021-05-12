from tests.tests import TestOnsiteIsTomorrow
import tokens
import os

tokens.set_tokens()

if __name__ == "__main__":
    TestOnsiteIsTomorrow(os.getenv("GREENHOUSE_API_TOKEN_SAMSARA"))
