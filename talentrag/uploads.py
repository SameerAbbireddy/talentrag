from io import BytesIO
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from .core import mentions, skills


def extract_text(name, data):
    if len(data) > 10 * 1024 * 1024:
        raise ValueError('Maximum resume size is 10 MB.')
    extension = Path(name).suffix.lower()
    try:
        if extension == '.txt':
            text = data.decode('utf-8-sig')
        elif extension == '.docx':
            with zipfile.ZipFile(BytesIO(data)) as archive:
                if sum(item.file_size for item in archive.infolist()) > 30 * 1024 * 1024:
                    raise ValueError('DOCX expanded content exceeds 30 MB.')
                root = ET.fromstring(archive.read('word/document.xml'))
            text = '\n'.join(''.join(paragraph.itertext()) for paragraph in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))
        elif extension == '.pdf':
            try:
                from pypdf import PdfReader
            except ImportError as error:
                raise ValueError('PDF extraction unavailable: install pypdf in the active environment or use TXT/DOCX.') from error
            else:
                reader = PdfReader(BytesIO(data))
                if reader.is_encrypted:
                    raise ValueError('Encrypted PDF: provide an unlocked document.')
                text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        else:
            raise ValueError('Supported formats: TXT, PDF, DOCX.')
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f'Could not extract {extension} text: {error}') from error
    if not text.strip():
        raise ValueError('No extractable text. This may be a scanned PDF; OCR is not implemented.')
    return text


def compare_upload(text, job):
    required = skills(job['must_have_skills'])
    preferred = skills(job['nice_to_have_skills']) - required
    result = {}
    for label, terms in [('required', required), ('preferred', preferred)]:
        result[label + '_matched'] = sorted(term for term in terms if mentions(text, term))
        result[label + '_missing'] = sorted(term for term in terms if not mentions(text, term))
    result['snippets'] = [line for line in text.splitlines() if any(mentions(line, term) for term in required | preferred)]
    return result
