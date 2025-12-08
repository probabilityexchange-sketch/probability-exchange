from playwright.sync_api import Page, expect, sync_playwright

def verify_live_ticker(page: Page):
    """
    Verify that the LiveTicker component renders correctly and does not show persistent errors.
    """
    # 1. Arrange: Go to the application homepage
    page.goto("http://localhost:3000")

    # 2. Assert: Check for "Live Odds" ticker label
    live_odds_label = page.get_by_text("LIVE ODDS")
    expect(live_odds_label).to_be_visible(timeout=20000)

    # 3. Assert: Check for Ticker Items
    # Wait a bit for potential transient error to pass if it triggers
    page.wait_for_timeout(2000)

    # Check if "Unable to load live markets" is VISIBLE (it should NOT be, or should disappear)
    error_msg = page.get_by_text("Unable to load live markets")
    if error_msg.count() > 0:
        expect(error_msg).not_to_be_visible(timeout=6000) # Should disappear after 5s

    # Verify at least one ticker item is present
    # Using more specific selector to avoid ambiguity
    # Use .first to select the first occurrence in the ticker
    btc_item = page.get_by_text("Bitcoin > $100k (Poly)").first
    expect(btc_item).to_be_visible()

    # 4. Screenshot
    page.screenshot(path="/home/jules/verification/live-ticker.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_live_ticker(page)
            print("Verification script ran successfully.")
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="/home/jules/verification/failed_test.png")
        finally:
            browser.close()
