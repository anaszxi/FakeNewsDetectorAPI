import pickle
import os
import logging
import re
from collections import Counter

# Set up logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_features(text):
    """Extract additional features from text."""
    # Convert text to lowercase for some checks
    text_lower = text.lower()
    
    # Count exclamation marks
    exclamation_count = text.count('!')
    
    # Calculate ratio of uppercase letters
    caps_count = sum(1 for c in text if c.isupper())
    caps_ratio = caps_count / len(text) if len(text) > 0 else 0
    
    # Urgency and sensational words
    urgency_words = [
        'urgent', 'breaking', 'share', 'must', 'warning',
        'attention', 'alert', 'emergency', 'shocking', 'bombshell'
    ]
    
    # Conspiracy and doubt words
    conspiracy_words = [
        'truth', 'exposed', 'secret', 'they', 'conspiracy',
        'controlled', 'mainstream media', 'hidden', 'coverup', 'revealed',
        'proof', 'evidence', 'wake up', 'sheeple', 'banned'
    ]
    
    # Count word occurrences
    urgency_count = sum(1 for word in urgency_words if word in text_lower)
    conspiracy_count = sum(1 for word in conspiracy_words if word in text_lower)
    
    # Check for repeated punctuation
    repeated_punct = len(re.findall(r'[!?]{2,}', text))
    
    # Calculate all caps words ratio
    words = text.split()
    caps_words = sum(1 for word in words if word.isupper() and len(word) > 1)
    caps_words_ratio = caps_words / len(words) if words else 0
    
    return {
        'exclamation_count': exclamation_count,
        'caps_ratio': caps_ratio,
        'urgency_words': urgency_count,
        'conspiracy_words': conspiracy_count,
        'repeated_punct': repeated_punct,
        'caps_words_ratio': caps_words_ratio
    }

def analyze_text(title, text):
    """Analyze text features and provide detailed scoring."""
    # Extract features from both title and text
    title_features = extract_features(title)
    text_features = extract_features(text)
    
    # Calculate risk score (higher score means more likely to be fake)
    risk_score = 0
    
    # Title analysis (weighted more heavily)
    risk_score += title_features['exclamation_count'] * 2
    risk_score += title_features['caps_ratio'] * 100
    risk_score += title_features['urgency_words'] * 3
    risk_score += title_features['conspiracy_words'] * 3
    risk_score += title_features['repeated_punct'] * 3
    risk_score += title_features['caps_words_ratio'] * 50
    
    # Text analysis
    risk_score += text_features['exclamation_count']
    risk_score += text_features['caps_ratio'] * 50
    risk_score += text_features['urgency_words'] * 2
    risk_score += text_features['conspiracy_words'] * 2
    risk_score += text_features['repeated_punct'] * 2
    risk_score += text_features['caps_words_ratio'] * 25
    
    # Normalize score to 0-100 range
    normalized_score = min(100, risk_score)
    
    return {
        'risk_score': normalized_score,
        'title_analysis': title_features,
        'text_analysis': text_features,
        'interpretation': {
            'caps_usage': 'High' if title_features['caps_ratio'] > 0.3 or text_features['caps_ratio'] > 0.3 else 'Normal',
            'punctuation': 'Excessive' if title_features['repeated_punct'] > 0 or text_features['repeated_punct'] > 2 else 'Normal',
            'sensationalism': 'High' if title_features['urgency_words'] > 1 or text_features['urgency_words'] > 2 else 'Normal',
            'conspiracy_language': 'Present' if title_features['conspiracy_words'] > 0 or text_features['conspiracy_words'] > 1 else 'Not Present'
        }
    }

def load_model():
    """Load the trained model."""
    try:
        model_path = os.path.join(os.path.dirname(__file__), "models", "model_1_5_2.pkl")
        logger.debug(f"Attempting to load model from: {model_path}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
            
        with open(model_path, 'rb') as f:
            logger.debug("Loading model file...")
            model_info = pickle.load(f)
            logger.debug("Model loaded successfully")
            
        return model_info['vectorizer'], model_info['model']
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def predict_news(title, text, vectorizer, model):
    """Predict if a news article is real or fake."""
    try:
        # Combine title and text
        combined_text = f"{title} {text}"
        logger.debug("Vectorizing text...")
        
        # Get ML model prediction
        features = vectorizer.transform([combined_text])
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        
        # Get feature-based analysis
        analysis = analyze_text(title, text)
        
        # Adjust prediction based on risk score
        risk_score = analysis['risk_score']
        logger.debug(f"Risk score: {risk_score}")
        
        # If risk score is very high but model predicts real, or vice versa, adjust confidence
        if risk_score > 70 and prediction == 1:  # Model thinks it's real but high risk
            probability[1] *= 0.5  # Reduce confidence in real prediction
            probability[0] = 1 - probability[1]  # Adjust fake probability
        elif risk_score < 30 and prediction == 0:  # Model thinks it's fake but low risk
            probability[0] *= 0.5  # Reduce confidence in fake prediction
            probability[1] = 1 - probability[0]  # Adjust real probability
        
        # Make final prediction
        final_prediction = 1 if probability[1] > 0.5 else 0
        
        return {
            'prediction': 'REAL' if final_prediction == 1 else 'FAKE',
            'confidence': float(max(probability)),
            'probabilities': {
                'fake': float(probability[0]),
                'real': float(probability[1])
            },
            'analysis': analysis
        }
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise

def main():
    try:
        # Load model
        logger.info("Loading model...")
        vectorizer, model = load_model()
        logger.info("Model loaded successfully!")
        
        # Test cases
        test_articles = [
            # Real news examples - Financial
            {
                'title': 'Fed Raises Interest Rates by 0.25% Amid Inflation Concerns',
                'text': 'The Federal Reserve raised its benchmark interest rate by a quarter percentage point today, continuing its fight against inflation while acknowledging recent banking system turmoil. Fed Chair Jerome Powell stated that the banking system remains sound and resilient.',
                'expected': 'REAL'
            },
            # Real news examples - Technology
            {
                'title': 'SpaceX Successfully Launches New Batch of Starlink Satellites',
                'text': 'SpaceX launched another batch of 60 Starlink satellites into orbit today using its Falcon 9 rocket. The launch took place at Kennedy Space Center in Florida. This marks the company\'s 20th successful launch this year.',
                'expected': 'REAL'
            },
            # Real news examples - Sports
            {
                'title': 'Manchester City Wins Premier League Title',
                'text': 'Manchester City secured their third consecutive Premier League title with a 4-1 victory over Arsenal at the Etihad Stadium. Kevin De Bruyne scored twice, while Phil Foden and Ilkay Gundogan added one each.',
                'expected': 'REAL'
            },
            # Real news examples - Health
            {
                'title': 'New Study Links Mediterranean Diet to Lower Heart Disease Risk',
                'text': 'A large-scale study published in the New England Journal of Medicine found that people following a Mediterranean diet had a 25% lower risk of heart disease. The research followed 12,000 participants over five years.',
                'expected': 'REAL'
            },
            # Fake news - Political Conspiracy
            {
                'title': '!!!URGENT!!! SHARE NOW!!! DEEP STATE EXPOSED!!! MUST READ!!!',
                'text': '!!!BREAKING NEWS!!! TOP SECRET documents PROVE that the DEEP STATE is controlling EVERYTHING!!! They don\'t want you to know this!!! SHARE BEFORE THEY DELETE THIS!!! The mainstream media is HIDING THE TRUTH!!! Wake up SHEEPLE!!! This is the BIGGEST CONSPIRACY ever exposed!!!',
                'expected': 'FAKE'
            },
            # Fake news - Health Misinformation
            {
                'title': 'MIRACLE CURE THEY DON\'T WANT YOU TO KNOW ABOUT!!!',
                'text': 'DOCTORS SHOCKED!!! Ancient remedy CURES ALL DISEASES overnight!!! Big Pharma DOESN\'T WANT YOU TO KNOW about this NATURAL cure!!! 100% effective! SHARE BEFORE they TAKE THIS DOWN!!! They\'re trying to SILENCE THE TRUTH!!!',
                'expected': 'FAKE'
            },
            # Fake news - Celebrity Conspiracy
            {
                'title': '!!! SHOCKING !!! Famous Celebrity Reveals DARK TRUTH About Hollywood !!!',
                'text': 'SHARE NOW!!! A-list celebrity exposes how the entertainment industry is controlled by ALIEN OVERLORDS!!! They\'re using MIND CONTROL on the public!!! This is why they want to SILENCE them!!! The truth must come out!!!',
                'expected': 'FAKE'
            },
            # Fake news - Science Misinformation
            {
                'title': 'SCIENTISTS ADMIT: Earth is Actually FLAT and NASA LIED!!!',
                'text': 'BREAKING!!! Top scientists finally ADMIT the TRUTH about our flat Earth!!! NASA has been LYING to us all along!!! All photos are FAKE!!! Share this BEFORE they delete it!!! The truth movement CANNOT BE STOPPED!!!',
                'expected': 'FAKE'
            },
            # Real news - Business
            {
                'title': 'Apple Reports Record Quarter with Strong iPhone Sales',
                'text': 'Apple Inc. reported quarterly revenue of $89.6 billion, up 54% year over year, driven by strong iPhone 12 sales. The company also announced a 7% increase in its dividend and additional $90 billion in share buybacks.',
                'expected': 'REAL'
            },
            # Real news - Science
            {
                'title': 'NASA\'s Mars Rover Discovers Signs of Ancient Microbial Life',
                'text': 'NASA\'s Perseverance rover has discovered organic molecules in Martian rocks that could indicate ancient microbial life. The findings, published in Science journal, suggest Mars once had conditions suitable for life.',
                'expected': 'REAL'
            },
            # Fake news - Financial Scam
            {
                'title': '!!! URGENT !!! SECRET BITCOIN HACK Makes Millions Overnight !!!',
                'text': 'LEAKED!!! Secret algorithm GUARANTEES 1000% returns in 24 hours!!! Banks HATE this!!! Make MILLIONS from home!!! This secret trading method is being SUPPRESSED by the elite!!! Act NOW before they BAN this!!!',
                'expected': 'FAKE'
            },
            # Fake news - Environmental Conspiracy
            {
                'title': 'EXPOSED!!! Weather Control Machines Found in SECRET Locations!!!',
                'text': 'SHOCKING TRUTH revealed!!! Government weather control devices DISCOVERED!!! They\'re controlling natural disasters!!! Whistleblower provides PROOF!!! The elite are manipulating our climate!!! SHARE before they SILENCE us!!!',
                'expected': 'FAKE'
            }
        ]
        
        # Test each article
        logger.info("\nTesting model with example articles:")
        correct_predictions = 0
        total_predictions = len(test_articles)
        
        for i, article in enumerate(test_articles, 1):
            logger.info(f"\nTest Article {i}:")
            logger.info(f"Title: {article['title']}")
            logger.info(f"Text: {article['text']}")
            logger.info(f"Expected: {article['expected']}")
            
            result = predict_news(article['title'], article['text'], vectorizer, model)
            
            logger.info(f"Prediction: {result['prediction']}")
            logger.info(f"Confidence: {result['confidence']:.2%}")
            logger.info(f"Probability of FAKE: {result['probabilities']['fake']:.2%}")
            logger.info(f"Probability of REAL: {result['probabilities']['real']:.2%}")
            
            # Log detailed analysis
            analysis = result['analysis']
            logger.info("\nDetailed Analysis:")
            logger.info(f"Risk Score: {analysis['risk_score']:.2f}/100")
            logger.info("Text Patterns:")
            logger.info(f"- Caps Usage: {analysis['interpretation']['caps_usage']}")
            logger.info(f"- Punctuation: {analysis['interpretation']['punctuation']}")
            logger.info(f"- Sensationalism: {analysis['interpretation']['sensationalism']}")
            logger.info(f"- Conspiracy Language: {analysis['interpretation']['conspiracy_language']}")
            
            is_correct = result['prediction'] == article['expected']
            correct_predictions += 1 if is_correct else 0
            logger.info(f"Correct: {'✓' if is_correct else '✗'}")
        
        # Print overall accuracy
        accuracy = correct_predictions / total_predictions
        logger.info(f"\nOverall Accuracy: {accuracy:.2%}")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 