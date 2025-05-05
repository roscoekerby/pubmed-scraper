# PubMed Data Scraper
# This script allows you to search and retrieve scientific publications from PubMed
# Based on article by Felipe Odorcyk

# Required libraries
from Bio import Entrez
import pandas as pd
import numpy as np
import time
import argparse
from tqdm import tqdm


def search(query, max_results=10):
    """
    Search PubMed for publications matching the query
    Returns a list of PubMed IDs
    """
    # IMPORTANT: Always provide your email when using NCBI's E-utilities
    Entrez.email = 'your.email@example.com'  # Replace with your actual email

    # Perform the search
    handle = Entrez.esearch(
        db='pubmed',
        sort='relevance',
        retmax=str(max_results),
        retmode='xml',
        term=query
    )

    # Parse the results
    results = Entrez.read(handle)
    handle.close()

    return results


def fetch_details(id_list, chunk_size=100):
    """
    Fetch details for a list of PubMed IDs
    Returns publication details
    """
    all_papers = []

    # Process IDs in chunks to avoid server issues
    for i in tqdm(range(0, len(id_list), chunk_size), desc="Fetching publication details"):
        chunk = id_list[i:i + chunk_size]
        ids = ','.join(chunk)

        # IMPORTANT: Always provide your email when using NCBI's E-utilities
        Entrez.email = 'roscoe.kerby@gmail.com'  # Replace with your actual email

        tries = 0
        max_tries = 3
        while tries < max_tries:
            try:
                # Fetch the details
                handle = Entrez.efetch(
                    db='pubmed',
                    retmode='xml',
                    id=ids
                )

                # Parse the results
                results = Entrez.read(handle)
                handle.close()

                # Add to our collection
                if 'PubmedArticle' in results:
                    all_papers.extend(results['PubmedArticle'])

                # Successful fetch, break the retry loop
                break

            except Exception as e:
                tries += 1
                print(f"Error fetching details (attempt {tries}/{max_tries}): {e}")
                if tries < max_tries:
                    # Exponential backoff
                    time_to_wait = 2 ** tries
                    print(f"Waiting {time_to_wait} seconds before retrying...")
                    time.sleep(time_to_wait)
                else:
                    print(f"Failed to fetch details for chunk {i}")

        # Be nice to NCBI servers
        time.sleep(0.5)

    return all_papers


def extract_data(papers):
    """
    Extract relevant data from the papers and create a DataFrame
    """
    data = {
        'PMID': [],
        'Title': [],
        'Abstract': [],
        'Journal': [],
        'Language': [],
        'Year': [],
        'Month': [],
        'Day': [],
        'Authors': [],
        'Keywords': [],
        'DOI': []
    }

    for paper in tqdm(papers, desc="Extracting publication data"):
        # Get the MedlineCitation section where most data is stored
        citation = paper.get('MedlineCitation', {})
        article = citation.get('Article', {})

        # Extract PMID
        pmid = citation.get('PMID', 'No PMID')
        data['PMID'].append(str(pmid))

        # Extract title
        title = article.get('ArticleTitle', 'No Title')
        data['Title'].append(title)

        # Extract abstract
        abstract = 'No Abstract'
        abstract_section = article.get('Abstract', {})
        if abstract_section and 'AbstractText' in abstract_section:
            try:
                # Sometimes AbstractText is a list of sections, sometimes a single string
                abstract_text = abstract_section['AbstractText']
                if isinstance(abstract_text, list):
                    abstract = ' '.join([str(text) for text in abstract_text])
                else:
                    abstract = str(abstract_text)
            except:
                pass
        data['Abstract'].append(abstract)

        # Extract journal
        journal = article.get('Journal', {}).get('Title', 'No Journal')
        data['Journal'].append(journal)

        # Extract language
        language = 'Unknown'
        if 'Language' in article and len(article['Language']) > 0:
            language = article['Language'][0]
        data['Language'].append(language)

        # Extract dates
        journal_issue = article.get('Journal', {}).get('JournalIssue', {})
        pub_date = journal_issue.get('PubDate', {})

        year = pub_date.get('Year', 'No Data')
        data['Year'].append(year)

        month = pub_date.get('Month', 'No Data')
        data['Month'].append(month)

        day = pub_date.get('Day', 'No Data')
        data['Day'].append(day)

        # Extract authors
        authors = []
        author_list = article.get('AuthorList', [])
        if author_list:
            for author in author_list:
                if 'LastName' in author and 'ForeName' in author:
                    authors.append(f"{author['LastName']} {author['ForeName']}")
                elif 'LastName' in author:
                    authors.append(author['LastName'])
                elif 'CollectiveName' in author:
                    authors.append(author['CollectiveName'])
        data['Authors'].append('; '.join(authors) if authors else 'No Authors')

        # Extract keywords
        keywords = []
        keyword_list = citation.get('KeywordList', [])
        if keyword_list and len(keyword_list) > 0:
            keywords = [str(keyword) for keyword in keyword_list[0]]
        data['Keywords'].append('; '.join(keywords) if keywords else 'No Keywords')

        # Extract DOI
        doi = 'No DOI'
        article_id_list = paper.get('PubmedData', {}).get('ArticleIdList', [])
        if article_id_list:
            for id_item in article_id_list:
                if id_item.attributes.get('IdType') == 'doi':
                    doi = str(id_item)
                    break
        data['DOI'].append(doi)

    return pd.DataFrame(data)


def standardize_dates(df):
    """
    Standardize the month format in the DataFrame
    """
    month_mapping = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    # Replace month names with numbers
    for month_name, month_num in month_mapping.items():
        df['Month'] = df['Month'].replace(month_name, month_num)

    # Replace 'No Data' with NaN
    df['Month'] = df['Month'].replace('No Data', np.nan)
    df['Day'] = df['Day'].replace('No Data', np.nan)
    df['Year'] = df['Year'].replace('No Data', np.nan)

    return df


def save_data(df, output_file='pubmed_data.csv'):
    """
    Save the DataFrame to a CSV file
    """
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='PubMed Data Scraper')
    parser.add_argument('query', type=str, help='Search query for PubMed')
    parser.add_argument('--max', type=int, default=100, help='Maximum number of results to retrieve')
    parser.add_argument('--output', type=str, default='pubmed_data.csv', help='Output file name')
    args = parser.parse_args()

    print(f"Searching PubMed for: {args.query}")
    print(f"Maximum results: {args.max}")

    # Search for papers
    results = search(args.query, max_results=args.max)
    id_list = results['IdList']

    print(f"Found {len(id_list)} publications")

    # Fetch details for the papers
    papers = fetch_details(id_list)

    # Extract data and create DataFrame
    df = extract_data(papers)

    # Standardize dates
    df = standardize_dates(df)

    # Save the data
    save_data(df, output_file=args.output)

    print("Done!")


if __name__ == "__main__":
    main()