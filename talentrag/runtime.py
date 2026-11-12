import importlib
import sys


def streamlit_module():
    """Load Streamlit exclusively from this interpreter's configured environment."""
    try:
        return importlib.import_module('streamlit')
    except ModuleNotFoundError as error:
        if error.name != 'streamlit':
            raise
    raise ModuleNotFoundError(
        f'Streamlit is unavailable for {sys.executable}. Install requirements.txt using this interpreter.'
    )
