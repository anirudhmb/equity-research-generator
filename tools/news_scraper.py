"""
News & Research Scraper for Indian Companies.

This module provides functions to fetch recent news and developments
from various free sources:
- Google News RSS feeds
- MoneyControl (basic scraping)
- Economic Times (basic scraping)
- NSE India announcements

All sources are free and do not require API keys.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re

import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import MONTHS_OF_NEWS, MAX_RETRIES, RETRY_DELAY
from utils.logger import logger


def fetch_google_news(company_name: str, ticker: str, months: int = MONTHS_OF_NEWS) -> List[Dict]:
    """
    Fetch news articles from Google News RSS feed.
    
    Args:
        company_name: Full company name (e.g., "Reliance Industries")
        ticker: Stock ticker without suffix (e.g., "RELIANCE")
        months: Number of months of news to fetch
    
    Returns:
        List of news articles with title, link, published date, summary
    
    Example:
        >>> news = fetch_google_news("Reliance Industries", "RELIANCE", months=6)
        >>> print(f"Found {len(news)} articles")
        >>> print(news[0]['title'])
    """
    logger.info(f"Fetching Google News for {company_name}")
    
    # Build search query
    search_query = f"{company_name} OR {ticker} stock news"
    encoded_query = requests.utils.quote(search_query)
    
    # Google News RSS feed URL
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        # Fetch RSS feed
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"No news found for {company_name}")
            return []
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        articles = []
        for entry in feed.entries:
            try:
                # Parse published date
                pub_date = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                
                # Filter by date
                if pub_date < cutoff_date:
                    continue
                
                article = {
                    'title': entry.title if hasattr(entry, 'title') else 'No title',
                    'link': entry.link if hasattr(entry, 'link') else '',
                    'published': pub_date,
                    'published_str': pub_date.strftime('%Y-%m-%d'),
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'source': _extract_source(entry.title) if hasattr(entry, 'title') else 'Unknown'
                }
                
                articles.append(article)
                
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        logger.success(f"✅ Fetched {len(articles)} articles from Google News")
        return articles
        
    except Exception as e:
        logger.error(f"Error fetching Google News: {e}")
        return []


def _extract_source(title: str) -> str:
    """Extract source name from Google News title (format: "Title - Source")."""
    if ' - ' in title:
        return title.split(' - ')[-1].strip()
    return 'Unknown'


def fetch_moneycontrol_news(ticker: str, months: int = MONTHS_OF_NEWS) -> List[Dict]:
    """
    Fetch news from MoneyControl (basic scraping).
    
    Note: This is a basic implementation. MoneyControl may update their
    HTML structure, requiring adjustments.
    
    Args:
        ticker: Stock ticker (e.g., "RELIANCE")
        months: Number of months of news
    
    Returns:
        List of news articles
    
    Example:
        >>> news = fetch_moneycontrol_news("RELIANCE")
        >>> print(f"Found {len(news)} MoneyControl articles")
    """
    logger.info(f"Fetching MoneyControl news for {ticker}")
    
    try:
        # MoneyControl search URL
        search_url = f"https://www.moneycontrol.com/news/tags/{ticker.lower()}.html"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"MoneyControl returned status {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find news articles (structure may vary)
        articles = []
        
        # Try to find article links
        news_items = soup.find_all('li', class_='clearfix')
        
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        for item in news_items[:20]:  # Limit to 20 articles
            try:
                link_tag = item.find('a')
                if not link_tag:
                    continue
                
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href', '')
                
                # Get date if available
                date_tag = item.find('span')
                pub_date = datetime.now()  # Default to now
                
                if date_tag:
                    date_text = date_tag.get_text(strip=True)
                    pub_date = _parse_relative_date(date_text)
                
                if pub_date < cutoff_date:
                    continue
                
                articles.append({
                    'title': title,
                    'link': link,
                    'published': pub_date,
                    'published_str': pub_date.strftime('%Y-%m-%d'),
                    'summary': '',
                    'source': 'MoneyControl'
                })
                
            except Exception as e:
                logger.debug(f"Error parsing MoneyControl article: {e}")
                continue
        
        logger.success(f"✅ Fetched {len(articles)} articles from MoneyControl")
        return articles
        
    except Exception as e:
        logger.warning(f"MoneyControl scraping failed: {e}")
        return []


def _parse_relative_date(date_str: str) -> datetime:
    """Parse relative dates like '2 hours ago', '3 days ago'."""
    now = datetime.now()
    date_str = date_str.lower()
    
    if 'hour' in date_str or 'hr' in date_str:
        hours = int(re.search(r'\d+', date_str).group()) if re.search(r'\d+', date_str) else 1
        return now - timedelta(hours=hours)
    elif 'day' in date_str:
        days = int(re.search(r'\d+', date_str).group()) if re.search(r'\d+', date_str) else 1
        return now - timedelta(days=days)
    elif 'week' in date_str:
        weeks = int(re.search(r'\d+', date_str).group()) if re.search(r'\d+', date_str) else 1
        return now - timedelta(weeks=weeks)
    elif 'month' in date_str:
        months = int(re.search(r'\d+', date_str).group()) if re.search(r'\d+', date_str) else 1
        return now - timedelta(days=months * 30)
    
    return now


def fetch_all_news(company_name: str, ticker: str, months: int = MONTHS_OF_NEWS) -> pd.DataFrame:
    """
    Fetch news from all available sources and combine.
    
    Args:
        company_name: Full company name
        ticker: Stock ticker (without suffix)
        months: Number of months of news
    
    Returns:
        DataFrame with combined news from all sources
    
    Example:
        >>> news_df = fetch_all_news("Reliance Industries", "RELIANCE", months=12)
        >>> print(f"Total articles: {len(news_df)}")
        >>> print(news_df[['published_str', 'title', 'source']].head())
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"FETCHING NEWS: {company_name} ({ticker})")
    logger.info(f"{'='*60}")
    
    all_articles = []
    
    # 1. Google News (Primary source - most reliable)
    google_news = fetch_google_news(company_name, ticker, months)
    all_articles.extend(google_news)
    
    # 2. MoneyControl (Secondary - may fail)
    try:
        mc_news = fetch_moneycontrol_news(ticker, months)
        all_articles.extend(mc_news)
    except Exception as e:
        logger.warning(f"MoneyControl fetch failed: {e}")
    
    # Convert to DataFrame
    if not all_articles:
        logger.warning("No news articles found from any source")
        return pd.DataFrame(columns=['title', 'link', 'published', 'published_str', 'summary', 'source'])
    
    df = pd.DataFrame(all_articles)
    
    # Sort by date (newest first)
    df = df.sort_values('published', ascending=False)
    
    # Remove duplicates based on title similarity
    df = _remove_duplicate_articles(df)
    
    logger.success(f"\n✅ Total news articles fetched: {len(df)}")
    logger.info(f"   Google News: {len([a for a in all_articles if a['source'] != 'MoneyControl'])}")
    logger.info(f"   MoneyControl: {len([a for a in all_articles if a['source'] == 'MoneyControl'])}")
    
    return df


def _remove_duplicate_articles(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate articles based on title similarity."""
    if df.empty:
        return df
    
    # Simple deduplication: remove exact title matches
    df = df.drop_duplicates(subset=['title'], keep='first')
    
    # Could add fuzzy matching here for better deduplication
    
    return df


def categorize_news(news_df: pd.DataFrame) -> Dict[str, List[Dict]]:
    """
    Categorize news articles into relevant categories.
    
    Categories:
    - Financial Performance
    - New Products/Services
    - Management Changes
    - Regulatory/Legal
    - Market/Industry Trends
    - Mergers & Acquisitions
    - Other
    
    Args:
        news_df: DataFrame with news articles
    
    Returns:
        Dictionary with categorized articles
    
    Example:
        >>> news_df = fetch_all_news("Reliance", "RELIANCE")
        >>> categorized = categorize_news(news_df)
        >>> print(f"Financial news: {len(categorized['financial'])}")
    """
    logger.info("Categorizing news articles")
    
    categories = {
        'financial': [],
        'products': [],
        'management': [],
        'regulatory': [],
        'market_trends': [],
        'ma': [],  # Mergers & Acquisitions
        'other': []
    }
    
    # Keywords for each category
    keywords = {
        'financial': ['revenue', 'profit', 'earnings', 'results', 'quarterly', 'q1', 'q2', 'q3', 'q4', 
                     'sales', 'growth', 'loss', 'margin', 'ebitda'],
        'products': ['launch', 'new product', 'service', 'innovation', 'technology', 'platform'],
        'management': ['ceo', 'cfo', 'chairman', 'board', 'director', 'appoint', 'resign', 'management'],
        'regulatory': ['sebi', 'rbi', 'regulator', 'compliance', 'legal', 'court', 'law', 'penalty'],
        'market_trends': ['market', 'industry', 'sector', 'competition', 'share', 'trend'],
        'ma': ['merger', 'acquisition', 'buyout', 'takeover', 'deal', 'partnership', 'joint venture']
    }
    
    for _, article in news_df.iterrows():
        title_lower = article['title'].lower()
        summary_lower = article.get('summary', '').lower()
        text = f"{title_lower} {summary_lower}"
        
        categorized = False
        
        # Check each category
        for category, category_keywords in keywords.items():
            if any(keyword in text for keyword in category_keywords):
                categories[category].append(article.to_dict())
                categorized = True
                break
        
        # If not categorized, put in 'other'
        if not categorized:
            categories['other'].append(article.to_dict())
    
    # Log category counts
    logger.success("✅ News categorization complete:")
    for category, articles in categories.items():
        if articles:
            logger.info(f"   {category.replace('_', ' ').title()}: {len(articles)} articles")
    
    return categories


def get_recent_developments_summary(news_df: pd.DataFrame, limit: int = 10) -> List[Dict]:
    """
    Get summary of recent developments for the report.
    
    Args:
        news_df: DataFrame with news articles
        limit: Number of recent articles to include
    
    Returns:
        List of most recent and relevant articles
    
    Example:
        >>> news_df = fetch_all_news("Reliance", "RELIANCE")
        >>> recent = get_recent_developments_summary(news_df, limit=5)
        >>> for article in recent:
        ...     print(f"{article['published_str']}: {article['title']}")
    """
    if news_df.empty:
        return []
    
    # Get most recent articles
    recent = news_df.head(limit)
    
    return recent.to_dict('records')


def save_news_to_csv(news_df: pd.DataFrame, ticker: str) -> str:
    """
    Save news data to CSV file.
    
    Args:
        news_df: DataFrame with news articles
        ticker: Company ticker
    
    Returns:
        Path to saved file
    """
    from config.settings import DATA_DIR
    
    if news_df.empty:
        logger.warning("No news data to save")
        return ""
    
    filename = f"{ticker}_news_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = DATA_DIR / filename
    
    # Select columns to save
    columns_to_save = ['published_str', 'title', 'source', 'link', 'summary']
    news_df[columns_to_save].to_csv(filepath, index=False)
    
    logger.success(f"✅ Saved news data to {filepath}")
    return str(filepath)


if __name__ == "__main__":
    # Test the module
    print("Testing News Scraper...")
    
    test_company = "Reliance Industries"
    test_ticker = "RELIANCE"
    
    try:
        print(f"\nFetching news for {test_company}...")
        
        # Fetch all news
        news_df = fetch_all_news(test_company, test_ticker, months=3)
        
        if news_df.empty:
            print("\n❌ No news articles found")
        else:
            print(f"\n✅ Test successful! Fetched {len(news_df)} articles")
            
            # Show recent articles
            print(f"\n📰 Recent Articles (Last 5):")
            recent = news_df.head(5)
            for idx, article in recent.iterrows():
                print(f"\n{idx + 1}. [{article['published_str']}] {article['source']}")
                print(f"   {article['title']}")
                print(f"   {article['link'][:80]}...")
            
            # Categorize news
            print(f"\n📊 News Categories:")
            categorized = categorize_news(news_df)
            for category, articles in categorized.items():
                if articles:
                    print(f"   {category.replace('_', ' ').title()}: {len(articles)} articles")
            
            # Save to CSV
            filepath = save_news_to_csv(news_df, test_ticker)
            print(f"\n💾 Saved to: {filepath}")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

