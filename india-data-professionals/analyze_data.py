#!/usr/bin/env python3
"""
Data Analysis Script
Analyzes collected data from various sources
"""

import json
import csv
import os
from collections import Counter
from typing import List, Dict
import glob

def load_json_files(pattern: str) -> List[Dict]:
    """Load all JSON files matching the pattern."""
    all_data = []
    files = glob.glob(pattern)

    for file in files:
        print(f"Loading {file}...")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return all_data

def load_csv_files(pattern: str) -> List[Dict]:
    """Load all CSV files matching the pattern."""
    all_data = []
    files = glob.glob(pattern)

    for file in files:
        print(f"Loading {file}...")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data.extend(list(reader))
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return all_data

def analyze_github_profiles(profiles: List[Dict]):
    """Analyze GitHub profile data."""
    print("\n" + "=" * 60)
    print("GITHUB PROFILES ANALYSIS")
    print("=" * 60)

    if not profiles:
        print("No profiles to analyze")
        return

    print(f"\nTotal profiles: {len(profiles)}")

    # Location distribution
    locations = [p.get('location', '').strip() for p in profiles if p.get('location')]
    location_counts = Counter(locations)

    print(f"\nTop 15 Locations:")
    for location, count in location_counts.most_common(15):
        print(f"  {location}: {count}")

    # Company distribution
    companies = [p.get('company', '').strip() for p in profiles if p.get('company')]
    # Clean company names (remove @ symbol common in GitHub)
    companies = [c.lstrip('@') for c in companies if c]
    company_counts = Counter(companies)

    print(f"\nTop 20 Companies:")
    for company, count in company_counts.most_common(20):
        print(f"  {company}: {count}")

    # Experience estimation (based on account creation date)
    print(f"\nAccount Creation Years:")
    years = []
    for p in profiles:
        created = p.get('created_at', '')
        if created:
            year = created.split('-')[0]
            years.append(year)

    year_counts = Counter(years)
    for year, count in sorted(year_counts.items(), reverse=True)[:10]:
        print(f"  {year}: {count} accounts created")

    # Repository statistics
    repos = [int(p.get('public_repos', 0)) for p in profiles]
    followers = [int(p.get('followers', 0)) for p in profiles]

    if repos:
        print(f"\nRepository Statistics:")
        print(f"  Average public repos: {sum(repos) / len(repos):.1f}")
        print(f"  Max repos: {max(repos)}")
        print(f"  Users with 0 repos: {repos.count(0)}")

    if followers:
        print(f"\nFollower Statistics:")
        print(f"  Average followers: {sum(followers) / len(followers):.1f}")
        print(f"  Max followers: {max(followers)}")
        print(f"  Users with 100+ followers: {sum(1 for f in followers if f >= 100)}")

    # Bio keyword analysis
    print(f"\nBio Keyword Analysis:")
    keywords = [
        'data scientist', 'data engineer', 'machine learning', 'ML',
        'AI', 'artificial intelligence', 'analytics', 'big data',
        'deep learning', 'NLP', 'computer vision', 'senior', 'lead',
        'principal', 'manager', 'director'
    ]

    for keyword in keywords:
        count = sum(1 for p in profiles
                   if p.get('bio') and keyword.lower() in p.get('bio', '').lower())
        if count > 0:
            print(f"  '{keyword}': {count} profiles")

    # Experience level estimation from bio
    seniority = {
        'junior': 0,
        'mid': 0,
        'senior': 0,
        'lead': 0,
        'principal': 0,
        'director': 0,
        'manager': 0
    }

    for p in profiles:
        bio = p.get('bio', '').lower() if p.get('bio') else ''
        name = p.get('name', '').lower() if p.get('name') else ''
        combined = bio + ' ' + name

        for level in seniority:
            if level in combined:
                seniority[level] += 1

    print(f"\nSeniority Level Indicators (from bio/name):")
    for level, count in sorted(seniority.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {level.capitalize()}: {count}")

    # Email availability
    emails = [p for p in profiles if p.get('email')]
    print(f"\nProfiles with public email: {len(emails)}")

    # Blog/website availability
    blogs = [p for p in profiles if p.get('blog')]
    print(f"Profiles with blog/website: {len(blogs)}")

def generate_summary_report(profiles: List[Dict], output_file: str):
    """Generate a summary report."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Data Professionals in India - Summary Report\n\n")

        f.write(f"## Overview\n\n")
        f.write(f"Total profiles collected: {len(profiles)}\n\n")

        # Top locations
        locations = [p.get('location', '').strip() for p in profiles if p.get('location')]
        location_counts = Counter(locations)

        f.write(f"## Top Locations\n\n")
        for location, count in location_counts.most_common(10):
            f.write(f"- {location}: {count}\n")

        # Top companies
        companies = [p.get('company', '').strip().lstrip('@') for p in profiles if p.get('company')]
        company_counts = Counter(companies)

        f.write(f"\n## Top Companies\n\n")
        for company, count in company_counts.most_common(15):
            f.write(f"- {company}: {count}\n")

        f.write(f"\n## Statistics\n\n")

        repos = [int(p.get('public_repos', 0)) for p in profiles]
        if repos:
            f.write(f"- Average public repositories: {sum(repos) / len(repos):.1f}\n")

        followers = [int(p.get('followers', 0)) for p in profiles]
        if followers:
            f.write(f"- Average followers: {sum(followers) / len(followers):.1f}\n")

        emails = [p for p in profiles if p.get('email')]
        f.write(f"- Profiles with public email: {len(emails)} ({len(emails)*100/len(profiles):.1f}%)\n")

    print(f"\nSummary report saved to {output_file}")

def main():
    """Main analysis function."""
    print("Data Professionals Analysis")
    print("=" * 60)

    # Load GitHub data
    github_json = load_json_files('github_profiles_*.json')
    github_csv = load_csv_files('github_profiles_*.csv')

    # Use JSON data if available, otherwise CSV
    github_data = github_json if github_json else github_csv

    if github_data:
        analyze_github_profiles(github_data)
        generate_summary_report(github_data, 'analysis_summary.md')
    else:
        print("\nNo data files found!")
        print("Expected files: github_profiles_*.json or github_profiles_*.csv")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
