from elasticsearch import Elasticsearch, helpers
import json
import os

es = Elasticsearch("http://localhost:9200")

INDEX_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'index.json')


with open(INDEX_JSON_PATH, encoding='utf-8') as f:
    articles = json.load(f)

print(f"Loaded {len(articles)} articles")


cleaned_articles = []
for article in articles:

    if article.get('published') == '':
        article['published'] = None  

    if article.get('summary') == '':
        article['summary'] = None
    
    if article.get('author') == '':
        article['author'] = None
    
    cleaned_articles.append(article)

articles = cleaned_articles
print(f"Cleaned {len(articles)} articles")


if es.indices.exists(index="articles"):
    es.indices.delete(index="articles")
    print("Deleted existing 'articles' index")


es.indices.create(index="articles", body={
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "summary": {"type": "text"},
            "blog_name": {"type": "keyword"},
            "category": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "published": {
                "type": "date", 
                "format": "yyyy-MM-dd||yyyy-MM-dd'T'HH:mm:ss||yyyy-MM-dd HH:mm:ss||epoch_millis",
                "null_value": None
            },
            "description": {"type": "text"},
            "author": {"type": "keyword"},
            "link": {"type": "keyword"},
            "blog_url": {"type": "keyword"},
            "fetched_at": {"type": "date"}
        }
    }
})

print("Created 'articles' index")


actions = [
    {
        "_index": "articles",
        "_id": article.get('id', i),
        "_source": article
    }
    for i, article in enumerate(articles)
]

try:
    response = helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} articles to Elasticsearch.")
    print(f"Bulk response: {response}")
except helpers.BulkIndexError as e:
    print(f"Some documents failed to index: {len(e.errors)} errors")


try:
    count = es.count(index="articles")
    print(f"Total documents in index: {count['count']}")
except Exception as e:
    print(f"Error getting count: {e}")