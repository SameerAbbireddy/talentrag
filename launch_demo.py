import sys
from pathlib import Path

from talentrag.runtime import streamlit_module


if __name__ == '__main__':
    try:
        streamlit_module()
        from streamlit.web import cli
        sys.argv = ['streamlit', 'run', str(Path(__file__).with_name('app.py')), '--server.address=127.0.0.1', '--server.port=8501', '--browser.gatherUsageStats=false'] + sys.argv[1:]
        sys.exit(cli.main())
    except (ImportError, PermissionError) as error:
        print(f'TalentRAG could not start: {error}', file=sys.stderr)
        if isinstance(error, PermissionError):
            print('Local socket binding was denied. Run this command in a normal Terminal outside the restricted agent sandbox.', file=sys.stderr)
        sys.exit(1)
