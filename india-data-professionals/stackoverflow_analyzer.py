#!/usr/bin/env python3
"""
Stack Overflow Developer Survey Analyzer
Analyzes data scientists and engineers from India in Stack Overflow survey data
"""

import requests
import pandas as pd
import zipfile
import io
from pathlib import Path

def download_survey_data(year: int = 2024) -> Path:
    """
    Download Stack Overflow Developer Survey data for a given year.

    Args:
        year: Survey year to download (2024, 2023, etc.)

    Returns:
        Path to the downloaded CSV file
    """
    # Note: The actual URL pattern varies by year
    # For 2024, check: https://survey.stackoverflow.co/2024/
    urls = {
        2024: 'https://cdn.stackoverflow.co/files/jo7n4k8s/production/49583ab61089f665dd0f4b00d97b9995755f3af4.zip',
        2023: 'https://info.stackoverflowsolutions.com/rs/719-EMH-566/images/stack-overflow-developer-survey-2023.zip',
    }

    if year not in urls:
        print(f"Survey data URL for {year} not configured")
        return None

    print(f"Downloading Stack Overflow Developer Survey {year}...")

    try:
        response = requests.get(urls[year])
        response.raise_for_status()

        # Extract ZIP file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            # Find the CSV file in the ZIP
            csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
            if csv_files:
                csv_file = csv_files[0]
                print(f"Extracting {csv_file}...")
                zip_file.extract(csv_file, '.')
                return Path(csv_file)

    except Exception as e:
        print(f"Error downloading survey data: {e}")
        return None

def analyze_india_data_professionals(csv_file: Path):
    """
    Analyze data scientists and engineers from India in the survey data.

    Args:
        csv_file: Path to the survey CSV file
    """
    print(f"\nAnalyzing data from {csv_file}...")

    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        print(f"Total responses: {len(df)}")
        print(f"Columns available: {df.columns.tolist()}\n")

        # Filter for India
        if 'Country' in df.columns:
            india_df = df[df['Country'] == 'India']
        elif 'Country ' in df.columns:  # Sometimes there's a space
            india_df = df[df['Country '] == 'India']
        else:
            print("Country column not found. Available columns:")
            print(df.columns.tolist())
            return

        print(f"Total responses from India: {len(india_df)}")

        # Identify data science-related roles
        # Column names vary by year - common ones:
        # DevType, Employment, EdLevel, YearsCode, YearsCodePro, etc.

        if 'DevType' in india_df.columns:
            # DevType contains role information
            data_roles = india_df[
                india_df['DevType'].str.contains(
                    'Data scientist|Data engineer|Data analyst|Machine learning',
                    case=False, na=False
                )
            ]

            print(f"\nData professionals in India: {len(data_roles)}")

            # Analyze role distribution
            print("\nRole Distribution:")
            roles = []
            for role_str in data_roles['DevType'].dropna():
                roles.extend([r.strip() for r in role_str.split(';')])

            role_series = pd.Series(roles)
            data_related = role_series[
                role_series.str.contains(
                    'Data|Machine|ML|AI|Analytics',
                    case=False, na=False
                )
            ]
            print(data_related.value_counts().head(10))

            # Experience levels
            if 'YearsCodePro' in data_roles.columns:
                print("\nYears of Professional Coding Experience:")
                print(data_roles['YearsCodePro'].value_counts().head(10))

            # Education
            if 'EdLevel' in data_roles.columns:
                print("\nEducation Levels:")
                print(data_roles['EdLevel'].value_counts())

            # Employment
            if 'Employment' in data_roles.columns:
                print("\nEmployment Status:")
                print(data_roles['Employment'].value_counts())

            # Save filtered data
            output_file = 'india_data_professionals_survey.csv'
            data_roles.to_csv(output_file, index=False)
            print(f"\nSaved {len(data_roles)} profiles to {output_file}")

        else:
            print("DevType column not found. Showing sample of data:")
            print(india_df.head())

    except Exception as e:
        print(f"Error analyzing data: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main execution function."""
    print("Stack Overflow Developer Survey Analyzer")
    print("=" * 50)

    # Try to download 2024 survey data
    csv_file = download_survey_data(2024)

    if csv_file and csv_file.exists():
        analyze_india_data_professionals(csv_file)
    else:
        print("\nFailed to download survey data.")
        print("You can manually download from: https://survey.stackoverflow.co/")
        print("And place the CSV file in this directory.")

if __name__ == '__main__':
    main()
