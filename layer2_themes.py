"""
Layer 2: Theme Extraction & Classification
- Embedding Generation (vector representations)
- Theme Clustering (HDBSCAN or LLM-based)
- Theme Labeling (LLM generates human-readable names)
- Theme Limit Enforcer (merge or prioritize to max 5)

Reference: https://medium.com/@mrsirsh/cluster-chatter-hdbscan-llm-1ec89120eae6
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
    EMBEDDINGS_AVAILABLE = False

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    logger.warning("hdbscan not installed. Install with: pip install hdbscan")
    HDBSCAN_AVAILABLE = False

try:
    import google.generativeai as genai
    _gemini_api = os.getenv("GEMINI_API_KEY")
    if _gemini_api:
        genai.configure(api_key=_gemini_api)
    LLM_AVAILABLE = bool(_gemini_api)
except Exception:
    LLM_AVAILABLE = False


class EmbeddingGenerator:
    """Generate vector embeddings for review text using sentence transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Sentence transformer model name
                - 'all-MiniLM-L6-v2': Fast, good quality (default)
                - 'all-mpnet-base-v2': Higher quality, slower
                - 'paraphrase-multilingual-MiniLM-L12-v2': Multilingual support
        """
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError("sentence-transformers required. Install: pip install sentence-transformers")
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def generate(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of review texts
            batch_size: Batch size for encoding
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings


class ThemeClusterer:
    """Cluster reviews into themes using HDBSCAN."""
    
    def __init__(self, 
                 min_cluster_size: int = 15,
                 min_samples: int = 5,
                 metric: str = 'euclidean'):
        """
        Initialize HDBSCAN clusterer.
        
        Args:
            min_cluster_size: Minimum size of clusters (default: 15)
            min_samples: Conservative parameter for core points (default: 5)
            metric: Distance metric (euclidean, cosine, etc.)
        """
        if not HDBSCAN_AVAILABLE:
            raise ImportError("hdbscan required. Install: pip install hdbscan")
        
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.metric = metric
        self.clusterer = None
        self.labels_ = None
        self.probabilities_ = None
    
    def fit(self, embeddings: np.ndarray) -> 'ThemeClusterer':
        """
        Fit HDBSCAN on embeddings.
        
        Args:
            embeddings: numpy array of embeddings
            
        Returns:
            self
        """
        logger.info(f"Clustering {len(embeddings)} embeddings with HDBSCAN")
        logger.info(f"Parameters: min_cluster_size={self.min_cluster_size}, min_samples={self.min_samples}")
        
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric=self.metric,
            cluster_selection_method='eom',  # Excess of Mass
            prediction_data=True
        )
        
        self.labels_ = self.clusterer.fit_predict(embeddings)
        self.probabilities_ = self.clusterer.probabilities_
        
        # Count clusters (excluding noise cluster -1)
        unique_labels = set(self.labels_)
        n_clusters = len(unique_labels - {-1})
        n_noise = list(self.labels_).count(-1)
        
        logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")
        
        return self
    
    def get_cluster_stats(self) -> Dict:
        """Get clustering statistics."""
        if self.labels_ is None:
            return {}
        
        unique_labels = set(self.labels_)
        cluster_counts = Counter(self.labels_)
        
        stats = {
            'n_clusters': len(unique_labels - {-1}),
            'n_noise': cluster_counts.get(-1, 0),
            'cluster_sizes': {
                int(label): count 
                for label, count in cluster_counts.items() 
                if label != -1
            },
            'total_points': len(self.labels_)
        }
        
        return stats


class ThemeLabeler:
    """Generate human-readable theme labels using LLM."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize theme labeler.
        
        Args:
            model_name: Gemini model name (default: gemini-1.5-flash)
        """
        if not LLM_AVAILABLE:
            logger.warning("Gemini API not configured. Theme labeling will use fallback.")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    def _extract_representative_reviews(self, 
                                       reviews: List[str], 
                                       probabilities: np.ndarray,
                                       max_reviews: int = 10) -> List[str]:
        """Extract most representative reviews from a cluster."""
        # Sort by probability (cluster membership confidence)
        sorted_indices = np.argsort(probabilities)[::-1]
        top_indices = sorted_indices[:max_reviews]
        return [reviews[i] for i in top_indices]
    
    def label_cluster(self, 
                     cluster_reviews: List[str],
                     cluster_probabilities: np.ndarray) -> Dict[str, str]:
        """
        Generate theme label and description for a cluster.
        
        Args:
            cluster_reviews: Reviews in this cluster
            cluster_probabilities: Membership probabilities for each review
            
        Returns:
            dict with 'theme_name' and 'description'
        """
        # Get representative reviews
        representative = self._extract_representative_reviews(
            cluster_reviews, 
            cluster_probabilities,
            max_reviews=10
        )
        
        if not LLM_AVAILABLE:
            # Fallback: simple keyword extraction
            return self._fallback_labeling(representative)
        
        # LLM-based labeling
        prompt = self._build_labeling_prompt(representative, len(cluster_reviews))
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            result = json.loads(response.text or "{}")
            
            return {
                'theme_name': result.get('theme_name', 'Unknown Theme'),
                'description': result.get('description', '')
            }
        except Exception as e:
            logger.error(f"LLM labeling failed: {e}")
            return self._fallback_labeling(representative)
    
    def _build_labeling_prompt(self, reviews: List[str], total_count: int) -> str:
        """Build prompt for LLM theme labeling."""
        reviews_text = "\n".join([f"{i+1}. {r[:200]}" for i, r in enumerate(reviews)])
        
        prompt = f"""You are analyzing customer reviews to identify themes.

Below are {len(reviews)} representative reviews from a cluster of {total_count} similar reviews:

{reviews_text}

Tasks:
1. Identify the main theme these reviews share
2. Create a concise, descriptive theme name (2-4 words)
3. Write a brief description (1 sentence)

Guidelines:
- Theme name should be specific and actionable (e.g., "KYC Verification Delays" not "Issues")
- Focus on what users are discussing, not just sentiment
- Avoid generic labels like "App Experience" or "Feedback"

Return ONLY valid JSON:
{{
  "theme_name": "...",
  "description": "..."
}}"""
        return prompt
    
    def _fallback_labeling(self, reviews: List[str]) -> Dict[str, str]:
        """Fallback labeling using keyword extraction."""
        # Simple keyword frequency
        from collections import Counter
        import re
        
        words = []
        for review in reviews[:5]:
            words.extend(re.findall(r'\b\w+\b', review.lower()))
        
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'not', 'very', 'just', 'even', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
        top_words = Counter(filtered_words).most_common(3)
        
        theme_name = " ".join([w[0].capitalize() for w in top_words[:2]]) or "General Feedback"
        
        return {
            'theme_name': theme_name,
            'description': f"Reviews discussing {theme_name.lower()}"
        }


class ThemeLimitEnforcer:
    """Merge or prioritize themes to ensure maximum of 5 themes."""
    
    MAX_THEMES = 5
    
    @staticmethod
    def enforce_limit(themes: List[Dict], 
                     reviews: List[str],
                     labels: np.ndarray,
                     embeddings: np.ndarray) -> List[Dict]:
        """
        Reduce themes to maximum of 5 by merging or prioritizing.
        
        Args:
            themes: List of theme dicts with 'cluster_id', 'theme_name', 'description', 'size'
            reviews: Original review texts
            labels: Cluster labels for each review
            embeddings: Review embeddings
            
        Returns:
            List of max 5 themes, sorted by size
        """
        if len(themes) <= ThemeLimitEnforcer.MAX_THEMES:
            logger.info(f"Theme count ({len(themes)}) within limit")
            return sorted(themes, key=lambda x: x['size'], reverse=True)
        
        logger.info(f"Enforcing theme limit: {len(themes)} → {ThemeLimitEnforcer.MAX_THEMES}")
        
        # Strategy: Keep top 4 by size, merge remaining into "Other"
        sorted_themes = sorted(themes, key=lambda x: x['size'], reverse=True)
        
        top_themes = sorted_themes[:ThemeLimitEnforcer.MAX_THEMES - 1]
        merged_themes = sorted_themes[ThemeLimitEnforcer.MAX_THEMES - 1:]
        
        # Create "Other" theme from merged
        other_size = sum(t['size'] for t in merged_themes)
        other_cluster_ids = [t['cluster_id'] for t in merged_themes]
        
        other_theme = {
            'cluster_id': -2,  # Special ID for merged theme
            'theme_name': 'Other',
            'description': 'Mixed feedback on various topics',
            'size': other_size,
            'merged_from': other_cluster_ids
        }
        
        final_themes = top_themes + [other_theme]
        
        logger.info(f"Final themes: {[t['theme_name'] for t in final_themes]}")
        
        return final_themes


class Layer2Pipeline:
    """Orchestrates Layer 2: Theme Extraction & Classification."""
    
    def __init__(self,
                 embedding_model: str = 'all-MiniLM-L6-v2',
                 min_cluster_size: int = 15,
                 min_samples: int = 5,
                 max_themes: int = 5):
        """
        Initialize Layer 2 pipeline.
        
        Args:
            embedding_model: Sentence transformer model
            min_cluster_size: HDBSCAN min cluster size
            min_samples: HDBSCAN min samples
            max_themes: Maximum number of themes (default: 5)
        """
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.clusterer = ThemeClusterer(min_cluster_size, min_samples)
        self.labeler = ThemeLabeler()
        self.max_themes = max_themes
    
    def process(self, reviews: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Process reviews through Layer 2 pipeline.
        
        Args:
            reviews: List of review dicts with 'text' field
            
        Returns:
            (enriched_reviews, theme_metadata)
            - enriched_reviews: Reviews with 'theme' and 'theme_confidence' added
            - theme_metadata: Dict with theme info and statistics
        """
        logger.info("="*60)
        logger.info("LAYER 2: THEME EXTRACTION & CLASSIFICATION")
        logger.info("="*60)
        
        # Extract texts
        texts = [r.get('text', '') for r in reviews]
        
        # Step 1: Generate embeddings
        logger.info("Step 1: Generating embeddings...")
        embeddings = self.embedding_generator.generate(texts)
        
        # Step 2: Cluster themes
        logger.info("Step 2: Clustering themes with HDBSCAN...")
        self.clusterer.fit(embeddings)
        labels = self.clusterer.labels_
        probabilities = self.clusterer.probabilities_
        
        cluster_stats = self.clusterer.get_cluster_stats()
        logger.info(f"Clustering stats: {cluster_stats}")
        
        # Step 3: Label themes
        logger.info("Step 3: Generating theme labels with LLM...")
        themes = []
        unique_labels = set(labels) - {-1}  # Exclude noise
        
        for cluster_id in sorted(unique_labels):
            cluster_mask = labels == cluster_id
            cluster_reviews = [texts[i] for i, mask in enumerate(cluster_mask) if mask]
            cluster_probs = probabilities[cluster_mask]
            
            label_info = self.labeler.label_cluster(cluster_reviews, cluster_probs)
            
            themes.append({
                'cluster_id': int(cluster_id),
                'theme_name': label_info['theme_name'],
                'description': label_info['description'],
                'size': len(cluster_reviews)
            })
            
            logger.info(f"  Cluster {cluster_id}: {label_info['theme_name']} ({len(cluster_reviews)} reviews)")
        
        # Step 4: Enforce theme limit
        logger.info(f"Step 4: Enforcing max {self.max_themes} themes...")
        final_themes = ThemeLimitEnforcer.enforce_limit(
            themes, texts, labels, embeddings
        )
        
        # Enrich reviews with theme assignments
        enriched_reviews = []
        for i, review in enumerate(reviews):
            cluster_id = int(labels[i])
            
            # Find theme for this cluster
            theme_name = "Noise"
            if cluster_id != -1:
                theme_obj = next((t for t in final_themes if t['cluster_id'] == cluster_id), None)
                if not theme_obj:
                    # Review was in a merged cluster
                    theme_obj = next((t for t in final_themes if t.get('cluster_id') == -2), None)
                theme_name = theme_obj['theme_name'] if theme_obj else "Other"
            
            enriched_review = review.copy()
            enriched_review['theme'] = theme_name
            enriched_review['theme_confidence'] = float(probabilities[i])
            enriched_review['cluster_id'] = cluster_id
            enriched_reviews.append(enriched_review)
        
        # Build metadata
        theme_metadata = {
            'themes': final_themes,
            'clustering_stats': cluster_stats,
            'embedding_model': self.embedding_generator.model_name,
            'total_reviews': len(reviews)
        }
        
        logger.info("="*60)
        logger.info("LAYER 2 COMPLETE")
        logger.info("="*60)
        
        return enriched_reviews, theme_metadata
