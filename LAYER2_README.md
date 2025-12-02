# Layer 2: Theme Extraction & Classification

## Overview
Layer 2 uses advanced ML techniques to automatically discover themes in review data through embedding-based clustering and LLM-powered labeling.

**Reference**: [Cluster Chatter: HDBSCAN + LLM](https://medium.com/@mrsirsh/cluster-chatter-hdbscan-llm-1ec89120eae6)

## Architecture

```
Layer 2: Theme Extraction & Classification
├─ Embedding Generation (vector representations)
├─ Theme Clustering (HDBSCAN density-based)
├─ Theme Labeling (LLM generates human-readable names)
└─ Theme Limit Enforcer (merge or prioritize to max 5)
```

## Components

### 1. Embedding Generation
Converts review text into dense vector representations using Sentence Transformers.

**Model Options**:
- `all-MiniLM-L6-v2` (default): Fast, good quality, 384 dimensions
- `all-mpnet-base-v2`: Higher quality, 768 dimensions, slower
- `paraphrase-multilingual-MiniLM-L12-v2`: Multilingual support

**Example**:
```python
from layer2_themes import EmbeddingGenerator

generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
embeddings = generator.generate(review_texts)
# Output: numpy array (n_reviews, 384)
```

### 2. Theme Clustering (HDBSCAN)
Groups similar reviews using hierarchical density-based clustering.

**Why HDBSCAN?**
- No need to specify number of clusters (auto-discovers themes)
- Handles noise/outliers gracefully
- Works well with high-dimensional embeddings
- Robust to varying cluster densities

**Parameters**:
- `min_cluster_size=15`: Minimum reviews per theme
- `min_samples=5`: Core point threshold (conservative)
- `metric='euclidean'`: Distance metric

**Example**:
```python
from layer2_themes import ThemeClusterer

clusterer = ThemeClusterer(min_cluster_size=15, min_samples=5)
clusterer.fit(embeddings)

print(clusterer.labels_)  # Cluster assignments
print(clusterer.get_cluster_stats())
```

### 3. Theme Labeling (LLM)
Generates human-readable theme names and descriptions using Gemini.

**Process**:
1. Extract 10 most representative reviews per cluster (by membership probability)
2. Send to LLM with structured prompt
3. LLM returns theme name (2-4 words) + description (1 sentence)
4. Fallback to keyword extraction if LLM unavailable

**Example**:
```python
from layer2_themes import ThemeLabeler

labeler = ThemeLabeler()
result = labeler.label_cluster(cluster_reviews, cluster_probabilities)

# Output:
# {
#   'theme_name': 'KYC Verification Delays',
#   'description': 'Users reporting slow identity verification with document upload issues'
# }
```

### 4. Theme Limit Enforcer
Ensures maximum of 5 themes by merging or prioritizing.

**Strategy**:
- Keep top 4 themes by size
- Merge remaining themes into "Other"
- Preserves majority of feedback (top themes)

**Example**:
```python
from layer2_themes import ThemeLimitEnforcer

# Input: 8 themes
final_themes = ThemeLimitEnforcer.enforce_limit(themes, reviews, labels, embeddings)

# Output: 5 themes (top 4 + "Other")
```

## Full Pipeline

```python
from layer2_themes import Layer2Pipeline

# Initialize pipeline
pipeline = Layer2Pipeline(
    embedding_model='all-MiniLM-L6-v2',
    min_cluster_size=15,
    min_samples=5,
    max_themes=5
)

# Process reviews
reviews = [
    {'review_id': 'r1', 'text': 'KYC verification is slow...'},
    {'review_id': 'r2', 'text': 'Payment failed but deducted...'},
    # ... more reviews
]

enriched_reviews, metadata = pipeline.process(reviews)

# enriched_reviews: Each review now has:
#   - 'theme': assigned theme name
#   - 'theme_confidence': membership probability (0-1)
#   - 'cluster_id': internal cluster ID

# metadata: 
#   - 'themes': List of discovered themes with sizes
#   - 'clustering_stats': HDBSCAN statistics
#   - 'embedding_model': Model used
```

## Installation

```bash
pip install -r requirements.txt
```

**Required packages**:
- `sentence-transformers`: Embedding generation
- `hdbscan`: Density-based clustering
- `scikit-learn`: ML utilities
- `google-generativeai`: Theme labeling

## Testing

Run component tests:
```bash
py test_layer2.py
```

**Tests cover**:
1. Embedding generation
2. HDBSCAN clustering
3. LLM theme labeling
4. Theme limit enforcement
5. Full pipeline end-to-end

## Output Format

### Enriched Reviews
```python
{
    'review_id': 'abc123',
    'text': 'KYC verification took 5 days...',
    'theme': 'KYC Verification Delays',
    'theme_confidence': 0.92,
    'cluster_id': 0
}
```

### Theme Metadata
```python
{
    'themes': [
        {
            'cluster_id': 0,
            'theme_name': 'KYC Verification Delays',
            'description': 'Users reporting slow identity verification...',
            'size': 45
        },
        {
            'cluster_id': 1,
            'theme_name': 'Payment Failures',
            'description': 'Payment deductions without confirmation...',
            'size': 38
        },
        # ... up to 5 themes
    ],
    'clustering_stats': {
        'n_clusters': 8,
        'n_noise': 12,
        'cluster_sizes': {0: 45, 1: 38, ...},
        'total_points': 200
    },
    'embedding_model': 'all-MiniLM-L6-v2',
    'total_reviews': 200
}
```

## Advantages over Keyword Matching

| Aspect | Layer 2 (Embeddings + Clustering) | Keyword Matching |
|--------|-----------------------------------|------------------|
| **Discovery** | Auto-discovers themes from data | Requires pre-defined categories |
| **Semantic** | Understands meaning & context | Literal word matching only |
| **Flexible** | Adapts to new topics | Rigid, misses new issues |
| **Granularity** | Finds nuanced sub-themes | Coarse categories |
| **Noise handling** | HDBSCAN flags outliers | All reviews forced into buckets |

## Performance Tips

1. **Batch size**: Process reviews in batches of 100-500 for efficiency
2. **Min cluster size**: Increase for noisy data (15-20), decrease for sparse data (10)
3. **Embedding model**: Use `all-MiniLM-L6-v2` for speed, `all-mpnet-base-v2` for quality
4. **GPU acceleration**: Sentence transformers auto-use GPU if available

## Integration Example

```python
from layer1_import import Layer1Pipeline
from layer2_themes import Layer2Pipeline

# Layer 1: Import & Validation
layer1 = Layer1Pipeline('com.nextbillion.groww')
valid_reviews, _ = layer1.process_batch(count=200)

# Layer 2: Theme Extraction
layer2 = Layer2Pipeline(max_themes=5)
enriched_reviews, theme_metadata = layer2.process(valid_reviews)

# Now reviews have themes for downstream processing
```

## Troubleshooting

**Issue**: `ImportError: sentence-transformers not installed`
```bash
pip install sentence-transformers
```

**Issue**: `ImportError: hdbscan not installed`
```bash
pip install hdbscan
```

**Issue**: Too many noise points
- Decrease `min_cluster_size` (e.g., 10 instead of 15)
- Decrease `min_samples` (e.g., 3 instead of 5)

**Issue**: Too many themes (>10)
- Increase `min_cluster_size` to force larger clusters
- The enforcer will still limit to 5

**Issue**: LLM labeling fails
- Check `GEMINI_API_KEY` is set
- System falls back to keyword extraction automatically

## Next Steps

After Layer 2, reviews are enriched with themes and ready for:
- **Layer 3**: Summarization (weekly pulse generation)
- **Layer 4**: Email delivery
- **Analytics**: Theme trending over time
