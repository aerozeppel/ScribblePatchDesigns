import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

def scrape_shop(shop_url):
    """
    Enhanced scraper that preserves description formatting
    """
    print(f"🚀 Starting enhanced product sync for: {shop_url}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            "./browser_data",
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
                    print("⚠️  Navigation was redirected (normal for login). Waiting...")
                    time.sleep(3)
                else:
                    raise
            
            time.sleep(3)
            current_url = page.url.lower()
            
            if "sign-in" in current_url or "signin" in current_url:
                print("\n⚠️  Please log in, then press ENTER...")
                input()
                time.sleep(2)
            
            print("📜 Loading all products...")
            
            # Scroll to load everything
            for i in range(5):
                page.evaluate(f'window.scrollTo(0, {(i+1) * 800})')
                time.sleep(0.8)
            
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)
            
            print("🔍 Extracting basic product data...")
            
            # First pass: Get all listing IDs and basic info
            js_code = """
            () => {
                const products = [];
                const seen = new Set();
                
                const links = document.querySelectorAll('a[href*="/listing/"]');
                
                links.forEach(linkEl => {
                    try {
                        const href = linkEl.href;
                        if (!href || !href.includes('/listing/')) return;
                        
                        const baseLink = href.split('?')[0];
                        if (seen.has(baseLink)) return;
                        seen.add(baseLink);
                        
                        const listingIdMatch = baseLink.match(/listing\\/(\\d+)/);
                        if (!listingIdMatch) return;
                        const listingId = listingIdMatch[1];
                        
                        const container = linkEl.closest('[data-listing-id]') || 
                                         linkEl.closest('.wt-grid__item-xs-6') || 
                                         linkEl.closest('.v2-listing-card') ||
                                         linkEl.parentElement;
                        
                        let title = '';
                        const titleEl = container.querySelector('h3, h2, [data-listing-title]');
                        if (titleEl) {
                            title = titleEl.textContent.trim();
                        } else if (linkEl.textContent && !linkEl.querySelector('img')) {
                            title = linkEl.textContent.trim();
                        }
                        
                        let image = '';
                        const imgEl = container.querySelector('img') || linkEl.querySelector('img');
                        if (imgEl) {
                            image = imgEl.getAttribute('data-src') || 
                                   imgEl.getAttribute('src') || 
                                   imgEl.getAttribute('data-srcset')?.split(' ')[0] || '';
                            
                            if (image) {
                                image = image.replace(/il_\\d+x\\d+/g, 'il_1588xN')
                                            .replace(/il_\\d+xN/g, 'il_1588xN');
                            }
                        }
                        
                        let price = '';
                        const priceEl = container.querySelector('[class*="currency"], [class*="price"], .wt-text-title-01');
                        if (priceEl) {
                            price = priceEl.textContent.trim().replace(/\\s+/g, ' ');
                        }
                        
                        if (title || listingId) {
                            products.push({
                                title: title || `Listing ${listingId}`,
                                listingId: listingId,
                                image: image,
                                price: price,
                                fullUrl: baseLink
                            });
                        }
                    } catch (e) {
                        console.error('Error:', e);
                    }
                });
                
                return products;
            }
            """
            
            basic_products = page.evaluate(js_code)
            
            if not basic_products:
                print("\n⚠️  No products found.")
                page.screenshot(path='debug_screenshot.png')
                return
            
            print(f"✓ Found {len(basic_products)} products")
            print("\n📖 Now visiting each product page for detailed info...")
            print("   (This will take a few minutes)\n")
            
            detailed_products = []
            
            for i, product in enumerate(basic_products, 1):
                print(f"[{i}/{len(basic_products)}] Processing: {product['title'][:50]}...")
                
                try:
                    # Visit the listing page
                    page.goto(product['fullUrl'], wait_until='domcontentloaded', timeout=30000)
                    time.sleep(2.5)  # Give it time to fully load
                    
                    # Extract detailed information with BETTER formatting preservation
                    details = page.evaluate("""() => {
                        const data = {};
                        
                        // IMPROVED DESCRIPTION EXTRACTION
                        const descSelectors = [
                            '[data-product-details-description-text-content]',
                            '[data-id="description-text"]',
                            '.wt-text-body-01.wt-break-word',
                            '.product-description'
                        ];
                        
                        let descElement = null;
                        for (const selector of descSelectors) {
                            descElement = document.querySelector(selector);
                            if (descElement) break;
                        }
                        
                        if (descElement) {
                            let html = descElement.innerHTML;
                            
                            // Convert HTML to text with line breaks
                            html = html.replace(/<br[^>]*>/gi, '\\n');
                            html = html.replace(/<\\/p>/gi, '\\n\\n');
                            html = html.replace(/<p[^>]*>/gi, '');
                            html = html.replace(/<\\/div>/gi, '\\n');
                            html = html.replace(/<div[^>]*>/gi, '');
                            html = html.replace(/<\\/li>/gi, '\\n');
                            html = html.replace(/<li[^>]*>/gi, '• ');
                            html = html.replace(/<\\/h[1-6]>/gi, '\\n');
                            html = html.replace(/<h[1-6][^>]*>/gi, '\\n');
                            html = html.replace(/<[^>]+>/g, '');
                            
                            // Decode HTML entities
                            const textarea = document.createElement('textarea');
                            textarea.innerHTML = html;
                            html = textarea.value;
                            
                            // Clean up whitespace
                            html = html.replace(/\\n\\s*\\n\\s*\\n/g, '\\n\\n');
                            html = html.replace(/[ \\t]+/g, ' ');
                            
                            data.description = html.trim();
                        } else {
                            data.description = '';
                        }
                        
                        // All images
                        const images = [];
                        document.querySelectorAll('img[data-listing-page-image], .listing-page-image img').forEach(img => {
                            let src = img.getAttribute('data-src') || img.src;
                            if (src && src.includes('etsystatic')) {
                                src = src.replace(/il_\\d+x\\d+/g, 'il_1588xN').replace(/il_\\d+xN/g, 'il_1588xN');
                                if (!images.includes(src)) images.push(src);
                            }
                        });
                        data.images = images;
                        
                        // Tags
                        const tags = [];
                        document.querySelectorAll('a[href*="/search?"]').forEach(tag => {
                            const text = tag.textContent.trim();
                            if (text && text.length < 30) tags.push(text);
                        });
                        data.tags = [...new Set(tags)];
                        
                        // Item details
                        const details = {};
                        document.querySelectorAll('.wt-text-caption').forEach(el => {
                            const parent = el.closest('.wt-mb-xs-2');
                            if (parent) {
                                const label = el.textContent.trim();
                                const valueEl = parent.querySelector('.wt-text-body-01');
                                if (valueEl) {
                                    details[label] = valueEl.textContent.trim();
                                }
                            }
                        });
                        data.details = details;
                        
                        // Metadata
                        const metaDesc = document.querySelector('meta[property="og:description"]');
                        data.metaDescription = metaDesc ? metaDesc.content : '';
                        
                        return data;
                    }""")
                    
                    # Merge with basic info
                    enhanced_product = {**product, **details}
                    
                    # Generate URL-friendly slug
                    slug = re.sub(r'[^a-z0-9]+', '-', product['title'].lower()).strip('-')
                    enhanced_product['slug'] = slug
                    
                    # Add share link
                    enhanced_product['shareLink'] = f"https://scribblepatchdesigns.etsy.com/listing/{product['listingId']}?utm_source=scribblepatch&utm_medium=product_page&utm_campaign=direct"
                    
                    # Auto-detect collections
                    collections = []
                    title_lower = product['title'].lower()
                    tags_lower = ' '.join(details.get('tags', [])).lower()
                    combined = title_lower + ' ' + tags_lower
                    
                    if any(word in combined for word in ['kawaii', 'cute', 'adorable']):
                        collections.append('kawaii')
                    if any(word in combined for word in ['christmas', 'holiday', 'elf', 'santa', 'festive']):
                        collections.append('christmas')
                    if any(word in combined for word in ['soccer', 'football', 'golf', 'sport']):
                        collections.append('sports')
                    if any(word in combined for word in ['unicorn', 'fantasy', 'magical']):
                        collections.append('fantasy')
                    if any(word in combined for word in ['cat', 'dog', 'animal', 'pet']):
                        collections.append('animals')
                    if any(word in combined for word in ['kid', 'children', 'child']):
                        collections.append('kids')
                    
                    enhanced_product['collections'] = list(set(collections))
                    
                    detailed_products.append(enhanced_product)
                    
                    # Show what we got
                    desc_preview = enhanced_product.get('description', '')[:100]
                    print(f"   ✓ Got description ({len(enhanced_product.get('description', ''))} chars)")
                    
                except Exception as e:
                    print(f"   ⚠️  Error on this product: {e}")
                    basic_copy = product.copy()
                    basic_copy['slug'] = re.sub(r'[^a-z0-9]+', '-', product['title'].lower()).strip('-')
                    basic_copy['shareLink'] = f"https://scribblepatchdesigns.etsy.com/listing/{product['listingId']}"
                    basic_copy['collections'] = []
                    basic_copy['description'] = ''
                    detailed_products.append(basic_copy)
                
                time.sleep(1.5)
            
            # Save data
            print("\n💾 Saving product data...")
            
            output_data = {
                'scrapedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
                'totalProducts': len(detailed_products),
                'products': detailed_products
            }
            
            with open('products_detailed.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ SUCCESS: Scraped {len(detailed_products)} products with formatted descriptions!")
            print(f"💾 Saved to: products_detailed.json")
            
            # Generate collections
            all_collections = {}
            for product in detailed_products:
                for collection in product.get('collections', []):
                    if collection not in all_collections:
                        all_collections[collection] = []
                    all_collections[collection].append(product['listingId'])
            
            print(f"\n📚 Detected Collections:")
            for collection, listings in sorted(all_collections.items()):
                print(f"   • {collection.title()}: {len(listings)} products")
            
            collections_data = {
                'collections': {
                    name: {
                        'name': name.title(),
                        'slug': name,
                        'productCount': len(ids),
                        'listingIds': ids
                    }
                    for name, ids in all_collections.items()
                }
            }
            
            with open('collections.json', 'w', encoding='utf-8') as f:
                json.dump(collections_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Collections saved to: collections.json")
            
            # Show sample
            if detailed_products:
                sample = detailed_products[0]
                print(f"\n📦 Sample Description Preview:")
                desc = sample.get('description', '')[:300]
                print(f"   {desc}...")
                print(f"\n   Total description length: {len(sample.get('description', ''))} characters")
            
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
    print("ScribblePatch Designs - Enhanced Product Scraper v2")
    print("=" * 70)
    print()
    print("ℹ️  This will:")
    print("   • Visit each product listing page")
    print("   • Extract descriptions WITH formatting preserved")
    print("   • Get images, tags, reviews")
    print("   • Auto-detect collections")
    print()
    print("⏱️  Takes ~2-3 minutes for 10 products")
    print()
    
    scrape_shop("https://www.etsy.com/shop/ScribblePatchDesigns")