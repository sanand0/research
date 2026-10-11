#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["playwright>=1.50"]
# ///
"""Smoke-test the static file:// guide in a locally installed Edge/Chromium browser."""
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

uri = Path(__file__).with_name("index.html").as_uri()
browser_binary = shutil.which("microsoft-edge") or shutil.which("chromium")
assert browser_binary, "Install Microsoft Edge or Chromium to run the UI tests."

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True, executable_path=browser_binary, args=["--no-sandbox"]
    )
    for width, height in [(1440, 900), (390, 844)]:
        page = browser.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(uri)
        page.locator("#chapters .chapter").first.wait_for()
        assert page.locator(".chapter").count() == 17
        assert page.locator(".map-room").count() == 15
        assert page.locator(".puzzle-card").count() == 1
        assert "Startup Foyer" in page.locator("#room-title").inner_text()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not errors, errors

        page.locator("#spoilers").click()
        assert page.locator(".solution[open]").count() == 1
        page.locator("#next").click()
        assert "Hall of Imports" in page.locator("#room-title").inner_text()
        assert "#step=1&spoilers=1&theme=dark" in page.url
        page.locator("#theme").click()
        assert page.locator("html").get_attribute("data-theme") == "light"

        page.locator("#find").fill("frozendict")
        assert page.locator(".chapter").count() >= 1
        page.locator("#find").fill("")
        page.goto(uri + "#secrets")
        assert page.locator(".secret-card").count() == 11
        for name in ["barry", "thomas", "pablo", "donghee", "savannah", "hugo"]:
            page.locator("#secret-" + name).get_by_role("button").click()
        assert "6 / 11" in page.locator("#found-secrets").inner_text()
        page.locator("#secret-zen").get_by_role("button").click()
        page.locator("#secret-zen summary").click()
        assert page.locator("#secret-zen li").count() == 19
        page.locator("#command").fill("jump foyer")
        page.locator("#command").press("Enter")
        assert "Startup Foyer" in page.locator("#room-title").inner_text()
        page.goto(uri + "#ending")
        assert "375" in page.locator(".ending-score").inner_text()
        assert page.locator(".ending-metrics").locator("div").count() == 5
        assert not errors, errors
        print("PASS", width, "x", height, "navigation, secrets, completion, no errors/overflow")
        page.close()
    browser.close()
