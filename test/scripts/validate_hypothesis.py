import os
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

def validate_hypothesis():
    """
    Fetches embeddings for multiple age-related test cases and validates the hypothesis:
    sim(age_term, matching_age_range) > sim(age_term, different_age_range)
    """
    
    # --- 1. Get API Key ---
    # Check for API key in .env file or environment variables
    # Accepts either GEMINI_API_KEY or GOOGLE_API_KEY
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: API key not found.")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file.")
        return

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring API: {e}")
        return

    # --- 2. Define Test Cases ---
    model_name = 'models/embedding-001'
    
    # Format: (age_term, matching_age_range, different_age_range)
    test_cases = [
        # Youth-related terms
        ('young', 'age 10-25', 'age 50-60'),
        ('young person', 'age 15-25', 'age 65-75'),
        ('youth', 'age 12-24', 'age 55-70'),
        ('teenager', 'age 13-19', 'age 40-50'),
        ('teen', 'age 13-17', 'age 60-70'),
        ('adolescent', 'age 12-18', 'age 45-60'),
        ('child', 'age 5-12', 'age 50-65'),
        ('kid', 'age 6-14', 'age 55-70'),
        ('infant', 'age 0-2', 'age 40-60'),
        ('toddler', 'age 1-3', 'age 50-70'),
        ('preschooler', 'age 3-5', 'age 45-65'),
        
        # Young adult
        ('young adult', 'age 18-30', 'age 60-75'),
        ('college age', 'age 18-24', 'age 50-65'),
        ('twenties', 'age 20-29', 'age 55-70'),
        
        # Middle age terms
        ('middle-aged', 'age 40-55', 'age 18-25'),
        ('middle age', 'age 45-60', 'age 15-25'),
        ('midlife', 'age 40-60', 'age 20-30'),
        ('forties', 'age 40-49', 'age 15-25'),
        ('fifties', 'age 50-59', 'age 18-28'),
        
        # Older age terms
        ('old', 'age 65-80', 'age 15-25'),
        ('elderly', 'age 70-85', 'age 20-30'),
        ('senior', 'age 65-80', 'age 15-25'),
        ('senior citizen', 'age 65-85', 'age 18-30'),
        ('aged', 'age 70-90', 'age 15-30'),
        ('retiree', 'age 65-75', 'age 20-35'),
        ('pensioner', 'age 65-80', 'age 18-30'),
        ('golden years', 'age 65-85', 'age 20-35'),
        ('older adult', 'age 60-80', 'age 18-30'),
        ('geriatric', 'age 75-90', 'age 20-40'),
        
        # Adult terms (compared to both younger and older)
        ('adult', 'age 25-50', 'age 5-15'),
        ('grown-up', 'age 30-55', 'age 8-18'),
        ('mature adult', 'age 35-60', 'age 10-20'),
        
        # Decades-based terms
        ('thirties', 'age 30-39', 'age 60-70'),
        ('sixties', 'age 60-69', 'age 20-30'),
        ('seventies', 'age 70-79', 'age 18-28'),
        ('eighties', 'age 80-89', 'age 20-35'),
    ]

    print(f"🔬 Testing Age-Term to Age-Range Similarity Hypothesis")
    print(f"Model: {model_name}")
    print(f"Total Test Cases: {len(test_cases)}")
    print("=" * 70)
    print("Hypothesis: similarity(term, matching_range) > similarity(term, different_range)")
    print("=" * 70)

    results = []
    
    # --- 3. Process Each Test Case ---
    for i, (text1, text2, text3) in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/{len(test_cases)}: '{text1}'")
        
        try:
            # Get embeddings for this test case
            result = genai.embed_content(
                model=model_name,
                content=[text1, text2, text3],
                task_type="SEMANTIC_SIMILARITY"
            )
            
            embeddings = result['embedding']
            
            if len(embeddings) < 3:
                print("   ⚠️  API did not return all embeddings. Skipping...")
                results.append({'passed': False, 'case': (text1, text2, text3)})
                continue
                
            vec1 = embeddings[0]
            vec2 = embeddings[1]
            vec3 = embeddings[2]
            
            # Calculate similarities
            sim_1_2 = cosine_similarity(vec1, vec2)
            sim_1_3 = cosine_similarity(vec1, vec3)
            
            passed = sim_1_2 > sim_1_3
            
            print(f"   '{text1}' ↔ '{text2}': {sim_1_2:.6f}")
            print(f"   '{text1}' ↔ '{text3}': {sim_1_3:.6f}")
            
            if passed:
                print(f"   ✅ PASS ({sim_1_2:.6f} > {sim_1_3:.6f})")
            else:
                print(f"   ❌ FAIL ({sim_1_2:.6f} ≤ {sim_1_3:.6f})")
            
            results.append({
                'passed': passed,
                'case': (text1, text2, text3),
                'sim_match': sim_1_2,
                'sim_diff': sim_1_3
            })
            
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            results.append({'passed': False, 'case': (text1, text2, text3)})

    # --- 4. Summary Statistics ---
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['passed'])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests:    {total_tests}")
    print(f"✅ Passed:      {passed_tests}")
    print(f"❌ Failed:      {failed_tests}")
    print(f"Success Rate:   {success_rate:.1f}%")
    
    # Show failed cases if any
    if failed_tests > 0:
        print(f"\n❌ Failed Cases:")
        for r in results:
            if not r['passed'] and 'sim_match' in r:
                text1, text2, text3 = r['case']
                print(f"   • '{text1}' → {r['sim_match']:.4f} (match) vs {r['sim_diff']:.4f} (diff)")
    
    print("=" * 70)
    
    if success_rate >= 90:
        print("🎉 Excellent! Hypothesis strongly validated!")
    elif success_rate >= 75:
        print("👍 Good! Hypothesis generally holds true.")
    elif success_rate >= 60:
        print("⚠️  Moderate support for hypothesis.")
    else:
        print("❌ Hypothesis may need refinement.")
    
    print("=" * 70)


if __name__ == "__main__":
    validate_hypothesis()
