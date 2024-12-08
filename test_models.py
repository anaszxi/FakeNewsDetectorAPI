import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def test_models():
    print("Testing model loading and predictions...")
    
    # Define test paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nb_model_path = os.path.join(base_dir, "models", "nb_model.pkl")
    vectorizer_path = os.path.join(base_dir, "models", "vectorizer_model.pkl")
    
    # Load models
    print(f"\nLoading models from:")
    print(f"- Model path: {nb_model_path}")
    print(f"- Vectorizer path: {vectorizer_path}")
    
    nb_model = pickle.load(open(nb_model_path, "rb"))
    vectorizer = pickle.load(open(vectorizer_path, "rb"))
    
    # Test cases
    test_cases = [
        {
            "text": "Scientists discover breakthrough in cancer research",
            "expected": "Real"
        },
        {
            "text": "SHOCKING: You won't believe what this celebrity did next!!!",
            "expected": "Fake"
        },
        {
            "text": "New study shows benefits of regular exercise",
            "expected": "Real"
        }
    ]
    
    print("\nRunning predictions on test cases:")
    for case in test_cases:
        # Transform text
        features = vectorizer.transform([case["text"]])
        
        # Get prediction and probability
        prediction = nb_model.predict(features)[0]
        proba = nb_model.predict_proba(features)[0]
        
        print(f"\nTest case: {case['text']}")
        print(f"Prediction: {'Real' if prediction == 1 else 'Fake'}")
        print(f"Probability: {np.max(proba):.2%}")
        print(f"Expected: {case['expected']}")
        print(f"Result: {'✅ Correct' if (prediction == 1 and case['expected'] == 'Real') or (prediction == 0 and case['expected'] == 'Fake') else '❌ Incorrect'}")

if __name__ == "__main__":
    test_models() 