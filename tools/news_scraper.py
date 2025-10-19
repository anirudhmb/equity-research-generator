"""
News & Research Scraper for Indian Companies.

This module provides functions to fetch recent news and developments
from various free sources:
- Google News RSS feeds (Primary source)
- MoneyControl (Secondary source via web scraping)
- Economic Times (Expandable)
- NSE India announcements (Expandable)

All sources are free and do not require API keys.

IMPORTANT LIMITATION:
- Google News RSS feeds typically retain only 2-3 months of articles
- Requesting more months will still only return what's available
- This is a known limitation of free news sources
- For historical analysis beyond 3 months, paid news APIs would be required
- However, 2-3 months is sufficient for the "Recent Developments" section
  of an equity research report
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
    
    # Show date range
    if not df.empty:
        oldest_date = df['published'].min().strftime('%Y-%m-%d')
        newest_date = df['published'].max().strftime('%Y-%m-%d')
        actual_months = (df['published'].max() - df['published'].min()).days / 30
        
        logger.success(f"\n✅ Total news articles fetched: {len(df)}")
        logger.info(f"   Google News: {len([a for a in all_articles if a['source'] != 'MoneyControl'])}")
        logger.info(f"   MoneyControl: {len([a for a in all_articles if a['source'] == 'MoneyControl'])}")
        logger.info(f"   Date Range: {oldest_date} to {newest_date} ({actual_months:.1f} months)")
        
        if actual_months < months * 0.8:  # If we got less than 80% of requested time
            logger.warning(f"   ⚠️  Note: Requested {months} months but Google News RSS only retains ~2-3 months")
    
    return df


def _remove_duplicate_articles(df: pd.DataFrame, similarity_threshold: float = 0.85) -> pd.DataFrame:
    """
    Remove duplicate articles based on title similarity using fuzzy matching.
    
    This handles cases where the same story is reported by multiple sources
    with slightly different headlines.
    
    Args:
        df: DataFrame with news articles
        similarity_threshold: Titles with similarity >= this are considered duplicates (0-1)
    
    Returns:
        DataFrame with duplicates removed
    """
    if df.empty:
        return df
    
    from difflib import SequenceMatcher
    
    initial_count = len(df)
    
    # First, remove exact duplicates
    df = df.drop_duplicates(subset=['title'], keep='first')
    
    # Then, remove fuzzy duplicates
    to_remove = set()
    titles = df['title'].tolist()
    
    for i in range(len(titles)):
        if i in to_remove:
            continue
            
        for j in range(i + 1, len(titles)):
            if j in to_remove:
                continue
            
            # Calculate similarity
            similarity = SequenceMatcher(None, titles[i].lower(), titles[j].lower()).ratio()
            
            if similarity >= similarity_threshold:
                # Keep the first one (newer), mark the second as duplicate
                to_remove.add(j)
                logger.debug(f"Removing duplicate: '{titles[j][:60]}...' (similar to '{titles[i][:60]}...')")
    
    # Remove duplicates
    if to_remove:
        df = df.iloc[[i for i in range(len(df)) if i not in to_remove]]
        removed_count = initial_count - len(df)
        logger.info(f"   Removed {removed_count} duplicate/similar articles")
    
    return df.reset_index(drop=True)


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


def get_news_timeline(news_df: pd.DataFrame) -> Dict:
    """
    Get timeline statistics showing news distribution over time.
    
    Args:
        news_df: DataFrame with news articles
    
    Returns:
        Dictionary with timeline statistics
    
    Example:
        >>> news_df = fetch_all_news("Reliance", "RELIANCE")
        >>> timeline = get_news_timeline(news_df)
        >>> print(f"Total articles: {timeline['total']}")
        >>> print(f"Date range: {timeline['date_range']}")
    """
    if news_df.empty:
        return {
            'total': 0,
            'date_range': 'No data',
            'by_month': {},
            'by_week': {},
            'sources': {}
        }
    
    # Overall stats
    oldest = news_df['published'].min()
    newest = news_df['published'].max()
    
    # Group by month
    news_df['month'] = news_df['published'].dt.to_period('M')
    by_month = news_df.groupby('month').size().to_dict()
    by_month = {str(k): v for k, v in by_month.items()}
    
    # Group by week
    news_df['week'] = news_df['published'].dt.to_period('W')
    by_week = news_df.groupby('week').size().to_dict()
    by_week = {str(k): v for k, v in by_week.items()}
    
    # Group by source
    by_source = news_df['source'].value_counts().to_dict()
    
    return {
        'total': len(news_df),
        'date_range': f"{oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}",
        'duration_days': (newest - oldest).days,
        'by_month': by_month,
        'by_week': by_week,
        'sources': by_source,
        'avg_per_week': len(news_df) / max(((newest - oldest).days / 7), 1)
    }


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
    print("Testing News Scraper with Enhanced Deduplication & Timeline Analysis...")
    
    test_company = "Reliance Industries"
    test_ticker = "RELIANCE"
    
    try:
        print(f"\nFetching news for {test_company}...")
        
        # Fetch all news (will request 12 months but likely get 2-3 months due to RSS limitations)
        news_df = fetch_all_news(test_company, test_ticker, months=12)
        
        if news_df.empty:
            print("\n❌ No news articles found")
        else:
            print(f"\n✅ Test successful! Fetched {len(news_df)} unique articles (after deduplication)")
            
            # Show timeline analysis
            print(f"\n📅 Timeline Analysis:")
            timeline = get_news_timeline(news_df)
            print(f"   Date Range: {timeline['date_range']}")
            print(f"   Duration: {timeline['duration_days']} days")
            print(f"   Average: {timeline['avg_per_week']:.1f} articles/week")
            print(f"\n   Distribution by Month:")
            for month, count in sorted(timeline['by_month'].items()):
                print(f"      {month}: {count} articles")
            print(f"\n   Sources:")
            for source, count in timeline['sources'].items():
                print(f"      {source}: {count} articles")
            
            # Show recent articles
            print(f"\n📰 Recent Articles (Last 5):")
            recent = news_df.head(5)
            for idx, article in recent.iterrows():
                print(f"\n{idx + 1}. [{article['published_str']}] {article['source']}")
                print(f"   {article['title'][:100]}...")
            
            # Categorize news
            print(f"\n📊 News Categories:")
            categorized = categorize_news(news_df)
            for category, articles in categorized.items():
                if articles:
                    print(f"   {category.replace('_', ' ').title()}: {len(articles)} articles")
            
            # Save to CSV
            filepath = save_news_to_csv(news_df, test_ticker)
            print(f"\n💾 Saved to: {filepath}")
            print(f"\n✨ The CSV contains unique, deduplicated articles covering the timeline above")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

