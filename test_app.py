import subprocess
import time
import os
import pytest
from playwright.sync_api import sync_playwright

def test_interactive_readme_generator():
    # 1. Start the server in the background
    server_process = subprocess.Popen(["python3", "demo.py"])
    time.sleep(1.5)  # Let the server bind and start up

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()

            # Go to the local page served by demo.py
            page.goto("http://localhost:8000")

            # Verify the title tag
            assert page.title() == "Interactive README Generator"

            # Check for header element presence
            header_text = page.locator("h1").first.text_content()
            assert "Interactive README Generator" in header_text

            # Select the 'Minimal' template button and click it
            minimal_btn = page.locator("button[data-template='minimal']")
            minimal_btn.click()

            # Verify input-title value was updated to 'Quick-Utils'
            title_input = page.locator("#input-title")
            assert title_input.input_value() == "Quick-Utils"

            # Verify that the raw markdown screen has the correct title
            # Click the Raw Markdown tab
            raw_tab = page.locator("#tab-btn-raw")
            raw_tab.click()

            # Verify that output textarea is populated
            output_textarea = page.locator("#output-markdown")
            output_content = output_textarea.input_value()
            assert "# Quick-Utils" in output_content

            # Switch back to Visual Preview
            preview_tab = page.locator("#tab-btn-preview")
            preview_tab.click()

            # Modify the Title field and see if preview updates dynamically
            title_input.fill("SuperDuperUtils")
            page.wait_for_timeout(300)  # Wait for rendering

            # Check the visual preview pane
            preview_pane = page.locator("#screen-preview")
            assert "SuperDuperUtils" in preview_pane.text_content()

            # Take a screenshot for frontend verification
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, "generator_verification.png")
            page.screenshot(path=screenshot_path)
            print(f"Screenshot captured at: {screenshot_path}")

            browser.close()

    finally:
        # Kill the background server
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_interactive_readme_generator()
