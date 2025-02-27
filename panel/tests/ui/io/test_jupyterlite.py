import time

from http.client import HTTPConnection
from subprocess import PIPE, Popen

import pytest

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

@pytest.fixture()
def launch_jupyterlite():
    process = Popen(
        ["python", "-m", "http.server", "8123", "--directory", 'lite/dist/'], stdout=PIPE
    )
    retries = 5
    while retries > 0:
        conn = HTTPConnection("localhost:8123")
        try:
            conn.request("HEAD", 'index.html')
            response = conn.getresponse()
            if response is not None:
                break
        except ConnectionRefusedError:
            time.sleep(1)
            retries -= 1

    if not retries:
        raise RuntimeError("Failed to start http server")
    try:
        yield
    finally:
        process.terminate()
        process.wait()


# ImportError: 'process_document_events' from 'bokeh.protocol.messages.patch_doc'"""
@pytest.mark.xfail(reason="Jupyterlite: does not work with Bokeh 3.")
@pytest.mark.flaky(max_runs=3)
@pytest.mark.skip(reason="Requires a dev release to be available")
def test_jupyterlite_execution(launch_jupyterlite, page):
    page.goto("http://localhost:8123/index.html")

    page.locator('text="Getting_Started.ipynb"').first.dblclick()
    for _ in range(6):
        page.locator('[data-command="runmenu:run"]').click()
        page.wait_for_timeout(500)

    page.locator('.noUi-handle').click(timeout=120 * 1000)

    page.keyboard.press('ArrowRight')

    expect(page.locator('.bk-clearfix').first).to_have_text('0.1')
