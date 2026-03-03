# =============================================================================
# website_360_view — Custom Odoo Module
# =============================================================================
# This __init__.py is the ENTRY POINT the Odoo module loader reads.
# It must import every Python sub-package that contains models, controllers, etc.
#
# WHY separate "models" and "controllers" folders?
#   Odoo convention keeps ORM models, HTTP controllers, and wizards in
#   dedicated packages so the codebase stays organized as it grows.
# =============================================================================

from . import models
from . import controllers
