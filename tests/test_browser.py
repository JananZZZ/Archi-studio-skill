from pathlib import Path
import pytest, threading, http.server, socketserver, functools
from archi_studio.models import Preferences
from archi_studio.orchestrator import ArchiStudio

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=ROOT/'examples'/'sample_input'

class Reuse(socketserver.TCPServer):
    allow_reuse_address=True

def serve_dir(root: Path):
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
    httpd=Reuse(('127.0.0.1',0),handler)
    t=threading.Thread(target=httpd.serve_forever,daemon=True); t.start()
    return httpd, f'http://127.0.0.1:{httpd.server_address[1]}'

def launch(pw):
    exe='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None
    return pw.chromium.launch(headless=True,executable_path=exe,args=['--no-sandbox'])

def test_interactive_editor_chromium(tmp_path):
    try: from playwright.sync_api import sync_playwright
    except Exception: pytest.skip('playwright not installed')
    out=tmp_path/'browser'; ArchiStudio().build(SAMPLE,out,Preferences(),raster=False)
    server,url=serve_dir(out)
    try:
        with sync_playwright() as pw:
            browser=launch(pw); page=browser.new_page(accept_downloads=True)
            page.set_content((out/'interactive_editor.html').read_text(encoding='utf-8'), wait_until='load')
            assert page.locator('#project svg').count()==1
            page.select_option('#palette','academic-light')
            page.fill('#titleText','Browser Test')
            page.click('button:has-text("应用预览")')
            assert 'Browser Test' in page.locator('#project svg').text_content()
            with page.expect_download() as dl: page.click('button:has-text("导出项目 SVG")')
            assert dl.value.suggested_filename.endswith('.svg')
            with page.expect_download() as dl2: page.click('button:has-text("导出项目 PNG")')
            assert dl2.value.suggested_filename.endswith('.png')
            browser.close()
    finally: server.shutdown(); server.server_close()

def test_questionnaire_chromium(tmp_path):
    try: from playwright.sync_api import sync_playwright
    except Exception: pytest.skip('playwright not installed')
    out=tmp_path/'q'; ArchiStudio().build(SAMPLE,out,Preferences(),raster=False)
    # questionnaire references ../presets during packaged use; for browser test copy preview assets next to parent.
    import shutil
    shutil.copytree(ROOT/'presets',tmp_path/'presets')
    server,url=serve_dir(tmp_path)
    try:
        with sync_playwright() as pw:
            browser=launch(pw); page=browser.new_page(accept_downloads=True)
            page.set_content((out/'questionnaire.html').read_text(encoding='utf-8'), wait_until='load')
            page.select_option('#mode','academic')
            assert 'academic-light' in page.locator('#preview').inner_text()
            with page.expect_download() as dl: page.click('#download')
            assert dl.value.suggested_filename=='diagram.config.json'
            browser.close()
    finally: server.shutdown(); server.server_close()
