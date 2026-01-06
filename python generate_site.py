import json
import os
import re
from pathlib import Path
from datetime import datetime

class SiteGenerator:
    def __init__(self):
        self.products = []
        self.collections = {}
        self.existing_products = set()
        self.new_products = []
        self.updated_collections = []
        
    def load_data(self):
        """Load products and collections from JSON files"""
        print("📥 Loading data from JSON files...")
        
        # Load products
        if os.path.exists('products.json'):
            with open('products.json', 'r', encoding='utf-8') as f:
                self.products = json.load(f)
            print(f"   ✓ Loaded {len(self.products)} products")
        else:
            print("   ✗ products.json not found!")
            return False
            
        # Load collections
        if os.path.exists('collections.json'):
            with open('collections.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.collections = data.get('collections', {})
            print(f"   ✓ Loaded {len(self.collections)} collections")
        else:
            print("   ✗ collections.json not found!")
            return False
            
        return True
    
    def detect_changes(self):
        """Detect which products are new"""
        print("\n🔍 Detecting changes...")
        
        # Check which products already have pages
        products_dir = Path('products')
        if products_dir.exists():
            for html_file in products_dir.glob('*.html'):
                # Extract listing ID from HTML file
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'listing/(\d+)', content)
                    if match:
                        self.existing_products.add(match.group(1))
        
        # Find new products
        for product in self.products:
            if product['listingId'] not in self.existing_products:
                self.new_products.append(product)
        
        print(f"   • Existing products: {len(self.existing_products)}")
        print(f"   • New products: {len(self.new_products)}")
        
        return len(self.new_products) > 0 or len(self.existing_products) == 0
    
    def slugify(self, text):
        """Convert title to URL-friendly slug"""
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    
    def detect_product_collections(self, title):
        """Auto-detect which collections a product belongs to"""
        collections = []
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['kawaii', 'cute']):
            collections.append('kawaii')
        if any(word in title_lower for word in ['christmas', 'holiday', 'elf']):
            collections.append('christmas')
        if any(word in title_lower for word in ['soccer', 'football', 'golf', 'sport']):
            collections.append('sports')
        if any(word in title_lower for word in ['unicorn', 'fantasy']):
            collections.append('fantasy')
        if any(word in title_lower for word in ['cat', 'animal']):
            collections.append('animals')
        if any(word in title_lower for word in ['kid', 'teen', 'children']):
            collections.append('kids')
        
        return list(set(collections))
    
    def generate_product_description(self, product):
        """Generate SEO-friendly description based on product title"""
        title = product['title'].lower()
        
        if 'elf' in title:
            return """Bring the magic of Elf on the Shelf to life with our delightful Christmas coloring pages! This printable activity book features adorable elf characters in festive scenarios perfect for the holiday season. Each page is designed with clean lines and engaging details that kids ages 4-10 will love coloring. Download instantly and print as many times as you need for classroom activities, holiday parties, or quiet time at home. Our high-resolution PDF ensures crisp, clear printing on any home printer. Perfect for parents, teachers, and anyone looking to add creative fun to their Christmas celebrations."""
        
        elif 'soccer' in title or 'football' in title:
            return """Score big with our exciting soccer coloring pages! Perfect for young football fans and aspiring athletes, this printable activity book features dynamic soccer scenes, players in action, and fun football-themed designs. Whether your child plays in a youth league or just loves the beautiful game, these coloring pages provide hours of entertaining, screen-free fun. Ideal for ages 5-12, each design balances detail with accessibility. Great for team parties, birthday celebrations, or rainy day activities. Download instantly and print unlimited copies on any home printer."""
        
        elif 'unicorn' in title:
            return """Enter a world of magic with our enchanting unicorn coloring pages! This fantasy-themed printable book features beautiful unicorns, rainbows, stars, and whimsical scenes that spark imagination. Perfect for kids and girls who love magical creatures, each page offers the right balance of detail for engaging coloring without overwhelming younger artists. From majestic unicorns prancing through clouds to cute kawaii-style designs, there's something for every unicorn enthusiast. Instant PDF download means the magic starts immediately! Works beautifully with colored pencils, markers, or crayons."""
        
        elif 'golf' in title:
            return """Tee up some creative fun with our golf coloring pages! Designed for junior golfers, golf-loving families, and young sports enthusiasts, this printable activity book features golf courses, players, equipment, and fun golf scenes. Whether your child is learning the game or already competing in junior tournaments, these pages celebrate their passion for golf. Each design is crafted to be engaging for kids ages 6-14, with clear lines perfect for colored pencils, markers, or crayons. A hole-in-one gift for any young golfer! Download instantly and print unlimited times."""
        
        elif 'animals at work' in title or 'cute animals at work' in title:
            return """Discover the adorable world of working animals with our kawaii coloring pages! This charming collection features cute animals in various professions - from doctor cats to chef bears and firefighter dogs. Each page showcases the beloved kawaii art style with big eyes, sweet expressions, and delightful details. Perfect for kids and teens ages 5-15 who love cute characters and imaginative scenarios. These pages inspire creativity while introducing different careers in a fun, accessible way. Instant digital download delivers instant smiles! Print as many copies as you need."""
        
        elif 'christmas' in title and 'kawaii' in title:
            return """Combine the joy of Christmas with irresistibly cute kawaii animals! This festive coloring book features adorable animals celebrating the holiday season - think Santa bears, reindeer cats, and penguin elves. The kawaii style makes these Christmas scenes extra special with its characteristic charm and sweetness. Perfect for kids ages 4-12, these pages work wonderfully for advent calendar activities, holiday classroom projects, or cozy winter coloring sessions. Our Christmas kawaii designs bring double the joy - festive cheer meets adorable cuteness! Download instantly and print unlimited times at home."""
        
        elif 'spooky' in title or 'cats' in title:
            return """Get ready for some adorably spooky fun with our kawaii cats coloring pages! These aren't scary - they're cute cats with a gentle Halloween or mysterious twist. Think cats in witch hats, mystical feline friends, and playful spooky scenes perfect for kids who love cats and a touch of magic. The kawaii style keeps everything friendly and fun while adding just enough spookiness to be exciting. Great for Halloween, fall activities, or year-round for cat-loving kids ages 5-13. Instant PDF download, print unlimited times on any home printer."""
        
        else:
            return """High-quality printable coloring pages delivered as an instant PDF download. Perfect for creative fun at home, classroom activities, or thoughtful handmade gifts. Each page features carefully designed artwork with clean lines optimized for all skill levels. Download once and print unlimited copies on your home printer whenever you need them! Works beautifully with colored pencils, markers, crayons, or gel pens. Instant download means no waiting - start coloring within minutes of purchase."""
    
    def generate_product_page(self, product):
        """Generate individual product HTML page"""
        slug = self.slugify(product['title'])
        collections = self.detect_product_collections(product['title'])
        description = self.generate_product_description(product)
        
        # Get related products (same collections, exclude current)
        related = [p for p in self.products 
                   if p['listingId'] != product['listingId'] 
                   and any(c in self.detect_product_collections(p['title']) for c in collections)][:3]
        
        # Build collection tags HTML
        collection_tags = ''.join([
            f'<a href="../collections/{c}.html" class="collection-tag">#{c.title()}</a>'
            for c in collections
        ]) if collections else ''
        
        # Build related products HTML
        related_html = ''
        if related:
            related_html = '<div class="related-products"><h2>You Might Also Like</h2><div class="related-grid">'
            for r in related:
                r_slug = self.slugify(r['title'])
                related_html += f'''
                    <a href="{r_slug}.html" class="related-card">
                        <img src="{r['image']}" alt="{r['title']}" loading="lazy">
                        <div class="related-card-info">
                            <div class="related-card-title">{r['title']}</div>
                            <div class="related-card-price">{r['price']}</div>
                        </div>
                    </a>'''
            related_html += '</div></div>'
        
        # Primary collection for breadcrumb
        primary_collection = collections[0] if collections else 'all'
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{product['title'][:150]} - Instant PDF download from {product['price']}. High-quality printable coloring pages. Print unlimited times at home.">
    
    <title>{product['title'][:60]} | Scribble Patch Designs</title>
    <link rel="icon" type="image/png" href="../favicon.png">
    <link rel="canonical" href="https://www.scribblepatchdesigns.com/products/{slug}.html">
    
    <meta property="og:title" content="{product['title']}">
    <meta property="og:description" content="Instant PDF coloring pages from {product['price']}. Download and print at home.">
    <meta property="og:image" content="{product['image']}">
    <meta property="og:type" content="product">
    
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "{product['title']}",
      "image": "{product['image']}",
      "description": "{description[:200].replace('"', '&quot;')}...",
      "brand": {{
        "@type": "Brand",
        "name": "Scribble Patch Designs"
      }},
      "offers": {{
        "@type": "Offer",
        "price": "{product['price'].replace('£', '')}",
        "priceCurrency": "GBP",
        "availability": "https://schema.org/InStock",
        "url": "{product['link']}"
      }}
    }}
    </script>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500&family=Poppins:wght@300;400;500;600&display=swap');
        
        :root {{
            --primary: #2d3748;
            --accent: #667eea;
            --accent-hover: #5a67d8;
            --bg: #ffffff;
            --border: #e2e8f0;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            line-height: 1.7;
            color: var(--primary);
            background: var(--bg);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        nav {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--border);
        }}

        .nav-wrapper {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .nav-logo {{
            font-family: 'Fredoka', sans-serif;
            font-size: 1.25rem;
            color: var(--primary);
            text-decoration: none;
        }}

        .nav-links {{
            display: flex;
            gap: 2rem;
        }}

        .nav-links a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}

        .nav-links a:hover {{ color: var(--accent); }}

        .breadcrumbs {{
            padding: 1.5rem 0;
            font-size: 0.9rem;
            color: #718096;
        }}

        .breadcrumbs a {{
            color: var(--accent);
            text-decoration: none;
        }}

        .breadcrumbs a:hover {{ text-decoration: underline; }}

        .product-page {{
            padding: 2rem 0 4rem;
        }}

        .product-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            margin-bottom: 4rem;
        }}

        .product-image {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: #f7fafc;
        }}

        .product-info h1 {{
            font-size: 2rem;
            margin-bottom: 1rem;
            font-weight: 600;
            line-height: 1.3;
        }}

        .price {{
            font-size: 1.75rem;
            color: var(--accent);
            font-weight: 600;
            margin-bottom: 1.5rem;
        }}

        .collections {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }}

        .collection-tag {{
            background: #edf2f7;
            padding: 0.4rem 0.9rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: var(--primary);
            text-decoration: none;
            transition: background 0.2s;
        }}

        .collection-tag:hover {{
            background: #e2e8f0;
        }}

        .description {{
            margin: 2rem 0;
            line-height: 1.8;
            color: #4a5568;
        }}

        .features {{
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 2rem 0;
        }}

        .features h3 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }}

        .features ul {{
            margin-left: 1.5rem;
            color: #4a5568;
        }}

        .features li {{
            margin-bottom: 0.5rem;
        }}

        .cta-button {{
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 1rem 2.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: background 0.2s;
            margin-top: 1rem;
        }}

        .cta-button:hover {{
            background: var(--accent-hover);
        }}

        .faq {{
            margin-top: 3rem;
            padding-top: 3rem;
            border-top: 1px solid var(--border);
        }}

        .faq h2 {{
            font-size: 1.75rem;
            margin-bottom: 2rem;
            font-weight: 600;
        }}

        .faq-item {{
            margin-bottom: 2rem;
        }}

        .faq-item h3 {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}

        .faq-item p {{
            color: #4a5568;
            line-height: 1.7;
        }}

        .related-products {{
            margin-top: 4rem;
            padding-top: 4rem;
            border-top: 1px solid var(--border);
        }}

        .related-products h2 {{
            font-size: 1.75rem;
            margin-bottom: 2rem;
            font-weight: 600;
        }}

        .related-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
        }}

        .related-card {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .related-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.08);
        }}

        .related-card img {{
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
        }}

        .related-card-info {{
            padding: 1rem;
        }}

        .related-card-title {{
            font-weight: 600;
            font-size: 0.95rem;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }}

        .related-card-price {{
            color: var(--accent);
            font-weight: 600;
        }}

        footer {{
            background: white;
            border-top: 1px solid var(--border);
            padding: 2rem 0;
            text-align: center;
            font-size: 0.9rem;
            color: #718096;
        }}

        @media (max-width: 768px) {{
            .product-grid {{
                grid-template-columns: 1fr;
                gap: 2rem;
            }}
            .product-info h1 {{ font-size: 1.5rem; }}
            .related-grid {{ grid-template-columns: 1fr; }}
            .nav-links {{ display: none; }}
        }}
    </style>
</head>
<body>

    <nav>
        <div class="container nav-wrapper">
            <a href="../index.html" class="nav-logo">Scribble Patch Designs</a>
            <div class="nav-links">
                <a href="../index.html#products">Products</a>
                <a href="all.html">Collections</a>
                <a href="https://www.etsy.com/shop/ScribblePatchDesigns" target="_blank" rel="noopener">Etsy Store</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="breadcrumbs">
            <a href="../index.html">Home</a> / <a href="all.html">Collections</a> / {collection_info['name']}
        </div>

        <div class="collection-header">
            <h1>{collection_info['name']} Coloring Pages</h1>
            <p>{descriptions.get(collection_key, 'Beautiful coloring pages perfect for creative fun.')}</p>
            <div class="product-count">{collection_info['productCount']} products</div>
        </div>

        <div class="product-grid">{products_html}</div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2026 Scribble Patch Designs. Created with ♥ for the creative community.</p>
        </div>
    </footer>

</body>
</html>'''
        
        return html
    
    def generate_all_products_page(self):
        """Generate 'All Products' collection page"""
        # Build product grid
        products_html = ''
        for p in self.products:
            slug = self.slugify(p['title'])
            products_html += f'''
                <a href="../products/{slug}.html" class="product-card">
                    <img src="{p['image']}" alt="{p['title']}" class="product-image" loading="lazy">
                    <div class="product-info">
                        <div class="product-title">{p['title']}</div>
                        <div class="product-price">{p['price']}</div>
                    </div>
                </a>'''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Browse all {len(self.products)} Scribble Patch Designs coloring pages. Kawaii animals, Christmas themes, sports, fantasy and more. Instant PDF downloads from £1.44.">
    <title>All Coloring Pages | Scribble Patch Designs</title>
    <link rel="icon" type="image/png" href="../favicon.png">
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500&family=Poppins:wght@300;400;500;600&display=swap');
        
        :root {{
            --primary: #2d3748;
            --accent: #667eea;
            --bg: #ffffff;
            --border: #e2e8f0;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Poppins', sans-serif; color: var(--primary); background: var(--bg); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}

        nav {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--border);
        }}

        .nav-wrapper {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav-logo {{ font-family: 'Fredoka', sans-serif; font-size: 1.25rem; color: var(--primary); text-decoration: none; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ color: var(--primary); text-decoration: none; font-weight: 500; font-size: 0.9rem; }}
        .nav-links a:hover {{ color: var(--accent); }}

        .page-header {{ text-align: center; padding: 3rem 0; }}
        .page-header h1 {{ font-family: 'Fredoka', sans-serif; font-size: 2.5rem; margin-bottom: 1rem; }}
        .page-header p {{ font-size: 1.1rem; color: #4a5568; }}

        .collections-nav {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin: 2rem 0;
        }}

        .collections-nav a {{
            background: #edf2f7;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            text-decoration: none;
            color: var(--primary);
            font-weight: 500;
            transition: all 0.2s;
        }}

        .collections-nav a:hover {{
            background: var(--accent);
            color: white;
        }}

        .product-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            padding: 2rem 0 4rem;
        }}

        .product-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.08); }}
        .product-image {{ width: 100%; aspect-ratio: 1; object-fit: cover; }}
        .product-info {{ padding: 1.25rem; }}
        .product-title {{
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.75rem;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .product-price {{ color: var(--accent); font-weight: 600; font-size: 1.1rem; }}

        footer {{
            background: white;
            border-top: 1px solid var(--border);
            padding: 2rem 0;
            text-align: center;
            font-size: 0.9rem;
            color: #718096;
        }}

        @media (max-width: 768px) {{
            .page-header h1 {{ font-size: 2rem; }}
            .product-grid {{ grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
            .nav-links {{ display: none; }}
        }}
    </style>
</head>
<body>

    <nav>
        <div class="container nav-wrapper">
            <a href="../index.html" class="nav-logo">Scribble Patch Designs</a>
            <div class="nav-links">
                <a href="../index.html#products">Products</a>
                <a href="all.html">Collections</a>
                <a href="https://www.etsy.com/shop/ScribblePatchDesigns" target="_blank" rel="noopener">Etsy Store</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="page-header">
            <h1>All Coloring Pages</h1>
            <p>Browse our complete collection of {len(self.products)} printable coloring pages</p>
        </div>

        <div class="collections-nav">
            {''.join([f'<a href="{k}.html">{v["name"]}</a>' for k, v in self.collections.items()])}
        </div>

        <div class="product-grid">{products_html}</div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2026 Scribble Patch Designs. Created with ♥ for the creative community.</p>
        </div>
    </footer>

</body>
</html>'''
        
        return html
    
    def save_pages(self):
        """Generate and save all necessary pages"""
        print("\n📝 Generating pages...\n")
        
        # Create directories
        Path('products').mkdir(exist_ok=True)
        Path('collections').mkdir(exist_ok=True)
        
        # Generate product pages (only new ones if detecting changes)
        products_to_generate = self.new_products if self.new_products else self.products
        
        for i, product in enumerate(products_to_generate, 1):
            slug, html = self.generate_product_page(product)
            filepath = Path('products') / f'{slug}.html'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            status = "🆕" if product in self.new_products else "✓"
            print(f"   {status} products/{slug}.html")
        
        # Generate collection pages
        print()
        for collection_key, collection_info in self.collections.items():
            html = self.generate_collection_page(collection_key, collection_info)
            filepath = Path('collections') / f'{collection_key}.html'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"   ✓ collections/{collection_key}.html")
        
        # Generate "All Products" page
        html = self.generate_all_products_page()
        with open('collections/all.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✓ collections/all.html")
        
        # Save generation log
        log = {
            'generated_at': datetime.now().isoformat(),
            'total_products': len(self.products),
            'new_products': len(self.new_products),
            'collections': len(self.collections),
            'new_product_ids': [p['listingId'] for p in self.new_products]
        }
        
        with open('generation_log.json', 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)
    
    def run(self):
        """Main execution flow"""
        print("="*60)
        print("🎨 Scribble Patch Designs - Smart Site Generator")
        print("="*60)
        
        if not self.load_data():
            print("\n❌ Failed to load data. Make sure products.json and collections.json exist.")
            return
        
        has_changes = self.detect_changes()
        
        if not has_changes and len(self.existing_products) > 0:
            print("\n✨ No new products detected. Site is up to date!")
            print("   Run the Etsy scraper if you've added new products.")
            return
        
        self.save_pages()
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Site generated successfully")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Total products: {len(self.products)}")
        print(f"   • New products: {len(self.new_products)}")
        print(f"   • Collections: {len(self.collections)}")
        print(f"\n📁 Files created:")
        print(f"   • products/*.html ({len(self.new_products) if self.new_products else len(self.products)} files)")
        print(f"   • collections/*.html ({len(self.collections) + 1} files)")
        print(f"\n🚀 Next steps:")
        print(f"   1. Upload the products/ and collections/ folders to your website")
        print(f"   2. Update your index.html to link to these pages")
        print(f"   3. Test the site locally before deploying")
        
        if self.new_products:
            print(f"\n🆕 New products added:")
            for p in self.new_products:
                print(f"   • {p['title'][:60]}...")


if __name__ == "__main__":
    generator = SiteGenerator()
    generator.run()
        <div class="container nav-wrapper">
            <a href="../index.html" class="nav-logo">Scribble Patch Designs</a>
            <div class="nav-links">
                <a href="../index.html#products">Products</a>
                <a href="../collections/{primary_collection}.html">Collections</a>
                <a href="https://www.etsy.com/shop/ScribblePatchDesigns" target="_blank" rel="noopener">Etsy Store</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="breadcrumbs">
            <a href="../index.html">Home</a> / <a href="../collections/{primary_collection}.html">{primary_collection.title()}</a> / {product['title'][:50]}...
        </div>

        <div class="product-page">
            <div class="product-grid">
                <div>
                    <img src="{product['image']}" alt="{product['title']}" class="product-image" loading="eager">
                </div>

                <div class="product-info">
                    <h1>{product['title']}</h1>
                    
                    <div class="price">{product['price']}</div>

                    <div class="collections">{collection_tags}</div>

                    <div class="description">
                        <p>{description}</p>
                    </div>

                    <div class="features">
                        <h3>✨ What's Included</h3>
                        <ul>
                            <li>High-resolution PDF file optimized for home printing</li>
                            <li>Instant digital download - no shipping, no waiting</li>
                            <li>Print unlimited copies for personal use</li>
                            <li>Compatible with any home printer</li>
                            <li>Works great with colored pencils, markers, or crayons</li>
                        </ul>
                    </div>

                    <a href="{product['link']}" class="cta-button" target="_blank" rel="noopener">
                        Buy on Etsy - {product['price']} →
                    </a>

                    <p style="font-size: 0.85rem; color: #718096; margin-top: 1rem;">
                        ✓ Secure checkout via Etsy<br>
                        ✓ Instant download after purchase<br>
                        ✓ Print unlimited times for personal use
                    </p>
                </div>
            </div>

            <div class="faq">
                <h2>Frequently Asked Questions</h2>
                
                <div class="faq-item">
                    <h3>What format is the download?</h3>
                    <p>You'll receive a high-resolution PDF file that's optimized for printing on standard home printers. The PDF works on all devices and can be opened with any PDF reader.</p>
                </div>

                <div class="faq-item">
                    <h3>How many times can I print these coloring pages?</h3>
                    <p>You can print unlimited copies for personal use! Print them for your kids, classroom, parties, or any personal activity.</p>
                </div>

                <div class="faq-item">
                    <h3>What supplies do I need?</h3>
                    <p>These coloring pages work beautifully with colored pencils, crayons, markers, or gel pens. We recommend printing on standard printer paper (80-100 GSM) or cardstock for a sturdier finish.</p>
                </div>

                <div class="faq-item">
                    <h3>How do I receive my download?</h3>
                    <p>After completing your purchase on Etsy, you'll receive an instant download link. Simply click the link to download your PDF file, then print at home whenever you're ready!</p>
                </div>
            </div>

            {related_html}
        </div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2026 Scribble Patch Designs. Created with ♥ for the creative community.</p>
        </div>
    </footer>

</body>
</html>'''
        
        return slug, html
    
    def generate_collection_page(self, collection_key, collection_info):
        """Generate collection page HTML"""
        collection_products = [p for p in self.products 
                              if p['listingId'] in collection_info['listingIds']]
        
        descriptions = {
            'kawaii': 'Adorable kawaii-style coloring pages featuring cute characters with big eyes and sweet expressions. Perfect for fans of Japanese cute culture and charming artwork.',
            'christmas': 'Festive Christmas and holiday coloring pages to celebrate the season. From Santa to elves, bring holiday cheer to your coloring sessions.',
            'sports': 'Action-packed sports coloring pages for young athletes and sports enthusiasts. Soccer, golf, and more athletic themes to inspire active kids.',
            'fantasy': 'Magical fantasy coloring pages featuring unicorns, mythical creatures, and enchanted scenes. Let imagination soar with these whimsical designs.',
            'animals': 'Delightful animal coloring pages featuring cats, dogs, and adorable creatures in fun scenarios. Perfect for animal lovers of all ages.',
            'kids': 'Kid-friendly coloring pages designed specifically for children. Age-appropriate themes and designs that engage young artists.'
        }
        
        # Build product grid HTML
        products_html = ''
        for p in collection_products:
            slug = self.slugify(p['title'])
            products_html += f'''
                <a href="../products/{slug}.html" class="product-card">
                    <img src="{p['image']}" alt="{p['title']}" class="product-image" loading="lazy">
                    <div class="product-info">
                        <div class="product-title">{p['title']}</div>
                        <div class="product-price">{p['price']}</div>
                    </div>
                </a>'''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{collection_info['name']} coloring pages - {collection_info['productCount']} printable PDF designs. Instant download from £1.44. High-quality coloring books for kids and adults.">
    
    <title>{collection_info['name']} Coloring Pages | Scribble Patch Designs</title>
    <link rel="icon" type="image/png" href="../favicon.png">
    <link rel="canonical" href="https://www.scribblepatchdesigns.com/collections/{collection_key}.html">
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500&family=Poppins:wght@300;400;500;600&display=swap');
        
        :root {{
            --primary: #2d3748;
            --accent: #667eea;
            --bg: #ffffff;
            --border: #e2e8f0;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            line-height: 1.7;
            color: var(--primary);
            background: var(--bg);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        nav {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--border);
        }}

        .nav-wrapper {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .nav-logo {{
            font-family: 'Fredoka', sans-serif;
            font-size: 1.25rem;
            color: var(--primary);
            text-decoration: none;
        }}

        .nav-links {{
            display: flex;
            gap: 2rem;
        }}

        .nav-links a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}

        .nav-links a:hover {{ color: var(--accent); }}

        .breadcrumbs {{
            padding: 1.5rem 0;
            font-size: 0.9rem;
            color: #718096;
        }}

        .breadcrumbs a {{
            color: var(--accent);
            text-decoration: none;
        }}

        .collection-header {{
            text-align: center;
            padding: 3rem 0;
        }}

        .collection-header h1 {{
            font-family: 'Fredoka', sans-serif;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}

        .collection-header p {{
            font-size: 1.1rem;
            color: #4a5568;
            max-width: 700px;
            margin: 0 auto;
        }}

        .product-count {{
            font-size: 0.9rem;
            color: #718096;
            margin-top: 0.5rem;
        }}

        .product-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            padding: 2rem 0 4rem;
        }}

        .product-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.08);
        }}

        .product-image {{
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
        }}

        .product-info {{
            padding: 1.25rem;
        }}

        .product-title {{
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.75rem;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .product-price {{
            color: var(--accent);
            font-weight: 600;
            font-size: 1.1rem;
        }}

        footer {{
            background: white;
            border-top: 1px solid var(--border);
            padding: 2rem 0;
            text-align: center;
            font-size: 0.9rem;
            color: #718096;
        }}

        @media (max-width: 768px) {{
            .collection-header h1 {{ font-size: 2rem; }}
            .product-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
            }}
            .nav-links {{ display: none; }}
        }}
    </style>
</head>
<body>

    <nav>