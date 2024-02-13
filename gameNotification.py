import boto3, os
from botocore.exceptions import ClientError

from dotenv import load_dotenv

load_dotenv()


class MessageTemplate:
    @staticmethod
    def insufficient_balance_msg(bet_price, balance, strategy: str = "") -> dict:
        return {
            "message": f"Insufficient balance, bot can not execute bet, bot is trying to place a bet of {bet_price} while the balance remaining is {balance}, strategy - {strategy}",
            "subject": "Insuffient Balance",
        }

    @staticmethod
    def stake_plan_exceeded_msg(campaign_run: int, strategy: str = "") -> dict:
        return {
            "message": f"The staking plan has been exceeded after {campaign_run} consecutive runs, The stake plan has reached the end, Reset state to restart, strategy - {strategy}",
            "subject": "Stake Plan Exceeded",
        }

    @staticmethod
    def martingale_limit_msg(limit_number: int, strategy: str = "") -> dict:
        return {
            "message": "Martingale Limit Exceeded",
            "subject": f"Martingale Limit exceeded of {limit_number}, Reset state to restart, strategy - {strategy}",
        }

    @staticmethod
    def take_profit_msg(profit_made: float) -> dict:
        return {
            "message": f"Take profit reached, you just made {profit_made}, profit target of met N{profit_made}",
            "subject": "Take Profit Reached",
        }


class Notification:
    @staticmethod
    def send_mail(recipient, data: dict = {}):
        # This address must be verified with Amazon SES.
        SENDER = "49ja Notification service <dataslid@gmail.com>"

        RECIPIENT = recipient

        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        AWS_REGION = "us-east-1"

        # The subject line for the email.
        SUBJECT = data.get("subject")

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = data.get("message")

        # The HTML body of the email.
        BODY_HTML = f"""<html>
            <head></head>
            <body>
            <h1>{SUBJECT}</h1>
            <p>{BODY_TEXT}</p>
            </body>
            </html>
        """

        # The character encoding for the email.
        CHARSET = "UTF-8"

        email_key = os.getenv("aws_key")
        email_secret = os.getenv("aws_secret")

        # Create a new SES resource and specify a region.

        # print(recipient, RECIPIENT, email_secret, email_key, AWS_REGION)
        client = boto3.client(
            "ses",
            region_name=AWS_REGION,
            aws_access_key_id=email_key,
            aws_secret_access_key=email_secret,
        )

        try:
            # Provide the contents of the email.
            client.send_email(
                Source=SENDER,
                Destination={
                    "ToAddresses": [
                        RECIPIENT,
                    ],
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": CHARSET,
                            "Data": BODY_HTML,
                        },
                        "Text": {
                            "Charset": CHARSET,
                            "Data": BODY_TEXT,
                        },
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": SUBJECT,
                    },
                },
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Email sent!")
