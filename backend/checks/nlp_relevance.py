from sentence_transformers import SentenceTransformer, util
from backend.config import config
import os

# Initialize model lazily or globally
print("Loading NLP Model for Relevance Checks...")
try:
    model = SentenceTransformer(config.EMBEDDING_MODEL)
except Exception as e:
    print(f"Warning: Could not load NLP model. {e}")
    model = None

def score_relevance(sow_text, metric_labels):
    if not model:
        return [{"metric": "NLP Error", "similarity": 0, "relevant": False}]
        
    if not sow_text.strip():
        # No SOW text provided
        return []

    # Encode embeddings
    sow_emb = model.encode(sow_text, convert_to_tensor=True)
    metric_emb = model.encode(metric_labels, convert_to_tensor=True)

    # Compute cosine similarity
    # We compare each metric label against the *entire* SOW text? 
    # Or chunks of SOW text?
    # Simple approach: Similarity between SOW (as one block or summary) and Label.
    # Better approach usually: Check if Label semantics exist in SOW.
    
    scores = util.cos_sim(metric_emb, sow_emb) # Shape: (n_metrics, 1)

    relevance = []
    for idx, label in enumerate(metric_labels):
        score = float(scores[idx][0])
        relevance.append({
            "metric": label,
            "similarity": score,
            "relevant": score >= config.SIMILARITY_THRESHOLD
        })

    return relevance
