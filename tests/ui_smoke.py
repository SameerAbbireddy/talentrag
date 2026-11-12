import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas
import numpy
from talentrag.runtime import streamlit_module
streamlit_module()
from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60).run()
assert not app.exception, app.exception
app.button[0].click().run()
assert not app.exception, app.exception
assert any('Top 10 candidates' in item.value for item in app.subheader)
app.selectbox[1].select('BM25').run()
app.button[0].click().run()
assert not app.exception, app.exception
app.radio[0].set_value('Custom job').run()
app.text_area[0].set_value('Build Python and SQL services using Flask').run()
app.button[0].click().run()
assert not app.exception, app.exception
next(item for item in app.selectbox if item.label == 'Or use a fictional demo TXT').select('fictional_backend.txt').run()
next(item for item in app.button if item.label == 'Compare extracted text').click().run()
assert not app.exception, app.exception
app.text_area[0].set_value('Changed job description').run()
assert not any('Top 10 candidates' == item.value for item in app.subheader)
original_exists = Path.exists
with patch.object(Path, 'exists', lambda path: False if path.name == 'development.json' else original_exists(path)):
    app.run()
    assert not app.exception, app.exception
    assert any('metadata is missing' in item.value for item in app.warning)
original_read_csv = pandas.read_csv
def read_csv_with_invalid_evaluation(path, *args, **kwargs):
    if Path(path).name == 'development.csv':
        return pandas.DataFrame({'unexpected': [1]})
    return original_read_csv(path, *args, **kwargs)
with patch.object(pandas, 'read_csv', side_effect=read_csv_with_invalid_evaluation):
    app.run()
    assert not app.exception, app.exception
    assert any('Evaluation results unavailable' in item.value for item in app.warning)
print('PASS: initial render, baseline, BM25, custom job, fictional upload, stale ranking hidden, missing metadata and invalid evaluation CSV handled.')
