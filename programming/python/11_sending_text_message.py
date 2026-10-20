# create a twilio account and get a phone number.

# install twilio with pipenv instal twilio.

from twilio.rest import Client

account_sid = "" # get the sid from twilio console
auth_token = "" 

client = Client(account_sid, auth_token)

call = client.messages.create(
  to="",
  from_="",
  body="This is our first message"
)
