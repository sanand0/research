#!/usr/bin/env python3
"""
GitHub Data Professionals Collector
Searches GitHub for data scientists and engineers in India
"""

import requests
import time
import json
import csv
import os
from typing import List, Dict, Optional
from datetime import datetime

class GitHubCollector:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub collector.

        Args:
            token: GitHub personal access token (optional, but increases rate limit)
        """
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'

        self.base_url = 'https://api.github.com'
        self.results = []

    def check_rate_limit(self) -> Dict:
        """Check current GitHub API rate limit status."""
        response = requests.get(f'{self.base_url}/rate_limit', headers=self.headers)
        return response.json()

    def search_users(self, query: str, max_results: int = 1000) -> List[Dict]:
        """
        Search for users matching the query.

        Args:
            query: GitHub search query (e.g., "location:India data scientist")
            max_results: Maximum number of results to fetch

        Returns:
            List of user dictionaries
        """
        users = []
        page = 1
        per_page = 100  # GitHub max

        print(f"Searching for: {query}")

        while len(users) < max_results:
            try:
                url = f'{self.base_url}/search/users'
                params = {
                    'q': query,
                    'per_page': per_page,
                    'page': page
                }

                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code == 403:
                    print("Rate limit exceeded. Waiting...")
                    rate_limit = self.check_rate_limit()
                    reset_time = rate_limit['resources']['search']['reset']
                    wait_time = reset_time - time.time() + 5
                    if wait_time > 0:
                        print(f"Waiting {wait_time:.0f} seconds for rate limit reset...")
                        time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()

                if not data.get('items'):
                    break

                users.extend(data['items'])
                print(f"Fetched {len(users)} users so far...")

                # GitHub search API only returns up to 1000 results
                if data['total_count'] <= len(users) or len(data['items']) < per_page:
                    break

                page += 1
                time.sleep(2)  # Be nice to the API

            except Exception as e:
                print(f"Error searching users: {e}")
                break

        return users[:max_results]

    def get_user_details(self, username: str) -> Optional[Dict]:
        """
        Get detailed information for a specific user.

        Args:
            username: GitHub username

        Returns:
            User details dictionary
        """
        try:
            url = f'{self.base_url}/users/{username}'
            response = requests.get(url, headers=self.headers)

            if response.status_code == 403:
                rate_limit = self.check_rate_limit()
                reset_time = rate_limit['resources']['core']['reset']
                wait_time = reset_time - time.time() + 5
                if wait_time > 0:
                    print(f"Rate limit hit. Waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time)
                    response = requests.get(url, headers=self.headers)

            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error fetching user {username}: {e}")
            return None

    def extract_profile_data(self, user_detail: Dict) -> Dict:
        """Extract relevant fields from user profile."""
        return {
            'username': user_detail.get('login', ''),
            'name': user_detail.get('name', ''),
            'company': user_detail.get('company', ''),
            'blog': user_detail.get('blog', ''),
            'location': user_detail.get('location', ''),
            'email': user_detail.get('email', ''),
            'bio': user_detail.get('bio', ''),
            'public_repos': user_detail.get('public_repos', 0),
            'followers': user_detail.get('followers', 0),
            'following': user_detail.get('following', 0),
            'created_at': user_detail.get('created_at', ''),
            'updated_at': user_detail.get('updated_at', ''),
            'profile_url': user_detail.get('html_url', ''),
            'twitter_username': user_detail.get('twitter_username', ''),
        }

    def collect_data_professionals(self, locations: List[str], keywords: List[str],
                                   max_per_query: int = 500) -> List[Dict]:
        """
        Collect data professionals from India.

        Args:
            locations: List of location strings (e.g., ['India', 'Bangalore', 'Mumbai'])
            keywords: List of keyword searches (e.g., ['data scientist', 'machine learning'])
            max_per_query: Maximum results per search query

        Returns:
            List of user profiles
        """
        all_users = {}  # Use dict to deduplicate by username

        for location in locations:
            for keyword in keywords:
                query = f'location:{location} {keyword}'
                users = self.search_users(query, max_results=max_per_query)

                print(f"\nFetching details for {len(users)} users from query: {query}")

                for i, user in enumerate(users, 1):
                    username = user['login']

                    if username in all_users:
                        continue

                    details = self.get_user_details(username)
                    if details:
                        profile = self.extract_profile_data(details)
                        all_users[username] = profile

                        if i % 10 == 0:
                            print(f"Processed {i}/{len(users)} users...")

                    time.sleep(1)  # Rate limiting

        return list(all_users.values())

    def save_to_json(self, data: List[Dict], filename: str):
        """Save collected data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(data)} profiles to {filename}")

    def save_to_csv(self, data: List[Dict], filename: str):
        """Save collected data to CSV file."""
        if not data:
            print("No data to save")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved {len(data)} profiles to {filename}")


def main():
    """Main execution function."""
    print("GitHub Data Professionals Collector")
    print("=" * 50)

    # Check for GitHub token in environment
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Warning: No GITHUB_TOKEN environment variable found.")
        print("Running without authentication (60 requests/hour limit)")
        print("Set GITHUB_TOKEN for 5000 requests/hour\n")

    collector = GitHubCollector(token)

    # Check rate limit
    rate_limit = collector.check_rate_limit()
    search_limit = rate_limit['resources']['search']
    print(f"Search API: {search_limit['remaining']}/{search_limit['limit']} requests remaining")
    core_limit = rate_limit['resources']['core']
    print(f"Core API: {core_limit['remaining']}/{core_limit['limit']} requests remaining\n")

    # Define search parameters
    # Use major Indian cities + "India" to maximize coverage
    locations = [
        'India',
        'Bangalore',
        'Bengaluru',
        'Mumbai',
        'Delhi',
        'Hyderabad',
        'Pune',
        'Chennai',
        'Kolkata',
        'Gurgaon',
        'Noida'
    ]

    # Keywords related to data science and engineering
    keywords = [
        'data scientist',
        'data engineer',
        'machine learning engineer',
        'ML engineer',
        'data analyst',
        'AI engineer',
        'analytics',
    ]

    # Collect data
    print(f"Searching {len(locations)} locations × {len(keywords)} keywords...")
    print(f"This may take a while due to API rate limits.\n")

    profiles = collector.collect_data_professionals(
        locations=locations[:3],  # Start with top 3 locations to test
        keywords=keywords[:3],     # Start with top 3 keywords
        max_per_query=100          # Limit for testing
    )

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    collector.save_to_json(profiles, f'github_profiles_{timestamp}.json')
    collector.save_to_csv(profiles, f'github_profiles_{timestamp}.csv')

    print(f"\n{'=' * 50}")
    print(f"Total unique profiles collected: {len(profiles)}")
    print(f"{'=' * 50}")


if __name__ == '__main__':
    main()
