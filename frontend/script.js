/**
 * Past News - Frontend JavaScript
 * Handles user interactions and API communication
 */

// DOM elements
const buttons = document.querySelectorAll('.time-button');
const resultsSection = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const articleContainer = document.getElementById('article-container');
const quietDayDiv = document.getElementById('quiet-day');
const errorContainer = document.getElementById('error-container');

// Article elements
const articleDateLabel = document.getElementById('article-date-label');
const articleHeadline = document.getElementById('article-headline');
const articleExcerpt = document.getElementById('article-excerpt');
const articlePublished = document.getElementById('article-published');
const articleUrl = document.getElementById('article-url');

// Quiet day elements
const quietDayMessage = document.getElementById('quiet-day-message');
const quietDayDate = document.getElementById('quiet-day-date');

// Error elements
const errorMessage = document.getElementById('error-message');
const retryButton = document.getElementById('retry-button');

// State
let currentOption = null;

/**
 * Initialize the application
 */
function init() {
    // Add click handlers to all time period buttons
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const option = button.dataset.option;
            fetchNews(option);
        });
    });

    // Add retry button handler
    retryButton.addEventListener('click', () => {
        if (currentOption) {
            fetchNews(currentOption);
        }
    });

    // Auto-load today's news on page load
    fetchNews('today');
}

/**
 * Fetch news for a specific time period
 * @param {string} option - Time period option (one_week, two_weeks, one_month, random)
 */
async function fetchNews(option) {
    currentOption = option;

    // Show loading state
    showLoading();

    try {
        // Call API endpoint
        const response = await fetch(`/api/index?option=${option}`);
        const data = await response.json();

        // Handle response
        if (!response.ok) {
            throw new Error(data.error || `Server returned ${response.status}`);
        }

        if (!data.success) {
            throw new Error(data.error || 'Unknown error occurred');
        }

        // Display results
        if (data.article) {
            displayArticle(data);
        } else {
            displayQuietDay(data);
        }

    } catch (error) {
        displayError(error.message);
    }
}

/**
 * Show loading state
 */
function showLoading() {
    resultsSection.classList.remove('hidden');
    loadingDiv.classList.remove('hidden');
    articleContainer.classList.add('hidden');
    quietDayDiv.classList.add('hidden');
    errorContainer.classList.add('hidden');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Hide loading state
 */
function hideLoading() {
    loadingDiv.classList.add('hidden');
}

/**
 * Display article in the UI
 * @param {Object} data - API response data
 */
function displayArticle(data) {
    hideLoading();

    const { date, article } = data;

    // Format and display date
    const formattedDate = formatDate(date);
    articleDateLabel.textContent = `${formattedDate}`;

    // Display article content
    articleHeadline.textContent = article.headline;
    articleExcerpt.textContent = article.excerpt;
    articleUrl.href = article.url;

    // Format and display publication time
    if (article.published) {
        const publishedDate = new Date(article.published);
        articlePublished.textContent = publishedDate.toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Show article container
    articleContainer.classList.remove('hidden');
}

/**
 * Display quiet day message
 * @param {Object} data - API response data
 */
function displayQuietDay(data) {
    hideLoading();

    const { date, message } = data;

    // Format and display date
    const formattedDate = formatDate(date);
    quietDayMessage.textContent = message || 'No Trump coverage found on this day.';
    quietDayDate.textContent = formattedDate;

    // Show quiet day container
    quietDayDiv.classList.remove('hidden');
}

/**
 * Display error message
 * @param {string} message - Error message to display
 */
function displayError(message) {
    hideLoading();

    // Customize error message for common cases
    let displayMessage = message;

    if (message.includes('rate limit')) {
        displayMessage = 'API rate limit exceeded. Please try again later.';
    } else if (message.includes('fetch') || message.includes('network')) {
        displayMessage = 'Network error. Please check your connection and try again.';
    } else if (message.includes('GUARDIAN_API_KEY')) {
        displayMessage = 'Server configuration error. Please contact the administrator.';
    }

    errorMessage.textContent = displayMessage;

    // Show error container
    errorContainer.classList.remove('hidden');
}

/**
 * Format date string for display
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
