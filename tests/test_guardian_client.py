"""Tests for guardian_client module."""

import pytest
import responses
from datetime import date
from requests.exceptions import Timeout
from src.guardian_client import (
    GuardianClient,
    GuardianAPIError,
    GuardianRateLimitError,
)


@pytest.fixture
def client():
    """Create a GuardianClient instance for testing."""
    return GuardianClient(api_key='test-api-key')


@pytest.fixture
def sample_api_response():
    """Sample successful API response."""
    return {
        'response': {
            'status': 'ok',
            'total': 2,
            'results': [
                {
                    'id': 'politics/2024/jan/20/trump-article-1',
                    'webTitle': 'Trump makes statement on policy',
                    'webUrl': 'https://www.theguardian.com/politics/2024/jan/20/trump-article-1',
                    'webPublicationDate': '2024-01-20T10:00:00Z',
                    'fields': {
                        'headline': 'Trump makes statement on policy',
                        'body': '<p>Trump said today that...</p>',
                        'thumbnail': 'https://example.com/thumb.jpg'
                    }
                },
                {
                    'id': 'politics/2024/jan/20/trump-article-2',
                    'webTitle': 'Another Trump story',
                    'webUrl': 'https://www.theguardian.com/politics/2024/jan/20/trump-article-2',
                    'webPublicationDate': '2024-01-20T14:30:00Z',
                    'fields': {
                        'headline': 'Another Trump story',
                        'body': '<p>In other Trump news...</p>'
                    }
                }
            ]
        }
    }


class TestGuardianClientInit:
    """Tests for GuardianClient initialization."""

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        client = GuardianClient('my-api-key')
        assert client.api_key == 'my-api-key'
        assert client.BASE_URL == 'https://content.guardianapis.com/search'


class TestSearchTrumpArticles:
    """Tests for search_trump_articles method."""

    @responses.activate
    def test_successful_search(self, client, sample_api_response):
        """Test successful article search."""
        target_date = date(2024, 1, 20)

        # Mock the API response
        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json=sample_api_response,
            status=200
        )

        # Call the method
        articles = client.search_trump_articles(target_date)

        # Verify results
        assert len(articles) == 2
        assert articles[0]['webTitle'] == 'Trump makes statement on policy'
        assert articles[1]['webTitle'] == 'Another Trump story'

        # Verify request was made with correct parameters
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert 'q=Trump' in request.url
        assert 'from-date=2024-01-20' in request.url
        assert 'to-date=2024-01-20' in request.url
        assert 'page-size=50' in request.url
        assert 'show-fields=body%2Cheadline%2Cthumbnail' in request.url
        assert 'api-key=test-api-key' in request.url

    @responses.activate
    def test_empty_results(self, client):
        """Test handling of empty results."""
        target_date = date(2015, 1, 1)

        # Mock empty response
        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json={
                'response': {
                    'status': 'ok',
                    'total': 0,
                    'results': []
                }
            },
            status=200
        )

        articles = client.search_trump_articles(target_date)
        assert articles == []

    @responses.activate
    def test_custom_page_size(self, client, sample_api_response):
        """Test search with custom page size."""
        target_date = date(2024, 1, 20)

        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json=sample_api_response,
            status=200
        )

        client.search_trump_articles(target_date, page_size=100)

        # Verify page_size parameter
        request = responses.calls[0].request
        assert 'page-size=100' in request.url

    @responses.activate
    def test_rate_limit_error(self, client):
        """Test handling of rate limit (429) error."""
        target_date = date(2024, 1, 20)

        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json={'message': 'Rate limit exceeded'},
            status=429
        )

        with pytest.raises(GuardianRateLimitError, match="API rate limit exceeded"):
            client.search_trump_articles(target_date)

    @responses.activate
    def test_api_error_400(self, client):
        """Test handling of 400 error."""
        target_date = date(2024, 1, 20)

        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json={'message': 'Bad request'},
            status=400
        )

        with pytest.raises(GuardianAPIError, match="Guardian API returned error 400"):
            client.search_trump_articles(target_date)

    @responses.activate
    def test_api_error_500(self, client):
        """Test handling of 500 server error."""
        target_date = date(2024, 1, 20)

        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json={'message': 'Internal server error'},
            status=500
        )

        with pytest.raises(GuardianAPIError, match="Guardian API returned error 500"):
            client.search_trump_articles(target_date)

    @responses.activate
    def test_non_ok_status_in_response(self, client):
        """Test handling of non-OK status in API response."""
        target_date = date(2024, 1, 20)

        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json={
                'response': {
                    'status': 'error',
                    'message': 'Something went wrong'
                }
            },
            status=200
        )

        with pytest.raises(GuardianAPIError, match="non-OK status"):
            client.search_trump_articles(target_date)

    @responses.activate
    def test_timeout_error(self, client):
        """Test handling of timeout."""
        target_date = date(2024, 1, 20)

        # Mock timeout
        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            body=Timeout()
        )

        with pytest.raises(Timeout, match="timed out"):
            client.search_trump_articles(target_date)


class TestContextManager:
    """Tests for context manager functionality."""

    @responses.activate
    def test_context_manager(self, sample_api_response):
        """Test using client as context manager."""
        target_date = date(2024, 1, 20)

        responses.add(
            responses.GET,
            'https://content.guardianapis.com/search',
            json=sample_api_response,
            status=200
        )

        with GuardianClient('test-key') as client:
            articles = client.search_trump_articles(target_date)
            assert len(articles) == 2

        # Session should be closed after context exit
        # (We can't easily test this without accessing private attributes)

    def test_manual_close(self, client):
        """Test manual close of session."""
        # Should not raise any errors
        client.close()
