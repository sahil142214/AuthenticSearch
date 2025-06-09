from flask import Flask, request, jsonify
from rapidfuzz import fuzz
from flask_cors import CORS
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
import math
from elasticsearch import Elasticsearch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


with open('../data/index.json') as f:
    ARTICLES = json.load(f)

WORD_INDEX = defaultdict(set)
for i, article in enumerate(ARTICLES):
    words = re.findall(r'\w+', (article['title'] + ' ' + article['summary']).lower())
    for word in words:
        WORD_INDEX[word].add(i)

es = Elasticsearch("http://localhost:9200")

def calculate_quality_score(article):
    """Calculate a quality score based on various factors"""
    score = 50  
    
   
    summary_length = len(article.get('summary', ''))
    if summary_length > 500:
        score += 15
    elif summary_length > 200:
        score += 8
    
  
    title = article.get('title', '').lower()
    clickbait_words = ['amazing', 'shocking', 'unbelievable', 'you won\'t believe']
    if any(word in title for word in clickbait_words):
        score -= 10
    
  
    personal_indicators = ['i ', 'my ', 'me ', 'we ', 'our ', 'personal', 'experience']
    text = (article.get('title', '') + ' ' + article.get('summary', '')).lower()
    personal_count = sum(text.count(indicator) for indicator in personal_indicators)
    score += min(personal_count * 2, 20)  
    
    return max(score, 0)

def search_articles(query, limit=50):
    """Improved search with multiple ranking factors"""
    if not query:
        return []
    
    query_lower = query.lower()
    query_words = re.findall(r'\w+', query_lower)
    
  
    candidates = set()
    for word in query_words:
       
        if word in WORD_INDEX:
            candidates.update(WORD_INDEX[word])
       
        if len(word) >= 3:
            for indexed_word in WORD_INDEX:
                if word in indexed_word or indexed_word in word:
                    candidates.update(WORD_INDEX[indexed_word])
    
    results = []
    for idx in candidates:
        article = ARTICLES[idx]
        
       
        title_score = fuzz.partial_ratio(query_lower, article['title'].lower())
        summary_score = fuzz.partial_ratio(query_lower, article['summary'].lower())
        exact_match_bonus = 0
        
      
        if query_lower in article['title'].lower():
            exact_match_bonus += 20
        if query_lower in article['summary'].lower():
            exact_match_bonus += 10
        
     
        relevance_score = max(title_score, summary_score) + exact_match_bonus
        
        if relevance_score > 60: 
            quality_score = calculate_quality_score(article)
            
          
            recency_bonus = 0
            if article.get('published'):
                try:
                    pub_date = datetime.strptime(article['published'][:10], '%Y-%m-%d')
                    days_old = (datetime.now() - pub_date).days
                    if days_old < 30:
                        recency_bonus = 10
                    elif days_old < 90:
                        recency_bonus = 5
                except:
                    pass
            
          
            final_score = relevance_score * 0.6 + quality_score * 0.3 + recency_bonus
            
            results.append((final_score, article))
    

    results.sort(reverse=True, key=lambda x: x[0])
    return [article for score, article in results[:limit]]

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    if not query:
        return jsonify([])

    es_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "summary", "blog_name", "tags", "category", "description"],
                "fuzziness": "AUTO"
            }
        },
        "size": limit
    }
    res = es.search(index="articles", body=es_query)
    hits = [hit["_source"] for hit in res["hits"]["hits"]]
    return jsonify(hits)

@app.route('/stats')
def stats():
    """Get statistics about the indexed content"""
    blog_counts = defaultdict(int)
    total_articles = len(ARTICLES)
    
    for article in ARTICLES:
        blog_counts[article['blog_name']] += 1
    
    return jsonify({
        'total_articles': total_articles,
        'total_blogs': len(blog_counts),
        'articles_per_blog': dict(blog_counts),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/random')
def random_article():
    """Get a random article for discovery"""
    import random
    if ARTICLES:
        article = random.choice(ARTICLES)
        return jsonify(article)
    return jsonify({})

@app.route('/blogs')
def list_blogs():
    """List all blogs with article counts"""
    blog_info = defaultdict(lambda: {'count': 0, 'latest': None})
    
    for article in ARTICLES:
        blog_name = article['blog_name']
        blog_info[blog_name]['count'] += 1
        
      
        if article.get('published'):
            if not blog_info[blog_name]['latest'] or article['published'] > blog_info[blog_name]['latest']:
                blog_info[blog_name]['latest'] = article['published']
    
    return jsonify(dict(blog_info))

if __name__ == '__main__':
    print(f"Loaded {len(ARTICLES)} articles")
    print(f"Created word index with {len(WORD_INDEX)} unique words")
    app.run(debug=True, port=5050)