# Authentic Search

A modern search engine for personal blogs that helps users discover authentic content from independent writers. The platform indexes and searches through personal blog posts, providing a clean and intuitive interface for content discovery.

## Features

- 🔍 **Smart Search**: Elasticsearch-powered search with fuzzy matching and relevance ranking
- 📱 **Modern UI**: Clean, responsive interface with smooth animations
- 📊 **Content Quality**: Advanced ranking system that considers content quality, recency, and relevance
- 🎲 **Random Discovery**: Feature to discover random articles from the index
- 📈 **Real-time Stats**: View total indexed articles and blog statistics
- 🔄 **Auto-updating**: Regular content fetching from RSS feeds

## Tech Stack

### Backend
- Python/Flask
- Elasticsearch
- RSS Feed Parser
- Content Quality Analysis

### Frontend
- Vanilla JavaScript
- Modern CSS
- Responsive Design

## Setup

### Prerequisites
- Python 3.8+
- Elasticsearch 8.x

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sahil142214/AuthenticSearch
cd AuthenticSearch
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Start Elasticsearch:
```bash
# Make sure Elasticsearch is running on http://localhost:9200
```

4. Index the content:
```bash
cd backend
python index_to_es.py
```

5. Start the backend server:
```bash
python app.py
```

6. Open the frontend:
- Open `frontend/index.html` in your browser
- Or serve it using a local server:
```bash
python -m http.server 8000
```

## Usage

1. **Searching**:
   - Enter your search query in the search bar
   - Results are ranked by relevance, quality, and recency
   - Click on article titles to read the full content

2. **Random Discovery**:
   - Click the "Discover Random" button to find random articles
   - Great for content discovery and exploration

3. **Content Updates**:
   - Run the fetcher periodically to update content:
```bash
python backend/fetcher.py
```

## Project Structure

```
authentic-search/
├── backend/
│   ├── app.py              # Flask server
│   ├── fetcher.py          # RSS feed fetcher
│   └── index_to_es.py      # Elasticsearch indexer
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Styling
│   └── script.js           # Frontend logic
├── data/
│   ├── index.json          # Article index
│   └── blogs.json          # Blog list
└── README.md
```

## Acknowledgments

- Thanks to all the personal bloggers who share their authentic content
- Built with ❤️ for the independent web 
