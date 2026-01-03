import json
import time
from playwright.sync_api import sync_playwright

def scrape_shop(shop_url):
    """
    Scrape Etsy shop - you'll log in once, then it remembers you.
    """
    print(f"🚀 Starting sync for: {shop_url}\n")
    
    with sync_playwright() as p:
        # Use a persistent context with its own data directory
        # This saves login state between runs
        browser = p.chromium.launch_persistent_context(
            "./browser_data",  # Local folder for browser data
            headless=False,
            viewport={'width': 1280, 'height': 800},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        try:
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            print("📡 Opening Etsy in browser...")
            page.goto("https://www.etsy.com", wait_until='domcontentloaded', timeout=30000)
            
            print("\n" + "="*70)
            print("⚠️  If you're not logged in, please log in now.")
            print("="*70)
            print("\n👉 Press ENTER when you're logged in and ready to continue...")
            input()
            
            print("\n📡 Navigating to your shop...")
            try:
                page.goto(shop_url, wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                if "interrupted" in str(e).lower():
                    print("⚠️  Navigation was redirected (normal for login). Waiting for page to settle...")
                    time.sleep(3)
                else:
                    raise
            
            # Check if we need to log in
            time.sleep(3)
            current_url = page.url.lower()
            
            if "sign-in" in current_url or "signin" in current_url or "ref_login_action" in current_url:
                print("\n" + "="*70)
                print("⚠️  YOU NEED TO LOG IN")
                print("="*70)
                print("\n👉 Please log in to Etsy in the browser, then press ENTER here...")
                input()
                
                print("\n✅ Continuing...")
                time.sleep(2)
            
            print("📜 Loading all products...")
            
            # Scroll to trigger lazy loading
            for i in range(5):
                page.evaluate(f'window.scrollTo(0, {(i+1) * 800})')
                time.sleep(0.8)
            
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)
            
            print("🔍 Extracting product data...")
            
            # Extract products
            js_code = """
            () => {
                const products = [];
                const seen = new Set();
                
                // Find all listing links
                const links = document.querySelectorAll('a[href*="/listing/"]');
                
                links.forEach(linkEl => {
                    try {
                        const href = linkEl.href;
                        if (!href || !href.includes('/listing/')) return;
                        
                        const baseLink = href.split('?')[0];
                        if (seen.has(baseLink)) return;
                        seen.add(baseLink);
                        
                        // Extract listing ID
                        const listingIdMatch = baseLink.match(/listing\\/(\\d+)/);
                        if (!listingIdMatch) return;
                        const listingId = listingIdMatch[1];
                        
                        // Find the parent container
                        const container = linkEl.closest('[data-listing-id]') || 
                                         linkEl.closest('.wt-grid__item-xs-6') || 
                                         linkEl.closest('.v2-listing-card') ||
                                         linkEl.parentElement;
                        
                        // Extract title
                        let title = '';
                        const titleEl = container.querySelector('h3, h2, [data-listing-title]');
                        if (titleEl) {
                            title = titleEl.textContent.trim();
                        } else if (linkEl.textContent && !linkEl.querySelector('img')) {
                            title = linkEl.textContent.trim();
                        }
                        
                        // Extract image
                        let image = '';
                        const imgEl = container.querySelector('img') || linkEl.querySelector('img');
                        if (imgEl) {
                            image = imgEl.getAttribute('data-src') || 
                                   imgEl.getAttribute('src') || 
                                   imgEl.getAttribute('data-srcset')?.split(' ')[0] || '';
                            
                            // Upgrade to full resolution
                            if (image) {
                                image = image.replace(/il_\\d+x\\d+/g, 'il_1588xN')
                                            .replace(/il_\\d+xN/g, 'il_1588xN');
                            }
                        }
                        
                        // Extract price
                        let price = '';
                        const priceEl = container.querySelector('[class*="currency"], [class*="price"], .wt-text-title-01');
                        if (priceEl) {
                            price = priceEl.textContent.trim().replace(/\\s+/g, ' ');
                        }
                        
                        // Only add if we have at least a title or valid ID
                        if (title || listingId) {
                            const shareLink = `https://scribblepatchdesigns.etsy.com/listing/${listingId}?utm_source=showcase_site&utm_medium=product_grid&utm_campaign=share_and_save`;
                            
                            products.push({
                                title: title || `Listing ${listingId}`,
                                link: shareLink,
                                image: image,
                                price: price,
                                listingId: listingId
                            });
                        }
                    } catch (e) {
                        console.error('Error:', e);
                    }
                });
                
                return products;
            }
            """
            
            products = page.evaluate(js_code)
            
            if products and len(products) > 0:
                # Save to JSON
                with open('products.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, indent=4, ensure_ascii=False)
                
                print(f"\n✅ SUCCESS: Synced {len(products)} products!")
                print(f"💾 Saved to: products.json\n")
                
                # Show sample
                print("📦 Sample product:")
                print(f"   Title: {products[0]['title']}")
                print(f"   Price: {products[0]['price']}")
                print(f"   Image: {'✓' if products[0]['image'] else '✗'}")
                print(f"   Link: {products[0]['link'][:65]}...")
                
            else:
                print("\n⚠️  No products found.")
                print("📸 Taking screenshot for debugging...")
                page.screenshot(path='debug_screenshot.png')
                print("Screenshot saved as: debug_screenshot.png")
                
                # Save HTML for inspection
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("HTML saved as: debug_page.html")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            try:
                if page:
                    page.screenshot(path='error_screenshot.png')
                    print("📸 Error screenshot saved")
            except:
                pass
        
        finally:
            print("\n👋 Closing browser in 2 seconds...")
            time.sleep(2)
            browser.close()


if __name__ == "__main__":
    print("=" * 70)
    print("ScribblePatch Designs - Product Sync")
    print("=" * 70)
    print()
    print("ℹ️  You'll need to log in once. Your session will be saved.")
    print("   Shop owner visits don't affect customer conversion metrics.")
    print()
    
    scrape_shop("https://www.etsy.com/shop/ScribblePatchDesigns")