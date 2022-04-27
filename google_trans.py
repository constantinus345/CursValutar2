from base64 import encode
from http.client import ImproperConnectionState
from google.cloud import translate_v2 as translate
import six
import configs
from google.oauth2 import service_account
import html

creds = service_account.Credentials.from_service_account_file(filename=configs.JSON_Creds_Translate)
translate_client = translate.Client(credentials=creds)


def translate_text(target_language, text, source_language=None):
    """Translates text into the target_language language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    #if isinstance(text, six.binary_type):
     #   text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target_language, source_language=source_language)

    return result


"""
test1 = translate_text(target_language="en", text= "o stii de ce plang chitarele", source_language=None)
{'translatedText': 'You know why the guitars cry', 'detectedSourceLanguage': 'ro', 'input': 'o stii de ce plang chitarele'}


test1 = translate_text(target_language="en", text= "o stii de ce plang chitarele", source_language="ro")
{'translatedText': 'You know why the guitars cry', 'input': 'o stii de ce plang chitarele'}

print(test1)

!!!
To print properly, you need:
print(html.unescape(test1["translatedText"]))
"""

