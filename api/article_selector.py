"""Article selection logic for Past News application.

This module provides functionality to select the most Trump-relevant article
from a list of articles using a scoring heuristic.
"""

import re
from typing import Optional


def count_trump_mentions(text: str) -> int:
    """
    Count the number of times "Trump" appears in text (case-insensitive).

    Args:
        text: The text to search

    Returns:
        Number of Trump mentions
    """
    if not text:
        return 0
    return len(re.findall(r'\btrump\b', text, re.IGNORECASE))


def calculate_relevance_score(article: dict) -> int:
    """
    Calculate a relevance score for an article based on Trump mentions.

    The scoring heuristic:
    - Headline mentions: 3 points each
    - Body mentions: 1 point each

    Args:
        article: Article dictionary from Guardian API

    Returns:
        Relevance score (higher is more relevant)
    """
    score = 0

    # Get headline (webTitle or from fields)
    headline = article.get('webTitle', '')
    if article.get('fields'):
        headline = article.get('fields', {}).get('headline', headline)

    # Count headline mentions (weighted 3x)
    headline_mentions = count_trump_mentions(headline)
    score += headline_mentions * 3

    # Count body mentions (weighted 1x)
    body = article.get('fields', {}).get('body', '')
    body_mentions = count_trump_mentions(body)
    score += body_mentions

    return score


def extract_paragraphs(html_body: str, max_paragraphs: int = 3) -> str:
    """
    Extract the first N paragraphs from HTML body text.

    This function strips HTML tags and extracts plain text paragraphs.
    If the body is already plain text, it splits by double newlines.

    Args:
        html_body: HTML or plain text body
        max_paragraphs: Maximum number of paragraphs to extract

    Returns:
        Extracted text with up to max_paragraphs paragraphs
    """
    if not html_body:
        return ""

    # Replace closing paragraph tags with newlines to preserve boundaries
    text = re.sub(r'</p>', '\n\n', html_body)

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Split into paragraphs (by double newlines)
    paragraphs = re.split(r'\n\s*\n', text.strip())

    # Filter out empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # Take first N paragraphs
    selected = paragraphs[:max_paragraphs]

    # Join with double newline
    return '\n\n'.join(selected)


def select_most_relevant_article(articles: list[dict]) -> Optional[dict]:
    """
    Select the most Trump-relevant article from a list using a scoring heuristic.

    The function calculates a relevance score for each article and returns the
    one with the highest score. The returned article is formatted for display.

    Args:
        articles: List of article dictionaries from Guardian API

    Returns:
        Formatted article dictionary with keys:
        - headline: Article headline
        - excerpt: First 3 paragraphs of body
        - url: Article URL
        - published: Publication date
        Or None if no articles provided or all have zero relevance

    Example:
        >>> articles = [
        ...     {'webTitle': 'Trump wins election', 'webUrl': 'https://...', ...},
        ...     {'webTitle': 'Weather update', 'webUrl': 'https://...', ...},
        ... ]
        >>> result = select_most_relevant_article(articles)
        >>> result['headline']
        'Trump wins election'
    """
    if not articles:
        return None

    # Calculate scores for all articles
    scored_articles = []
    for article in articles:
        score = calculate_relevance_score(article)
        if score > 0:  # Only consider articles with at least one Trump mention
            scored_articles.append((score, article))

    # If no articles have Trump mentions, return None
    if not scored_articles:
        return None

    # Sort by score (descending) and get the best one
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    best_article = scored_articles[0][1]

    # Format the article for display
    headline = best_article.get('webTitle', 'Untitled')
    if best_article.get('fields', {}).get('headline'):
        headline = best_article['fields']['headline']

    body = best_article.get('fields', {}).get('body', '')
    excerpt = extract_paragraphs(body, max_paragraphs=3)

    # If no excerpt, try to create one from the headline or return a placeholder
    if not excerpt:
        excerpt = headline

    return {
        'headline': headline,
        'excerpt': excerpt,
        'url': best_article.get('webUrl', ''),
        'published': best_article.get('webPublicationDate', ''),
    }
