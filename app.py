from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai

app = Flask(__name__)

# Configure your Gemini API key here
GEMINI_API_KEY = "AIzaSyBEs4oQTz3vbDimpuQZ21p5D964MK72HiQ"
genai.configure(api_key=GEMINI_API_KEY)

def get_amazon():
    url = "https://www.amazon.in/gp/bestsellers"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    products = []
    for item in soup.select('.p13n-sc-uncoverable-faceout'):
        title = item.select_one('.p13n-sc-truncate-desktop-type2')
        if title:
            products.append(title.get_text(strip=True))
    return products[:5]

def get_seo_keywords(product_name):
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    prompt = f"Suggest 4 SEO keywords for writing a blog about: {product_name}"
    response = model.generate_content(prompt)
    return [kw.strip() for kw in response.text.split(",")]

def generate_blog(product, keywords):
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    prompt = f"""Write a short blog post (~200 words) about the product: {product}.
Incorporate the following SEO keywords: {', '.join(keywords)}.
Keep the tone friendly, helpful, and SEO-optimized."""
    response = model.generate_content(prompt)
    return response.text

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():
    try:
        products = get_amazon()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    product = data.get("product")
    if not product:
        return jsonify({"error": "Product name required"}), 400
    
    try:
        keywords = get_seo_keywords(product)
        blog = generate_blog(product, keywords)
        return jsonify({"title": product, "blog": blog})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
