# data/

Contient toutes les données du projet Nayaar, séparées par niveau de transformation.

- `raw/` — dataset Kaggle original, **immuable**, jamais modifié directement.
- `processed/` — dataset enrichi Nayaar (features métier, textes RAG, embeddings).
- `notebooks/` — notebooks Jupyter documentant le pipeline data (exploration →
  cleaning → feature engineering → embeddings).

Voir [Docs/PROJECT_CONTEXT.md](../Docs/PROJECT_CONTEXT.md) section 8 pour le détail
du pipeline.
