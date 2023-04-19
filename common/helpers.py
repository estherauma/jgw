from enum import Enum

from common.checklists import CheckLists
from common.help_contacts import HelpContacts
from common.inline import Inline
from common.messaging import Messaging
from common.preferences import Preferences

HELPERS = {
    "inline": lambda: Inline(),
    "inlineQNs_responses": lambda: Inline(),
    "inlineQNs_participation": lambda: Inline(),
    "preferences": lambda: Preferences(),
    "help_contacts": lambda: HelpContacts(),
    "messaging": lambda: Messaging(),
    "visa": lambda: CheckLists(key="visa"),
    "joboffer": lambda: CheckLists(key="joboffer"),
    "contract": lambda: CheckLists(key="contract"),
    "beforeyougo": lambda: CheckLists(key="beforeyougo"),
}


class HelpersParameters(Enum):
    INLINE = 'inline'
    INLINEQNS_RESPONSES = 'inlineQNs_responses'   
    INLINEQNS_PARTICIPATION = 'inlineQNs_participation' 
    PREFERENCES = 'preferences'
    HELP_CONTACTS = 'help_contacts'
    MESSAGING = 'messaging'
    VISA = 'visa'
    JOBOFFER = 'joboffer'
    CONTRACT = 'contract'
    BEFOREYOUGO = 'beforeyougo'