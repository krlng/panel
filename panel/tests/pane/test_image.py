import os

from base64 import b64decode, b64encode
from io import BytesIO, StringIO
from pathlib import Path

from panel.pane import (
    GIF, ICO, JPG, PDF, PNG, SVG,
)
from panel.pane.markup import escape


def test_svg_pane(document, comm):
    rect = """
    <svg xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="10" height="100" width="100"/>
    </svg>
    """
    pane = SVG(rect, encode=True)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;img src=&#x27;data:image/svg+xml;base64')
    assert b64encode(rect.encode('utf-8')).decode('utf-8') in model.text

    # Replace Pane.object
    circle = """
    <svg xmlns="http://www.w3.org/2000/svg" height="100">
      <circle cx="50" cy="50" r="40" />
    </svg>
    """
    pane.object = circle
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;img src=&#x27;data:image/svg+xml;base64')
    assert b64encode(circle.encode('utf-8')).decode('utf-8') in model.text

    pane.encode = False
    assert model.text == escape(circle)

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


twopixel = dict(\
    gif = b'R0lGODlhAgABAPAAAEQ6Q2NYYCH5BAAAAAAAIf8LSW1hZ2VNYWdpY2sNZ2FtbWE' + \
          b'9MC40NTQ1NQAsAAAAAAIAAQAAAgIMCgA7',
    png = b'iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAYAAAD0In+KAAAAFElEQVQIHQEJAPb' + \
          b'/AWNYYP/h4uMAFL0EwlEn99gAAAAASUVORK5CYII=',
    jpg = b'/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQE' + \
          b'BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQ' + \
          b'EBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBA' + \
          b'QEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAIDAREAAhEBAxEB/8QAFAABAAAAAAAA' + \
          b'AAAAAAAAAAAACf/EABoQAAEFAQAAAAAAAAAAAAAAAAYABAU2dbX/xAAVAQEBAAA' + \
          b'AAAAAAAAAAAAAAAAFBv/EABkRAAEFAAAAAAAAAAAAAAAAAAEAAjFxsf/aAAwDAQ' + \
          b'ACEQMRAD8AA0qs5HvTHQcJdsChioXSbOr/2Q==',
    ico = b'AAABAAEAAgEAAAEAIAA0AAAAFgAAACgAAAACAAAAAgAAAAEAIAAAAAAACAAAAHQ' + \
          b'SAAB0EgAAAAAAAAAAAAD//////////wAAAAA=')


def test_imgshape():
    for t in [PNG, JPG, GIF, ICO]:
        w,h = t._imgshape(b64decode(twopixel[t.name.lower()]))
        assert w == 2
        assert h == 1

def test_load_from_byteio():
    """Testing a loading a image from a ByteIo"""
    memory = BytesIO()

    path = os.path.dirname(__file__)
    with open(os.path.join(path, '../test_data/logo.png'), 'rb') as image_file:
        memory.write(image_file.read())

    image_pane = PNG(memory)
    image_data = image_pane._data(memory)
    assert b'PNG' in image_data

def test_load_from_stringio():
    """Testing a loading a image from a StringIO"""
    memory = StringIO()

    path = os.path.dirname(__file__)
    with open(os.path.join(path, '../test_data/logo.png'), 'rb') as image_file:
        memory.write(str(image_file.read()))

    image_pane = PNG(memory)
    image_data = image_pane._data(memory)
    assert 'PNG' in image_data

def test_loading_a_image_from_url():
    """Tests the loading of a image from a url"""
    url = 'https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/logo.png'

    image_pane = PNG(url)
    image_data = image_pane._data(url)
    assert b'PNG' in image_data

def test_image_from_bytes():
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '../test_data/logo.png'), 'rb') as f:
        img = f.read()

    image_pane = PNG(img)
    image_data = image_pane._data(img)
    assert b'PNG' in image_data

def test_loading_a_image_from_pathlib():
    """Tests the loading of a image from a pathlib"""
    filepath = Path(__file__).parent.parent / "test_data" / "logo.png"

    image_pane = PNG(filepath)
    image_data = image_pane._data(filepath)
    assert b'PNG' in image_data

def test_image_alt_text(document, comm):
    """Tests the loading of a image from a url"""
    url = 'https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/logo.png'

    image_pane = PNG(url, embed=False, alt_text="Some alt text")
    model = image_pane.get_root(document, comm)

    assert 'alt=&quot;Some alt text&quot;' in model.text


def test_image_link_url(document, comm):
    """Tests the loading of a image from a url"""
    url = 'https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/logo.png'

    image_pane = PNG(url, embed=False, link_url="http://anaconda.org")
    model = image_pane.get_root(document, comm)

    assert model.text.startswith('&lt;a href=&quot;http://anaconda.org&quot;')


def test_pdf_no_embed(document, comm):
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    pdf_pane = PDF(url, embed=False)
    model = pdf_pane.get_root(document, comm)

    assert model.text.startswith(f"&lt;embed src=&quot;{url}")
