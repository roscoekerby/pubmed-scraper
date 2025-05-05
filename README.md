# PubMed Scraper

A Python tool for extracting and analyzing scientific publication data from the PubMed database through NCBI's E-utilities API.

## Features

- Search PubMed database using complex queries
- Extract comprehensive metadata about scientific publications
- Automatically handle large result sets with intelligent chunking
- Robust error handling with automatic retries
- Data standardization for easier analysis
- Export results to CSV for further processing

## Installation

```bash
# Clone the repository
git clone https://github.com/roscoekerby/pubmed-scraper.git
cd pubmed-scraper

# Create and activate a virtual environment (recommended)
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.7+
- Biopython
- pandas
- numpy
- tqdm
- matplotlib (for visualization examples)

## Configuration

Before using the scraper, you need to provide your email address in the script, as required by NCBI's E-utilities service:

```python
# In pubmed_scraper.py
Entrez.email = 'your.email@example.com'  # Replace with your actual email
```

## Basic Usage

### Command Line Interface

```bash
python pubmed_scraper.py "COVID-19 AND vaccine" --max 100 --output results.csv
```

Arguments:
- First positional argument: Your PubMed search query (required)
- `--max`: Maximum number of results to retrieve (default: 100)
- `--output`: Output file name (default: pubmed_data.csv)

### Python API

```python
from pubmed_scraper import search, fetch_details, extract_data, standardize_dates, save_data

# Search for publications
query = "alzheimer disease AND neuroimaging"
results = search(query, max_results=200)
id_list = results['IdList']

# Fetch details for publications
papers = fetch_details(id_list)

# Extract data into a DataFrame
df = extract_data(papers)

# Standardize date formats
df = standardize_dates(df)

# Save to CSV
save_data(df, 'alzheimer_neuroimaging.csv')

# Access the data directly
print(f"Found {len(df)} publications")
print(f"Most recent publication: {df['Year'].max()}")
print(f"Top journals:")
print(df['Journal'].value_counts().head(5))
```

## Advanced Usage Examples

### Topic Analysis Over Time

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load previously scraped data
df = pd.read_csv('covid_data.csv')

# Convert Year to numeric
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

# Plot publications per year
plt.figure(figsize=(12, 6))
df['Year'].value_counts().sort_index().plot(kind='bar')
plt.title('COVID-19 Publications by Year')
plt.xlabel('Year')
plt.ylabel('Number of Publications')
plt.tight_layout()
plt.savefig('publications_by_year.png')
```

### Journal Impact Analysis

```python
import pandas as pd

# Load previously scraped data
df = pd.read_csv('cancer_research.csv')

# Get top journals by publication count
top_journals = df['Journal'].value_counts().head(10)

# Create a bar chart of top journals
plt.figure(figsize=(14, 7))
top_journals.plot(kind='barh')
plt.title('Top 10 Journals Publishing Cancer Research')
plt.xlabel('Number of Publications')
plt.tight_layout()
plt.savefig('top_journals.png')
```

### Author Collaboration Network

```python
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('immunology_research.csv')

# Create author collaboration network
G = nx.Graph()

# Process each paper's author list
for authors in df['Authors']:
    author_list = authors.split('; ')
    # Add edges between all author pairs
    for i, author1 in enumerate(author_list):
        if author1 != 'No Authors':
            G.add_node(author1)
            for author2 in author_list[i+1:]:
                if author2 != 'No Authors':
                    G.add_edge(author1, author2)

# Plot the network (for smaller networks)
plt.figure(figsize=(15, 15))
pos = nx.spring_layout(G, k=0.15)
nx.draw_networkx(G, pos, node_size=50, font_size=8, with_labels=True)
plt.title('Author Collaboration Network')
plt.axis('off')
plt.tight_layout()
plt.savefig('collaboration_network.png')
```

## Search Query Tips

PubMed supports a powerful query syntax:

- Boolean operators: `AND`, `OR`, `NOT`
- Field-specific searches: `[Title]`, `[Author]`, `[MeSH Terms]`, etc.
- Phrase searching: `"exact phrase"`
- Date filtering: `"2020/01/01"[Date - Publication] : "2020/12/31"[Date - Publication]`

Examples:
- `"COVID-19"[Title] AND vaccine` - Find papers with COVID-19 in the title and vaccine anywhere
- `"Alzheimer disease"[MeSH Terms] AND (biomarker OR biomarkers)` - Find papers on Alzheimer's disease biomarkers
- `"Smith J"[Author] AND cancer` - Find papers by author J. Smith on cancer

## Extracted Data Fields

| Field | Description |
|-------|-------------|
| PMID | PubMed ID |
| Title | Publication title |
| Abstract | Abstract text (if available) |
| Journal | Journal name |
| Language | Publication language |
| Year | Publication year |
| Month | Publication month (standardized to numeric format) |
| Day | Publication day |
| Authors | List of authors (separated by semicolons) |
| Keywords | Publication keywords (if available) |
| DOI | Digital Object Identifier (if available) |

## Common Issues and Solutions

### Rate Limiting

The NCBI E-utilities service has usage limits. If you exceed them, your requests may be blocked. The script includes rate limiting to help avoid this issue, but for very large queries (>10,000 publications), consider:

- Running queries during off-peak hours
- Spreading requests over multiple days
- Adding your API key if you have one

### Memory Issues

For extremely large result sets, you might encounter memory issues. Consider:

- Reducing the `max_results` parameter
- Processing results in smaller batches
- Saving intermediate results to disk

## Credits

This tool is based on the article "Scraping data from PubMed database" by Felipe Odorcyk, with enhancements for reliability, functionality, and usability.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
