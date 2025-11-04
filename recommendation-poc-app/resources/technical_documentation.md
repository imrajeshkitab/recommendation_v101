
# Technical Documentation: Recommendation Algorithms

This document provides a technical explanation of the recommendation algorithms used in the recommendation-poc-app. It includes an analysis of time complexity, scalability, and a comparison with vector embedding-based approaches.

## 1. Questionnaire-Based Recommendation

This algorithm recommends content to users based on their answers to a questionnaire.

### 1.1. Data Flow

1.  **Questionnaire**: The user is presented with a series of questions. Each answer option is associated with a set of predefined tags.
2.  **Tag Accumulation**: As the user answers the questions, the tags associated with their chosen answers are accumulated into a user profile. This profile is a dictionary where keys are tag categories (e.g., `primary_need`, `cognitive_style`) and values are lists of tags.
3.  **Scoring**: The user's accumulated tags are compared against the tags of each content item in the database.
4.  **Ranking**: Content items are ranked based on their similarity score, and the top-scoring items are presented to the user as recommendations.

### 1.2. Scoring Algorithm: Jaccard Similarity

The core of the scoring mechanism is the **Jaccard Similarity** index. This metric is used to gauge the similarity between two sets of tags.

The formula for Jaccard Similarity is:

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

Where:
*   `A` is the set of user's tags for a specific category.
*   `B` is the set of content's tags for the same category.
*   `|A ∩ B|` is the number of tags common to both sets (intersection).
*   `|A ∪ B|` is the total number of unique tags in both sets (union).

The final score for a content item is the average of the Jaccard scores across all tag categories.

### 1.3. Execution Flow and Calculation Strategy

The recommendation scores are calculated **sequentially, after each question is answered**.

*   **Process**: When a user selects an answer, their profile of accumulated tags is immediately updated. The application then recalculates the scores for all content items based on this new profile.
*   **Rationale**: This "live" recalculation provides an interactive and dynamic user experience. The user can see how their recommendations might evolve as they provide more information. For a small number of content items, this approach is effective as it gives immediate feedback. However, as we will see in the complexity analysis, this strategy has scalability limitations.

## 2. Algorithmic Analysis

### 2.1. Time Complexity

Let:
*   `C` be the total number of content items.
*   `Q` be the number of questions in the questionnaire.
*   `K` be the number of tag categories.
*   `U_avg` be the average number of tags in the user's profile.
*   `T_avg` be the average number of tags per content item.

The calculation for a single content item involves computing the Jaccard similarity for each of the `K` categories. The complexity of a single Jaccard similarity calculation is proportional to the sum of the sizes of the two sets, approximately `O(U_avg + T_avg)`.

The total time complexity for scoring all content items is:
`O(C * K * (U_avg + T_avg))`

Since this calculation is performed after each of the `Q` questions, the total complexity for a full questionnaire session is:
`O(Q * C * K * (U_avg + T_avg))`

Given that `Q`, `K`, `U_avg`, and `T_avg` are relatively small and constant, the complexity is dominated by the number of content items, `C`. Thus, the effective complexity is **O(C)** for each recalculation.

### 2.2. Scalability Analysis

The current Jaccard-based approach has significant scalability challenges:

*   **Linear Scaling with Content**: The `O(C)` complexity means that the time to calculate recommendations grows linearly with the number of content items. If the content library grows from 1,000 to 1,000,000 items, the calculation time will increase by a factor of 1,000, making real-time recalculation infeasible.
*   **High Computational Load**: The system performs a full scan of the database for every user interaction during the questionnaire. This is computationally expensive and does not scale well with a large number of concurrent users.

This approach is suitable for a Proof of Concept (PoC) with a small dataset but is not a viable long-term solution for a large-scale production system.

## 3. Comparison with Vector Embedding-Based Recommendation

A more scalable and modern approach to recommendation systems is based on vector embeddings.

### 3.1. Vector Embedding Approach

1.  **Offline Embedding Generation**:
    *   **Content Embeddings**: All content items (e.g., their text, titles, and metadata) are converted into high-dimensional numerical vectors (embeddings) using a deep learning model (like Sentence-BERT). This is a computationally intensive process but is performed offline.
    *   **User Profile Embeddings**: A user's profile (derived from their questionnaire answers or interaction history) is also converted into a vector in the same embedding space.

2.  **Online Recommendation**:
    *   **Similarity Search**: Recommendations are generated by finding the content embeddings that are "closest" to the user's profile embedding. This is typically done using cosine similarity.
    *   **Efficient Search**: Instead of a linear scan, this "nearest neighbor" search can be performed with extreme efficiency using specialized libraries like **Faiss** (from Facebook AI) or **Annoy** (from Spotify). These libraries use algorithms like Approximate Nearest Neighbor (ANN) to find the closest matches in sub-linear time, often `O(log C)`.

### 3.2. Scalability and Performance Comparison

| Aspect                | Jaccard Similarity (Current)                                | Vector Embedding (Proposed)                                       |
| --------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| **Scalability**       | **Low**. `O(C)` complexity per user action. Not suitable for large datasets. | **High**. `O(log C)` complexity at recommendation time. Scales to millions of items. |
| **Performance**       | **Slow** for large `C`. Recalculation becomes a bottleneck. | **Very Fast**. Near-instantaneous recommendations even with large datasets. |
| **Recommendation Quality** | Good, but limited to explicit tags. Misses semantic nuances. | **Superior**. Captures deep semantic relationships between words and concepts, leading to more relevant and serendipitous recommendations. |
| **Implementation Complexity** | Simple and easy to implement. Ideal for a PoC. | More complex, requiring knowledge of deep learning models, embedding generation, and vector databases/libraries. |

**Conclusion**: The vector embedding approach is vastly more scalable and typically provides higher-quality recommendations.

## 4. Conclusion and Future Improvements

The current Jaccard similarity-based algorithm is a simple and effective solution for this Proof of Concept. Its "calculate-on-every-answer" strategy provides a responsive UI for a small dataset.

However, for a production system, it is crucial to migrate to a **vector embedding-based recommendation engine**. This would involve:
1.  Setting up an offline pipeline to generate embeddings for all content.
2.  Implementing a service to generate user profile embeddings from questionnaire answers.
3.  Integrating a fast vector search library (like Faiss) to enable scalable, real-time recommendations.

This architectural change would ensure the system remains fast and responsive as the content library and user base grow.
