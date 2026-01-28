"""Tests for article_selector module."""

import pytest
from src.article_selector import (
    count_trump_mentions,
    calculate_relevance_score,
    extract_paragraphs,
    select_most_relevant_article,
)


class TestCountTrumpMentions:
    """Tests for count_trump_mentions function."""

    def test_single_mention(self):
        """Test counting a single mention."""
        text = "Trump made a statement today."
        assert count_trump_mentions(text) == 1

    def test_multiple_mentions(self):
        """Test counting multiple mentions."""
        text = "Trump said Trump would Trump."
        assert count_trump_mentions(text) == 3

    def test_case_insensitive(self):
        """Test that counting is case-insensitive."""
        text = "TRUMP, Trump, and trump are all counted."
        assert count_trump_mentions(text) == 3

    def test_word_boundary(self):
        """Test that only whole words are counted."""
        text = "Trumpet and Trumpeting should not count, but Trump does."
        assert count_trump_mentions(text) == 1

    def test_no_mentions(self):
        """Test text with no mentions."""
        text = "This article is about something else entirely."
        assert count_trump_mentions(text) == 0

    def test_empty_string(self):
        """Test empty string."""
        assert count_trump_mentions("") == 0

    def test_none_input(self):
        """Test None input."""
        assert count_trump_mentions(None) == 0


class TestCalculateRelevanceScore:
    """Tests for calculate_relevance_score function."""

    def test_headline_only_mentions(self):
        """Test scoring with mentions only in headline."""
        article = {
            'webTitle': 'Trump makes announcement',  # 1 mention × 3 = 3
            'fields': {
                'body': 'The president spoke today.'
            }
        }
        assert calculate_relevance_score(article) == 3

    def test_body_only_mentions(self):
        """Test scoring with mentions only in body."""
        article = {
            'webTitle': 'Political news',
            'fields': {
                'body': 'Trump spoke about Trump\'s policies.'  # 2 mentions × 1 = 2
            }
        }
        assert calculate_relevance_score(article) == 2

    def test_both_headline_and_body(self):
        """Test scoring with mentions in both headline and body."""
        article = {
            'webTitle': 'Trump news',  # 1 × 3 = 3
            'fields': {
                'headline': 'Trump makes statement',  # Override webTitle, 1 × 3 = 3
                'body': 'Trump said Trump would...'  # 2 × 1 = 2
            }
        }
        # Should use fields.headline (3) + body (2) = 5
        assert calculate_relevance_score(article) == 5

    def test_no_mentions(self):
        """Test scoring with no mentions."""
        article = {
            'webTitle': 'Weather update',
            'fields': {
                'body': 'Today will be sunny.'
            }
        }
        assert calculate_relevance_score(article) == 0

    def test_missing_body(self):
        """Test scoring when body is missing."""
        article = {
            'webTitle': 'Trump announcement',
            'fields': {}
        }
        assert calculate_relevance_score(article) == 3

    def test_missing_fields(self):
        """Test scoring when fields are missing entirely."""
        article = {
            'webTitle': 'Trump speaks'
        }
        assert calculate_relevance_score(article) == 3


class TestExtractParagraphs:
    """Tests for extract_paragraphs function."""

    def test_extract_single_paragraph(self):
        """Test extracting a single paragraph."""
        html = '<p>This is paragraph one.</p>'
        result = extract_paragraphs(html, max_paragraphs=3)
        assert result == 'This is paragraph one.'

    def test_extract_multiple_paragraphs(self):
        """Test extracting multiple paragraphs."""
        html = '<p>Paragraph one.</p><p>Paragraph two.</p><p>Paragraph three.</p>'
        result = extract_paragraphs(html, max_paragraphs=3)
        assert 'Paragraph one.' in result
        assert 'Paragraph two.' in result
        assert 'Paragraph three.' in result
        # Check they're separated by double newline
        assert '\n\n' in result

    def test_extract_limit_paragraphs(self):
        """Test that max_paragraphs limit is respected."""
        html = '<p>One.</p><p>Two.</p><p>Three.</p><p>Four.</p><p>Five.</p>'
        result = extract_paragraphs(html, max_paragraphs=2)
        assert 'One.' in result
        assert 'Two.' in result
        assert 'Three.' not in result

    def test_strip_html_tags(self):
        """Test that HTML tags are removed."""
        html = '<p>Text with <strong>bold</strong> and <em>italic</em>.</p>'
        result = extract_paragraphs(html)
        assert '<strong>' not in result
        assert '<em>' not in result
        assert 'Text with bold and italic.' in result

    def test_empty_html(self):
        """Test with empty HTML."""
        assert extract_paragraphs('') == ''

    def test_none_html(self):
        """Test with None input."""
        assert extract_paragraphs(None) == ''

    def test_plain_text_paragraphs(self):
        """Test with plain text separated by double newlines."""
        text = 'Paragraph one.\n\nParagraph two.\n\nParagraph three.'
        result = extract_paragraphs(text, max_paragraphs=2)
        assert 'Paragraph one.' in result
        assert 'Paragraph two.' in result
        assert 'Paragraph three.' not in result


class TestSelectMostRelevantArticle:
    """Tests for select_most_relevant_article function."""

    def test_select_highest_score(self):
        """Test that article with highest score is selected."""
        articles = [
            {
                'webTitle': 'Weather news',
                'webUrl': 'https://example.com/1',
                'webPublicationDate': '2024-01-20T10:00:00Z',
                'fields': {'body': 'Sunny today.'}
            },
            {
                'webTitle': 'Trump makes major announcement',  # High score
                'webUrl': 'https://example.com/2',
                'webPublicationDate': '2024-01-20T11:00:00Z',
                'fields': {
                    'headline': 'Trump makes major announcement',
                    'body': 'Trump spoke about Trump policies today.'
                }
            },
            {
                'webTitle': 'Sports news',
                'webUrl': 'https://example.com/3',
                'webPublicationDate': '2024-01-20T12:00:00Z',
                'fields': {'body': 'Game results.'}
            }
        ]

        result = select_most_relevant_article(articles)
        assert result is not None
        assert 'Trump makes major announcement' in result['headline']
        assert result['url'] == 'https://example.com/2'

    def test_empty_list(self):
        """Test with empty article list."""
        result = select_most_relevant_article([])
        assert result is None

    def test_no_trump_mentions(self):
        """Test when no articles mention Trump."""
        articles = [
            {
                'webTitle': 'Weather news',
                'webUrl': 'https://example.com/1',
                'webPublicationDate': '2024-01-20T10:00:00Z',
                'fields': {'body': 'Sunny today.'}
            },
            {
                'webTitle': 'Sports update',
                'webUrl': 'https://example.com/2',
                'webPublicationDate': '2024-01-20T11:00:00Z',
                'fields': {'body': 'Game ended 3-2.'}
            }
        ]

        result = select_most_relevant_article(articles)
        assert result is None

    def test_formatted_output(self):
        """Test that output is properly formatted."""
        articles = [
            {
                'webTitle': 'Trump news',
                'webUrl': 'https://example.com/1',
                'webPublicationDate': '2024-01-20T10:00:00Z',
                'fields': {
                    'headline': 'Trump Headline',
                    'body': '<p>First paragraph.</p><p>Second paragraph.</p>'
                }
            }
        ]

        result = select_most_relevant_article(articles)
        assert 'headline' in result
        assert 'excerpt' in result
        assert 'url' in result
        assert 'published' in result
        assert result['headline'] == 'Trump Headline'
        assert result['url'] == 'https://example.com/1'
        assert result['published'] == '2024-01-20T10:00:00Z'

    def test_excerpt_extraction(self):
        """Test that excerpt is properly extracted."""
        articles = [
            {
                'webTitle': 'Trump story',
                'webUrl': 'https://example.com/1',
                'webPublicationDate': '2024-01-20T10:00:00Z',
                'fields': {
                    'body': '<p>Para 1.</p><p>Para 2.</p><p>Para 3.</p><p>Para 4.</p>'
                }
            }
        ]

        result = select_most_relevant_article(articles)
        # Should have first 3 paragraphs
        assert 'Para 1.' in result['excerpt']
        assert 'Para 2.' in result['excerpt']
        assert 'Para 3.' in result['excerpt']
        assert 'Para 4.' not in result['excerpt']

    def test_missing_body_fallback(self):
        """Test fallback when body is missing."""
        articles = [
            {
                'webTitle': 'Trump headline',
                'webUrl': 'https://example.com/1',
                'webPublicationDate': '2024-01-20T10:00:00Z',
                'fields': {}
            }
        ]

        result = select_most_relevant_article(articles)
        assert result is not None
        # Should use headline as excerpt when body is missing
        assert result['excerpt'] == 'Trump headline'

    def test_uses_fields_headline_over_webtitle(self):
        """Test that fields.headline is preferred over webTitle."""
        articles = [
            {
                'webTitle': 'Generic Title',
                'webUrl': 'https://example.com/1',
                'webPublicationDate': '2024-01-20T10:00:00Z',
                'fields': {
                    'headline': 'Trump Specific Headline',
                    'body': '<p>Article body.</p>'
                }
            }
        ]

        result = select_most_relevant_article(articles)
        assert result['headline'] == 'Trump Specific Headline'
