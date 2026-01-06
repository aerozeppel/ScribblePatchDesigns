import json
import os
import shutil
from pathlib import Path

# Configuration
OUTPUT_DIR = "_site"
PRODUCTS_JSON = "products_detailed.json"
COLLECTIONS_JSON = "collections.json"

# --- HTML TEMPLATES ---

# 1. Common Head & Styles (Shared across all pages)
def get_head(title, description, url, image):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{title} | Scribble Patch Designs</title>
    <link rel="icon" type="image/png" href="/favicon.png">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="website">
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500&family=Poppins:wght@300;400;500;600&display=swap');
        
        :root {{
            --primary: #2d3748;
            --accent: #667eea;
            --accent-hover: #5a67d8;
            --bg-color: #ffffff;
            --bg-secondary: #f7fafc;
            --border: #e2e8f0;
            --soft-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        }}

        html {{ scroll-behavior: smooth; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            line-height: 1.7;
            color: var(--primary);
            background-color: var(--bg-color);
            background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
            background-size: 24px 24px;
        }}
        
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}
        img {{ max-width: 100%; display: block; }}

        /* Navigation */
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
        .nav-links a {{ color: var(--primary); text-decoration: none; font-weight: 500; transition: color 0.2s; }}
        .nav-links a:hover {{ color: var(--accent); }}

        /* Product Grids */
        .product-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        .product-card {{
            background: white; border-radius: 12px; overflow: hidden; border: 1px solid var(--border);
            text-decoration: none; color: inherit; transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex; flex-direction: column; text-align: left;
        }}
        .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.08); }}
        .product-image {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; background: #f1f5f9; }}
        .product-info {{ padding: 1.25rem; flex-grow: 1; }}
        .product-title {{ font-weight: 600; font-size: 1rem; margin-bottom: 0.75rem; line-height: 1.4; }}
        .product-footer {{ display: flex; justify-content: flex-end; align-items: center; margin-top: auto; }}
        .buy-link {{ font-size: 0.875rem; font-weight: 600; color: var(--accent); }}

        /* Footer */
        footer {{ background: white; border-top: 1px solid var(--border); padding: 2rem 0; text-align: center; margin-top: 4rem; color: #718096; }}

        /* --- Page Specific Styles --- */
        
        /* Product Details */
        .breadcrumb {{ margin: 2rem 0; font-size: 0.9rem; color: #718096; }}
        .breadcrumb a {{ color: var(--accent); text-decoration: none; }}
        
        .product-detail-wrapper {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; padding-bottom: 4rem; }}
        .gallery-main {{ width: 100%; border-radius: 16px; margin-bottom: 1rem; border: 1px solid var(--border); }}
        .gallery-thumbs {{ display: flex; gap: 10px; overflow-x: auto; padding-bottom: 5px; }}
        .gallery-thumb {{ width: 80px; height: 80px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 2px solid transparent; transition: all 0.2s; }}
        .gallery-thumb:hover, .gallery-thumb.active {{ border-color: var(--accent); opacity: 0.8; }}
        
        .pd-title {{ font-family: 'Fredoka', sans-serif; font-size: 2.5rem; line-height: 1.2; margin-bottom: 1rem; }}
        .pd-price {{ font-size: 1.5rem; color: var(--accent); font-weight: 600; margin-bottom: 2rem; }}
        .pd-desc {{ white-space: pre-wrap; color: #4a5568; margin-bottom: 2rem; }}
        .btn-primary {{
            background: var(--accent); color: white; padding: 1rem 2rem; border-radius: 8px;
            text-decoration: none; font-weight: 600; display: inline-block; transition: background 0.2s;
            text-align: center; width: 100%;
        }}
        .btn-primary:hover {{ background: var(--accent-hover); }}

        /* Collection Header */
        .collection-header {{ padding: 4rem 0; text-align: center; }}
        .collection-header h1 {{ font-family: 'Fredoka', sans-serif; font-size: 3rem; margin-bottom: 1rem; }}

        @media (max-width: 768px) {{
            .product-detail-wrapper {{ grid-template-columns: 1fr; gap: 2rem; }}
            .pd-title {{ font-size: 2rem; }}
            .nav-links {{ display: none; }} /* Simplified mobile nav for this script */
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container nav-wrapper">
            <a href="/" class="nav-logo">Scribble Patch Designs</a>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/#products">All Products</a>
                <a href="https://www.etsy.com/shop/ScribblePatchDesigns" target="_blank">Etsy Store</a>
            </div>
        </div>
    </nav>
"""

def get_footer():
    return """
    <footer>
        <div class="container">
            <p>&copy; 2026 Scribble Patch Designs. Created with ♥ for the creative community.</p>
        </div>
    </footer>
</body>
</html>
"""

# 2. Product Card HTML Generator
def generate_product_card(product):
    # Determine the link
    link = f"/products/{product['slug']}.html"
    
    # Get first image safely
    img_src = product['images'][0] if product.get('images') and len(product['images']) > 0 else 'https://placehold.co/400?text=No+Image'
    
    return f"""
    <a href="{link}" class="product-card">
        <img src="{img_src}" alt="{product['title']}" class="product-image" loading="lazy">
        <div class="product-info">
            <div class="product-title">{product['title']}</div>
            <div class="product-footer">
                <span class="buy-link">View Details →</span>
            </div>
        </div>
    </a>
    """

# --- BUILD FUNCTIONS ---

def build_product_page(product, all_products):
    """Generates a single product detail page."""
    
    filename = f"{OUTPUT_DIR}/products/{product['slug']}.html"
    
    # Images HTML - Safely handle empty images
    images = product.get('images', [])
    if images:
        main_img = images[0]
        thumbs_html = ""
        for i, img in enumerate(images):
            active_class = "active" if i == 0 else ""
            thumbs_html += f'<img src="{img}" class="gallery-thumb {active_class}" onclick="switchImage(this, \'{img}\')">'
    else:
        main_img = "https://placehold.co/600?text=No+Image"
        thumbs_html = ""

    # Clean description (basic formatting)
    desc_html = product.get('description', '').replace('\n', '<br>')

    html = get_head(
        title=product['title'],
        description=product.get('metaDescription') or product['title'],
        url=f"https://www.scribblepatchdesigns.com/products/{product['slug']}",
        image=main_img
    )
    
    html += f"""
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> > <a href="/#products">Products</a> > {product['title']}
        </div>

        <div class="product-detail-wrapper">
            <!-- Left: Gallery -->
            <div class="gallery-section">
                <img src="{main_img}" id="mainImage" class="gallery-main" alt="{product['title']}">
                <div class="gallery-thumbs">
                    {thumbs_html}
                </div>
            </div>

            <!-- Right: Info -->
            <div class="info-section">
                <h1 class="pd-title">{product['title']}</h1>
                <div class="pd-price">{product.get('price', '')}</div>
                
                <a href="{product.get('shareLink', '#')}" target="_blank" class="btn-primary">
                    Buy Instant Download on Etsy
                </a>
                
                <div style="margin-top: 2rem; padding: 1.5rem; background: var(--bg-secondary); border-radius: 12px;">
                    <strong>✨ Instant Digital Download</strong>
                    <ul style="margin-left: 1.5rem; margin-top: 0.5rem; font-size: 0.95rem; color: #4a5568;">
                        <li>High-resolution PDF files</li>
                        <li>Print at home immediately</li>
                        <li>No shipping fees</li>
                    </ul>
                </div>

                <h3 style="margin: 2rem 0 1rem;">Description</h3>
                <div class="pd-desc">{desc_html}</div>
            </div>
        </div>
    </div>

    <script>
        function switchImage(thumb, src) {{
            document.getElementById('mainImage').src = src;
            document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
        }}
    </script>
    """
    
    html += get_footer()
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Created Product Page: {product['slug']}")

def build_collection_page(collection_name, product_ids, all_products):
    """Generates a collection page."""
    slug = collection_name.lower().replace(" ", "-")
    filename = f"{OUTPUT_DIR}/collections/{slug}.html"
    
    # Filter products belonging to this collection
    collection_products = [p for p in all_products if p['listingId'] in product_ids]
    
    if not collection_products:
        return

    # Generate Grid
    grid_html = '<div class="product-grid">'
    for p in collection_products:
        grid_html += generate_product_card(p)
    grid_html += '</div>'

    # Safe image check for header
    first_product = collection_products[0]
    header_image = first_product['images'][0] if first_product.get('images') and len(first_product['images']) > 0 else ""

    html = get_head(
        title=f"{collection_name.title()} Coloring Pages",
        description=f"Browse our collection of {collection_name} coloring pages.",
        url=f"https://www.scribblepatchdesigns.com/collections/{slug}",
        image=header_image
    )

    html += f"""
    <div class="collection-header">
        <div class="container">
            <span style="text-transform: uppercase; letter-spacing: 2px; color: var(--accent); font-weight: 600;">Collection</span>
            <h1>{collection_name.title()} Coloring Pages</h1>
            <p>Explore our unique printable designs.</p>
        </div>
    </div>
    
    <div class="container">
        {grid_html}
    </div>
    """
    
    html += get_footer()
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Created Collection Page: {slug}")

def build_home_page(products, collections_data):
    """Rebuilds the index.html using the User's exact design but with local links."""
    
    # 1. Generate the Collection Buttons (To place in the Hero)
    coll_html = '<div style="display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; margin-top: 1.5rem;">'
    for name in collections_data.keys():
        slug = name.lower().replace(" ", "-")
        # Link to local collection page
        coll_html += f'<a href="collections/{slug}.html" class="btn-outline" style="color: var(--primary); border-color: var(--border); font-size: 0.8rem;">{name.title()}</a>'
    coll_html += '</div>'

    # 2. Generate the Product Grid (With local links)
    grid_html = ""
    # We use the top 8 products for the home page
    for p in products[:8]:
        # Logic to find a valid image
        img_src = p['images'][0] if p.get('images') else 'https://placehold.co/600?text=No+Image'
        
        # LINK TO LOCAL PAGE (This is the key change)
        link = f"products/{p['slug']}.html"
        
        grid_html += f"""
        <a href="{link}" class="product-card">
            <img src="{img_src}" alt="{p['title']}" class="product-image" loading="lazy">
            <div class="product-info">
                <div class="product-title">{p['title']}</div>
                <div class="product-footer">
                    <span class="buy-link">View Details →</span>
                </div>
            </div>
        </a>
        """

    # 3. The HTML Template (Your specific design)
    # Note: I replaced the hardcoded grid with {grid_html} and added {coll_html}
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Instant PDF coloring pages from £1.44! Premium printable designs for adults & kids.">
    <title>Premium Printable Coloring Pages | Scribble Patch Designs</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500&family=Poppins:wght@300;400;500;600&display=swap');
        :root {{ --primary: #2d3748; --accent: #667eea; --accent-hover: #5a67d8; --bg-color: #ffffff; --bg-secondary: #f7fafc; --border: #e2e8f0; --soft-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); }}
        html {{ scroll-behavior: smooth; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Poppins', sans-serif; line-height: 1.7; color: var(--primary); background-color: var(--bg-color); background-image: radial-gradient(#e2e8f0 1px, transparent 1px); background-size: 24px 24px; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}
        nav {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(8px); padding: 1rem 0; position: sticky; top: 0; z-index: 1000; border-bottom: 1px solid var(--border); }}
        .nav-wrapper {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav-logo {{ font-family: 'Fredoka', sans-serif; font-size: 1.25rem; color: var(--primary); text-decoration: none; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ color: var(--primary); text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: color 0.2s; }}
        .nav-links a:hover {{ color: var(--accent); }}
        .hero {{ padding: 4rem 0 2rem; text-align: center; }}
        .hero h1 {{ font-family: 'Fredoka', sans-serif; font-size: 2.75rem; line-height: 1.2; margin-bottom: 1rem; letter-spacing: -1px; }}
        .hero p {{ font-size: 1.125rem; color: #4a5568; max-width: 650px; margin: 0 auto 1.5rem; }}
        .eyebrow {{ text-transform: uppercase; font-size: 0.85rem; font-weight: 600; letter-spacing: 2px; color: var(--accent); display: block; margin-bottom: 1rem; }}
        
        /* Grid Styles */
        .product-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; margin-top: 2rem; }}
        .product-card {{ background: white; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); text-decoration: none; color: inherit; transition: transform 0.3s ease, box-shadow 0.3s ease; display: flex; flex-direction: column; text-align: left; }}
        .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.08); }}
        .product-image {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; background: #f1f5f9; }}
        .product-info {{ padding: 1.25rem; flex-grow: 1; }}
        .product-title {{ font-weight: 600; font-size: 1rem; margin-bottom: 0.75rem; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        .product-footer {{ display: flex; justify-content: flex-end; align-items: center; }}
        .buy-link {{ font-size: 0.875rem; font-weight: 600; color: var(--accent); }}
        
        /* Button Styles */
        .btn-outline {{ display: inline-block; background: transparent; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 500; border: 1px solid; transition: all 0.2s; }}
        .btn-outline:hover {{ background: rgba(0,0,0,0.05); }}

        footer {{ background: white; border-top: 1px solid var(--border); padding: 2rem 0; text-align: center; font-size: 0.9rem; color: #718096; margin-top: 4rem; }}
        
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2rem; }}
            .nav-links {{ display: none; }}
            .product-grid {{ grid-template-columns: repeat(2, 1fr); gap: 0.5rem; }}
        }}
    </style>
</head>
<body>

    <nav>
        <div class="container nav-wrapper">
            <a href="index.html" class="nav-logo">Scribble Patch Designs</a>
            <div class="nav-links">
                <a href="#products">Products</a>
                <a href="#about">About</a>
                <a href="https://www.etsy.com/shop/ScribblePatchDesigns" target="_blank">Etsy Store</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <div class="container">
            <div class="hero-text-content">
                <span class="eyebrow">Instant Digital Downloads</span>
                <h1>Premium Printable Coloring Pages</h1>
                <p>High-quality PDF coloring pages from £1.44. Instant download, print at home. Featuring Kawaii animals, Christmas themes, Sports, and Fantasy designs.</p>
                
                <!-- DYNAMIC COLLECTION BUTTONS INSERTED HERE -->
                {coll_html}
            </div>
        </div>
    </header>

    <div class="container">
        <h2 id="products" style="font-size: 1.75rem; margin-bottom: 1rem; font-weight: 600; text-align:center;">Our Coloring Page Collection</h2>

        <!-- DYNAMIC PRODUCT GRID INSERTED HERE -->
        <div class="product-grid">
            {grid_html}
        </div>
    </div>
    
    <section id="about" style="padding: 4rem 0; background: white; margin-top: 4rem; border-top: 1px solid var(--border);">
        <div class="container" style="text-align: center;">
            <h2 style="font-family: 'Fredoka', sans-serif; font-size: 2rem; margin-bottom: 1rem;">Why Scribble Patch?</h2>
            <p style="max-width: 700px; margin: 0 auto; color: #4a5568;">
                We create premium printable coloring pages that bring joy to colorists of all ages. 
                From niche sports like Golf and Soccer to cute Kawaii animals and festive Christmas themes.
            </p>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 Scribble Patch Designs.</p>
        </div>
    </footer>

</body>
</html>
    """
    
    # Write the file to the _site directory
    with open(f"{OUTPUT_DIR}/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print("Created Home Page: index.html")


# --- MAIN EXECUTION ---

def main():
    print("🚀 Starting Site Generator...")
    
    # 1. Prepare Directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(f"{OUTPUT_DIR}/products")
    os.makedirs(f"{OUTPUT_DIR}/collections")
    
    # 2. Copy Assets (favicon)
    if os.path.exists("favicon.png"):
        shutil.copy("favicon.png", f"{OUTPUT_DIR}/favicon.png")
        print("✓ Copied favicon")
    
    # 3. Load Data
    try:
        with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data['products']
            
        with open(COLLECTIONS_JSON, 'r', encoding='utf-8') as f:
            coll_data = json.load(f)['collections']
            
        print(f"✓ Loaded {len(products)} products and {len(coll_data)} collections")
    except FileNotFoundError:
        print("❌ Error: JSON files not found. Run the scraper first.")
        return

    # 4. Build Pages
    # A. Product Pages
    for p in products:
        build_product_page(p, products)
        
    # B. Collection Pages
    for name, data in coll_data.items():
        build_collection_page(name, data['listingIds'], products)
        
    # C. Home Page
    build_home_page(products, coll_data)
    
    print("\n✅ Website generation complete!")
    print(f"👉 Open {OUTPUT_DIR}/index.html to view your site.")

if __name__ == "__main__":
    main()
