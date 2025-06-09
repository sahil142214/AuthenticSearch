import json
import feedparser
import requests
from datetime import datetime
import time
import hashlib
import re
from urllib.parse import urljoin, urlparse
import html


MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 10

def clean_text(text):
    """Clean HTML and normalize text"""
    if not text:
        return ""
    

    text = re.sub(r'<[^>]+>', '', text)

    text = html.unescape(text)

    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_content_quality_signals(entry, blog_info):
    """Extract signals that indicate content quality"""
    signals = {}
    

    summary = clean_text(entry.get('summary', ''))
    signals['summary_length'] = len(summary)
    signals['word_count'] = len(summary.split())
    

    personal_pronouns = len(re.findall(r'\b(i|my|me|we|our|us)\b', summary.lower()))
    signals['personal_pronoun_count'] = personal_pronouns
    
  
    links_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', entry.get('summary', '')))
    signals['external_links'] = links_count
    
    return signals

def fetch_blog_with_retry(blog, max_retries=MAX_RETRIES):
    """Fetch blog RSS with retry logic"""
    headers = {
        'User-Agent': 'Personal Blog Search Engine (https://github.com/yourusername/blog-search)',
        'Accept': 'application/rss+xml, application/xml, text/xml'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}: Fetching {blog['name']}")
            response = requests.get(
                blog['rss_url'], 
                headers=headers, 
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
       
            feed = feedparser.parse(response.content)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                print(f"  Warning: Feed parsing issues for {blog['name']}: {feed.bozo_exception}")
            
            return feed
            
        except requests.exceptions.RequestException as e:
            print(f"  Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                print(f"  Failed to fetch {blog['name']} after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"  Unexpected error: {e}")
            return None

def process_article(entry, blog_info):
    """Process a single article with enhanced data extraction"""
    

    article_id = hashlib.md5(
        (entry.get('link', '') + entry.get('title', '')).encode()
    ).hexdigest()[:12]
    

    title = clean_text(entry.get('title', ''))
    summary = clean_text(entry.get('summary', entry.get('description', '')))
    
   
    content = entry.get('content')
    if content and isinstance(content, list) and len(content) > 0:
        content_text = clean_text(content[0].get('value', ''))
        if len(content_text) > len(summary):
            summary = content_text[:1000] + ('...' if len(content_text) > 1000 else '')
    

    published = entry.get('published', '')
    published_parsed = entry.get('published_parsed')
    if published_parsed:
        try:
            published = datetime(*published_parsed[:6]).isoformat()
        except:
            pass
    

    quality_signals = extract_content_quality_signals(entry, blog_info)
    

    article = {
        'id': article_id,
        'blog_name': blog_info['name'],
        'blog_url': blog_info['url'],
        'title': title,
        'link': entry.get('link', ''),
        'summary': summary,
        'published': published,
        'author': entry.get('author', ''),
        'tags': [tag.term for tag in entry.get('tags', [])],
        'quality_signals': quality_signals,
        'fetched_at': datetime.now().isoformat()
    }
    
    return article

def load_existing_articles():
    """Load existing articles to avoid duplicates"""
    try:
        with open('../data/index.json') as f:
            existing = json.load(f)
            return {article.get('id', article.get('link', '')): article for article in existing}
    except FileNotFoundError:
        return {}

def main():
    print("🚀 Starting blog content fetcher...")
    
   
    with open('../data/blogs.json') as f:
        blogs = json.load(f)
    
  
    existing_articles = load_existing_articles()
    print(f"📚 Found {len(existing_articles)} existing articles")
    
    all_articles = []
    fetch_stats = {
        'blogs_processed': 0,
        'blogs_failed': 0,
        'new_articles': 0,
        'updated_articles': 0,
        'skipped_articles': 0
    }
    
    for blog in blogs:
        print(f"\n📖 Processing: {blog['name']} ({blog['rss_url']})")
        
        feed = fetch_blog_with_retry(blog)
        if not feed:
            fetch_stats['blogs_failed'] += 1
            continue
        
        fetch_stats['blogs_processed'] += 1
        blog_articles = 0
        
        print(f"  Found {len(feed.entries)} entries")
        
        for entry in feed.entries:
            try:
                article = process_article(entry, blog)
                article_key = article['id']
                
              
                if article_key in existing_articles:
                    existing = existing_articles[article_key]
                    if existing.get('published') == article.get('published'):
                        fetch_stats['skipped_articles'] += 1
                        all_articles.append(existing)  

                        continue
                    else:
                        fetch_stats['updated_articles'] += 1
                else:
                    fetch_stats['new_articles'] += 1
                
                all_articles.append(article)
                blog_articles += 1
                
            except Exception as e:
                print(f"  Error processing article: {e}")
                continue
        
        print(f"  ✅ Processed {blog_articles} articles from {blog['name']}")
        
       
        time.sleep(1)
    

    print(f"\n💾 Saving {len(all_articles)} total articles...")
    
  
    all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    with open('../data/index.json', 'w') as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)
    
    # Save metadata
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'total_articles': len(all_articles),
        'total_blogs': len(blogs),
        'fetch_stats': fetch_stats
    }
    
    with open('../data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    

    print(f"\n📊 Fetch Summary:")
    print(f"  Blogs processed: {fetch_stats['blogs_processed']}/{len(blogs)}")
    print(f"  New articles: {fetch_stats['new_articles']}")
    print(f"  Updated articles: {fetch_stats['updated_articles']}")
    print(f"  Skipped articles: {fetch_stats['skipped_articles']}")
    print(f"  Total articles: {len(all_articles)}")
    print(f"  Failed blogs: {fetch_stats['blogs_failed']}")
    
    if fetch_stats['blogs_failed'] > 0:
        print(f"  ⚠️  Some blogs failed to fetch - check network connectivity")
    
    print("✨ Fetch complete!")

if __name__ == '__main__':
    main()