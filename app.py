from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import aiohttp
import asyncio

app = Flask(__name__)

def remove_dates(text):
    date_patterns = [
        r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(?:\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
        r'\b(?:\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b'
    ]
    combined_pattern = '|'.join(date_patterns)
    cleaned_text = re.sub(combined_pattern, '', text)
    return cleaned_text

async def is_valid_url(session, url):
    try:
        async with session.head(url, allow_redirects=True, timeout=5) as response:
            return response.status == 200
    except:
        return False

async def validate_urls(links):
    async with aiohttp.ClientSession() as session:
        tasks = [is_valid_url(session, link) for link in links]
        return await asyncio.gather(*tasks)

def fetch_fitness_info(query):
    search_url = f"https://www.google.com/search?q={query}+fitness"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    links = []
    
    for g in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
        text = g.get_text()
        if text:
            cleaned_text = remove_dates(text)
            if cleaned_text not in results and len(results) < 5:
                results.append(cleaned_text)
    
    for a in soup.find_all('a', href=True):
        link = a['href']
        if link.startswith('/url?q='):
            link = link[7:].split('&')[0]
            if link not in links and len(links) < len(results):
                links.append(link)
    
    valid_links = asyncio.run(validate_urls(links))
    filtered_links = [link for link, valid in zip(links, valid_links) if valid]
    
    structured_response = ""
    for i, (result, link) in enumerate(zip(results, filtered_links)):
        structured_response += f'<div>{i + 1}. {result} <a href="{link}" target="_blank"><button>Source</button></a></div><br>'
    
    if not results:
        return "No results found for your query."
    
    return structured_response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bmi_calculator.html')
def bmi_calculator():
    return render_template('bmi_calculator.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/gender_selection.html')
def gender_selection():
    return render_template('gender_selection.html')

@app.route('/quiz.html')
def quiz():
    return render_template('quiz.html')

@app.route('/plan1.html')
def plan():
    return render_template('plan1.html')

@app.route('/plan2.html')
def plan2():
    return render_template('plan2.html')

@app.route('/plan3.html')
def plan3():
    return render_template('plan3.html')

@app.route('/plan4.html')
def plan4():
    return render_template('plan4.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_query = request.form['query']
    response = fetch_fitness_info(user_query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
