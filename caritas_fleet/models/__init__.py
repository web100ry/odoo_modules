import logging
import odoo.tools.i18n
import babel.lists

_logger = logging.getLogger(__name__)

# Monkeypatch babel.lists.format_list to handle missing '2' pattern in some locales/styles
original_babel_format_list = babel.lists.format_list

def safe_babel_format_list(lst, style='standard', locale='en_US'):
    try:
        return original_babel_format_list(lst, style, locale)
    except KeyError as e:
        if str(e) == "'2'" and len(lst) == 2:
            _logger.warning("Babel KeyError '2' for style %s. Falling back to standard style.", style)
            return original_babel_format_list(lst, 'standard', locale)
        raise

babel.lists.format_list = safe_babel_format_list

from . import vehicle_department
from . import caritas_fleet_vehicle
from . import res_users
from . import vehicle_request
from . import vehicle_trip
from . import signal_config
from . import vehicle_usage_log
