# Stubs for mlconjug (Python 3.4 to 3.6)


from .mlconjug import *
from .PyVerbiste import *
from typing import Text, Tuple
import gettext

__author__: Text
__email__: Text
__version__: Text
__copyright__: Text
__credits__: Tuple[Text]
__license__: Text
__maintainer__: Text
__status__: Text
_RESOURCE_PACKAGE: Text = __name__
_TRANSLATIONS_PATH: Text
_SUPPORTED_LANGUAGES: Tuple[Text]
_TRANSLATED_LANGUAGES: Tuple[Text]
_MLCONJUG_TRANSLATIONS: gettext.GNUTranslations
_user_locale: Text

def _get_user_locale() -> Text: ...

def _getdoc(object: object) -> Text: ...
