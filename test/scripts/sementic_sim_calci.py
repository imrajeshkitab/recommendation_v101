import os
import sys
import google.generativeai as genai
import math
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def cosine_similarity(vec_a, vec_b):
    """Calculates the cosine similarity between two vectors."""
    
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        print("Error: Invalid vectors provided.")
        return 0

    dot_product = 0
    mag_a = 0
    mag_b = 0

    for i in range(len(vec_a)):
        dot_product += vec_a[i] * vec_b[i]
        mag_a += vec_a[i] * vec_a[i]
        mag_b += vec_b[i] * vec_b[i]

    mag_a = math.sqrt(mag_a)
    mag_b = math.sqrt(mag_b)

    if mag_a == 0 or mag_b == 0:
        print("Error: Zero-magnitude vector.")
        return 0

    return dot_product / (mag_a * mag_b)


def calculate_semantic_similarity(text1, text2):
    """
    Calculate semantic similarity between two texts using Gemini embeddings.
    
    Args:
        text1 (str): First text to compare
        text2 (str): Second text to compare
    
    Returns:
        float: Cosine similarity score between 0 and 1
    """
    
    # --- 1. Get API Key ---
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: API key not found.")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file.")
        return None

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring API: {e}")
        return None

    # --- 2. Get Embeddings ---
    model_name = 'models/embedding-001'
    
    try:
        print("Fetching embeddings...")
        result = genai.embed_content(
            model=model_name,
            content=[text1, text2],
            task_type="SEMANTIC_SIMILARITY"
        )
        
        embeddings = result['embedding']
        
        if len(embeddings) < 2:
            print("Error: API did not return embeddings for both texts.")
            return None
        
        vec1 = embeddings[0]
        vec2 = embeddings[1]
        
    except Exception as e:
        print(f"Error fetching embeddings: {e}")
        return None
    
    # --- 3. Calculate Similarity ---
    similarity = cosine_similarity(vec1, vec2)
    
    return similarity


def main():
    """Main function to handle command line arguments or interactive input."""
    
    print("=" * 70)
    print("🔍 Semantic Similarity Calculator")
    print("=" * 70)
    
    # Check if arguments were provided
    if len(sys.argv) == 3:
        # Use command line arguments
        text1 = sys.argv[1]
        text2 = sys.argv[2]
    elif len(sys.argv) == 1:
        # Interactive mode
        print("\nEnter two texts to compare their semantic similarity.")
        print("-" * 70)
        text1 = input("Text 1: ").strip()
        text2 = input("Text 2: ").strip()
        
        if not text1 or not text2:
            print("Error: Both texts must be non-empty.")
            return
    else:
        print("Usage:")
        print("  Interactive mode:  python3 calculate_similarity.py")
        print("  Command line mode: python3 calculate_similarity.py \"text1\" \"text2\"")
        print("\nExamples:")
        print("  python3 calculate_similarity.py \"young\" \"age 10-25\"")
        print("  python3 calculate_similarity.py \"happy\" \"joyful\"")
        return
    
    print("\n" + "-" * 70)
    print(f"Text 1: '{text1}'")
    print(f"Text 2: '{text2}'")
    print("-" * 70)
    
    # Calculate similarity
    similarity = calculate_semantic_similarity(text1, text2)
    
    if similarity is not None:
        print("\n" + "=" * 70)
        print(f"✨ Semantic Similarity Score: {similarity:.6f}")
        print("=" * 70)
        
        # Provide interpretation
        print("\nInterpretation:")
        if similarity >= 0.9:
            print("  🟢 Very High Similarity - Texts are semantically very similar")
        elif similarity >= 0.75:
            print("  🟢 High Similarity - Texts are quite similar in meaning")
        elif similarity >= 0.6:
            print("  🟡 Moderate Similarity - Texts share some semantic relationship")
        elif similarity >= 0.4:
            print("  🟡 Low-Moderate Similarity - Texts have some connection")
        elif similarity >= 0.2:
            print("  🟠 Low Similarity - Texts are somewhat different")
        else:
            print("  🔴 Very Low Similarity - Texts are semantically quite different")
        
        print("\nNote: Scores range from 0 (completely different) to 1 (identical)")
        print("=" * 70)


if __name__ == "__main__":
    main()

