
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('query');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const statsDiv = document.getElementById('stats');
const totalArticlesSpan = document.getElementById('totalArticles');
const randomButton = document.getElementById('randomButton');


const API_BASE = 'http://localhost:5050';


function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function setLoading(isLoading) {
    loadingDiv.classList.toggle('hidden', !isLoading);
    if (isLoading) {
        resultsDiv.innerHTML = '';
    }
}

function truncateText(text, maxLength = 200) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength).trim() + '...';
}

function createArticleCard(article) {
    const card = document.createElement('div');
    card.className = 'article-card';
    
    const title = document.createElement('h3');
    const titleLink = document.createElement('a');
    titleLink.href = article.link;
    titleLink.target = '_blank';
    titleLink.textContent = article.title;
    title.appendChild(titleLink);
    
    const summary = document.createElement('p');
    summary.textContent = truncateText(article.summary);
    
    const meta = document.createElement('div');
    meta.className = 'article-meta';
    
    const source = document.createElement('small');
    source.textContent = `${article.blog_name} | ${formatDate(article.published)}`;
    
    const readMore = document.createElement('a');
    readMore.href = article.link;
    readMore.target = '_blank';
    readMore.className = 'read-more';
    readMore.textContent = 'Read full article →';
    
    meta.appendChild(source);
    meta.appendChild(readMore);
    
    card.appendChild(title);
    card.appendChild(summary);
    card.appendChild(meta);
    
    return card;
}

async function searchArticles(query) {
    try {
        setLoading(true);
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Search failed');
        
        const articles = await response.json();
        
        if (articles.length === 0) {
            resultsDiv.innerHTML = '<p class="no-results">No results found. Try different keywords.</p>';
            return;
        }
        
        resultsDiv.innerHTML = '';
        articles.forEach(article => {
            resultsDiv.appendChild(createArticleCard(article));
        });
    } catch (error) {
        resultsDiv.innerHTML = '<p class="error">Error searching articles. Please try again.</p>';
        console.error('Search error:', error);
    } finally {
        setLoading(false);
    }
}

async function getRandomArticle() {
    try {
        setLoading(true);
        const response = await fetch(`${API_BASE}/random`);
        if (!response.ok) throw new Error('Failed to get random article');
        
        const article = await response.json();
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(createArticleCard(article));
    } catch (error) {
        resultsDiv.innerHTML = '<p class="error">Error getting random article. Please try again.</p>';
        console.error('Random article error:', error);
    } finally {
        setLoading(false);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        if (!response.ok) throw new Error('Failed to load stats');
        
        const stats = await response.json();
        totalArticlesSpan.textContent = stats.total_articles.toLocaleString();
    } catch (error) {
        console.error('Stats error:', error);
    }
}

searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (query) {
        await searchArticles(query);
    }
});

randomButton.addEventListener('click', getRandomArticle);


loadStats();