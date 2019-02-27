"""
Defines the scopes used in the BRC component.
"""

from zds_schema.scopes import Scope


SCOPE_BESLUITEN_ALLES_VERWIJDEREN = Scope(
    'scopes.besluiten.verwijderen',
    description="""
**Laat toe om**:

* besluiten te verwijderen
"""
)
