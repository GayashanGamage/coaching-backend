import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from dotenv import load_dotenv

load_dotenv()

# brevo configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('brevo')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration))


def sendEmail(mailData):
    Sender = {"name": "gayashan", "email": "gayashan.randimagamage@gmail.com"}
    Headers = {"Some-Custom-Name": "unique-id-1234"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=mailData['to'], headers=Headers, sender=Sender, subject=mailData['subject'], params=mailData['params'], template_id=mailData['template'])
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[{"name": "chamodi", "email": "chamodijanithya@gmail.com"}], headers={"Some-Custom-Name": "unique-id-1234"}, sender={
                                                   "name": "gayashan", "email": "gayashan.randimagamage@gmail.com"}, subject="password reset", template_id=3, params=mailData["params"])
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return {'mail_id': api_response._message_id, 'message': 'sucsusfull'}
    except ApiException as e:
        return {'mail_id': None, 'message': 'Unsucsusfull'}


def welcomeEmail(mailData):
    Sender = {"name": "gayashan", "email": "gayashan.randimagamage@gmail.com"}
    Headers = {"Some-Custom-Name": "unique-id-1234"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=mailData['to'], headers=Headers, sender=Sender, subject=mailData['subject'], params=mailData['params'], template_id=mailData['template'])
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return {'mail_id': api_response._message_id, 'message': 'sucsusfull'}
    except ApiException as e:
        return {'mail_id': None, 'message': 'Unsucsusfull'}
