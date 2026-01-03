from playwright.sync_api import sync_playwright
import json
import time

def scrape_etsy_playwright(shop_url):
    print(f"Launching browser for {shop_url}...")
    
    with sync_playwright() as p:
        # Launch browser - headless=False lets you see it working
        browser = p.chromium.launch(
            headless=False,  # Change to True once working
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US'
        )
        
        page = context.new_page()
        
        try:
            print("Loading shop page...")
            page.goto(shop_url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for listings to appear
            print("Waiting for products to load...")
            try:
                page.wait_for_selector('[data-listing-id]', timeout=15000)
            except:
                print("Timeout waiting for products, but continuing...")
            
            time.sleep(2)  # Extra wait for dynamic content
            
            # Scroll to load lazy images
            print("Scrolling to load all images...")
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)
            
            # Extract data directly with JavaScript for better reliability
            js_code = """
            () => {
                const items = [];
                const seen = new Set();
                
                const listings = document.querySelectorAll('[data-listing-id]');
                
                listings.forEach(listing => {
                    try {
                        const titleEl = listing.querySelector('h3, h2, [data-listing-title]');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        
                        if (!title || title === 'No Title' || title === 'Create new collection') {
                            return;
                        }
                        
                        const linkEl = listing.querySelector('a[href*="/listing/"]');
                        let link = linkEl ? linkEl.href : '';
                        
                        // Clean up URL and add functional parameters in specific order
                        const url = new URL(link);
                        
                        // Get ref parameter and item number
                        const refParam = url.searchParams.get('ref');
                        let itemNum = '1';
                        if (refParam && refParam.startsWith('shop_home_active_')) {
                            itemNum = refParam.split('_').pop();
                        } else if (refParam && refParam.includes('-')) {
                            itemNum = refParam.split('-').pop();
                        }
                        
                        // Build clean URL with parameters in desired order
                        const baseUrl = url.origin + url.pathname;
                        link = `${baseUrl}?ls=r&sr_prefetch=1&pf_from=shop_home&ref=items-pagination-${itemNum}&dd=1`;
                        
                        if (!link) {
                            return;
                        }
                        
                        if (seen.has(link)) {
                            return;
                        }
                        seen.add(link);
                        
                        const imgEl = listing.querySelector('img');
                        let img = imgEl ? (imgEl.dataset.src || imgEl.src || '') : '';
                        
                        // Replace thumbnail size with full size
                        if (img && img.includes('il_340x270')) {
                            img = img.replace('il_340x270', 'il_1588xN');
                        } else if (img && img.includes('il_170x135')) {
                            img = img.replace('il_170x135', 'il_1588xN');
                        } else if (img && img.includes('il_75x75')) {
                            img = img.replace('il_75x75', 'il_1588xN');
                        }
                        
                        let price = '0.00';
                        let symbol = '$';
                        
                        const priceEl = listing.querySelector('[class*="currency"], [class*="price"]');
                        if (priceEl) {
                            const priceText = priceEl.textContent;
                            const priceMatch = priceText.match(/[\$£€]?([\d,]+\.?\d*)/);
                            if (priceMatch) {
                                price = priceMatch[1];
                                const symbolMatch = priceText.match(/([\$£€])/);
                                if (symbolMatch) {
                                    symbol = symbolMatch[1];
                                }
                            }
                        }
                        
                        items.push({
                            title: title,
                            link: link,
                            image: img,
                            price: symbol + price
                        });
                    } catch (e) {
                        console.log('Error parsing listing:', e);
                    }
                });
                
                return items;
            }
            """
            
            products = page.evaluate(js_code)
            
            if not products:
                print("\n⚠ No products found!")
                print("Saving screenshot and HTML for debugging...")
                page.screenshot(path='debug_screenshot.png')
                
                html = page.content()
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                
                print("Saved: debug_screenshot.png and debug_page.html")
                print("\nPossible issues:")
                print("1. Shop might be empty or private")
                print("2. Etsy changed their HTML structure")
                print("3. Cloudflare is still blocking")
                return
            
            # Save to JSON
            with open('products.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=4, ensure_ascii=False)
            
            print(f"\n✓ SUCCESS! Saved {len(products)} products to products.json")
            
            # Display first 5 products
            if products:
                print("\n📦 First 5 products found:")
                for i, p in enumerate(products[:5], 1):
                    print(f"{i}. {p['title']}")
                    print(f"   Price: {p['price']}")
                    print(f"   Link: {p['link'][:60]}..." if len(p['link']) > 60 else f"   Link: {p['link']}")
                    print()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Save debug info
            try:
                page.screenshot(path='error_screenshot.png')
                print("Saved error screenshot: error_screenshot.png")
            except:
                pass
        
        finally:
            print("\nClosing browser...")
            browser.close()

if __name__ == "__main__":
    shop_url = "https://www.etsy.com/shop/ScribblePatchDesigns"
    scrape_etsy_playwright(shop_url)