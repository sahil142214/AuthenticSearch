document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const queryInput = document.getElementById('query');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const totalArticlesSpan = document.getElementById('totalArticles');
    const randomButton = document.getElementById('randomButton');

    const API_BASE = 'http://localhost:5050';

    function formatDate(dateString) {
        if (!dateString) return 'Date unknown';
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
        const summaryText = truncateText(article.summary || 'No summary available.');
        const publishedDate = formatDate(article.published);
        const title = article.title || 'Untitled Article';

        return `
            <div class="article-card">
                <h3>
                    <a href="${article.link}" target="_blank" rel="noopener noreferrer">${title}</a>
                </h3>
                <p>${summaryText}</p>
                <div class="article-meta">
                    <small>${article.blog_name} | ${publishedDate}</small>
                    <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="read-more">Read full article →</a>
                </div>
            </div>
        `;
    }
    
    function showWelcomeMessage() {
        resultsDiv.innerHTML = `
            <div class="welcome-message">
                <h2>Discover authentic voices.</h2>
                <p>Enter a topic above to search, or try discovering a random article.</p>
            </div>
        `;
    }

    async function searchArticles(query) {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error(`Search failed with status: ${response.status}`);
            
            const articles = await response.json();
            
            if (articles.length === 0) {
                resultsDiv.innerHTML = '<p class="no-results">No results found for that query. Try different keywords.</p>';
                return;
            }
            
            resultsDiv.innerHTML = articles.map(createArticleCard).join('');
        } catch (error) {
            resultsDiv.innerHTML = '<p class="error">Could not connect to the search service. Please try again later.</p>';
            console.error('Search error:', error);
        } finally {
            setLoading(false);
        }
    }

    async function getRandomArticle() {
        queryInput.value = ''; // Clear the search input
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE}/random`);
            if (!response.ok) throw new Error('Failed to get random article');
            
            const article = await response.json();
            resultsDiv.innerHTML = createArticleCard(article);
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
            totalArticlesSpan.textContent = 'N/A';
            console.error('Stats error:', error);
        }
    }

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (query) {
            searchArticles(query);
        }
    });

    randomButton.addEventListener('click', getRandomArticle);

    // Initial setup
    loadStats();
    showWelcomeMessage();
});
