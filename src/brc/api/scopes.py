"""
Defines the scopes used in the BRC component.
"""

from vng_api_common.scopes import Scope


SCOPE_BESLUITEN_ALLES_VERWIJDEREN = Scope(
    'scopes.besluiten.verwijderen',
    description="""
**Laat toe om**:

* besluiten te verwijderen
"""
)
