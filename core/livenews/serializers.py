from rest_framework import serializers
from .models import LiveNews, NewsCategory


class NewsSerializer(serializers.ModelSerializer):
    """Serializes the required fields from the `LiveNews` model"""
    reliability_score = serializers.SerializerMethodField()

    class Meta:
        model = LiveNews
        fields = '__all__'

    def get_reliability_score(self, obj):
        """Calculate reliability score based on confidence and prediction."""
        try:
            # Base score from confidence
            base_score = int(obj.confidence * 100)
            
            # Adjust score based on prediction and confidence thresholds
            if obj.prediction:  # Real news
                if obj.confidence > 0.9:  # Very high confidence
                    score = min(base_score + 10, 98)  # Cap at 98%
                elif obj.confidence > 0.8:  # High confidence
                    score = base_score + 5
                elif obj.confidence > 0.7:  # Moderate confidence
                    score = base_score
                else:  # Lower confidence
                    score = max(base_score - 5, 50)  # Don't go below 50%
            else:  # Fake news
                if obj.confidence > 0.9:  # Very high confidence
                    score = min(base_score - 5, 95)  # Slightly lower for fake news
                elif obj.confidence > 0.8:
                    score = base_score - 10
                elif obj.confidence > 0.7:
                    score = base_score - 15
                else:
                    score = max(base_score - 20, 40)  # Don't go below 40%
            
            return f"{score}%"
        except Exception:
            # Fallback only if something goes wrong
            return f"{int(obj.confidence * 100)}%"


class LiveNewsSerializer(serializers.ModelSerializer):
    """Serializes the required fields from the `LiveNews` model"""
    reliability_score = serializers.SerializerMethodField()

    class Meta:
        model = LiveNews
        fields = (
            'id', 'title', 'publication_date',
            'news_category', 'prediction', 'img_url',
            'reliability_score'
        )

    def get_reliability_score(self, obj):
        """Calculate reliability score based on confidence and prediction."""
        try:
            # Base score from confidence
            base_score = int(obj.confidence * 100)
            
            # Adjust score based on prediction and confidence thresholds
            if obj.prediction:  # Real news
                if obj.confidence > 0.9:  # Very high confidence
                    score = min(base_score + 10, 98)  # Cap at 98%
                elif obj.confidence > 0.8:  # High confidence
                    score = base_score + 5
                elif obj.confidence > 0.7:  # Moderate confidence
                    score = base_score
                else:  # Lower confidence
                    score = max(base_score - 5, 50)  # Don't go below 50%
            else:  # Fake news
                if obj.confidence > 0.9:  # Very high confidence
                    score = min(base_score - 5, 95)  # Slightly lower for fake news
                elif obj.confidence > 0.8:
                    score = base_score - 10
                elif obj.confidence > 0.7:
                    score = base_score - 15
                else:
                    score = max(base_score - 20, 40)  # Don't go below 40%
            
            return f"{score}%"
        except Exception:
            # Fallback only if something goes wrong
            return f"{int(obj.confidence * 100)}%"


class LiveNewsDetailedSerializer(serializers.ModelSerializer):
    """Serialized all fields from the `LiveNews` model"""
    reliability_score = serializers.SerializerMethodField()

    class Meta:
        model = LiveNews
        fields = (
            'id', 'title', 'publication_date',
            'news_category', 'prediction', 'section_id',
            'section_name', 'type', 'web_url', 'img_url',
            'reliability_score'
        )

    def get_reliability_score(self, obj):
        """Calculate reliability score based on confidence and prediction."""
        try:
            # Base score from confidence
            base_score = int(obj.confidence * 100)
            
            # Adjust score based on prediction and confidence thresholds
            if obj.prediction:  # Real news
                if obj.confidence > 0.9:  # Very high confidence
                    score = min(base_score + 10, 98)  # Cap at 98%
                elif obj.confidence > 0.8:  # High confidence
                    score = base_score + 5
                elif obj.confidence > 0.7:  # Moderate confidence
                    score = base_score
                else:  # Lower confidence
                    score = max(base_score - 5, 50)  # Don't go below 50%
            else:  # Fake news
                if obj.confidence > 0.9:  # Very high confidence
                    score = min(base_score - 5, 95)  # Slightly lower for fake news
                elif obj.confidence > 0.8:
                    score = base_score - 10
                elif obj.confidence > 0.7:
                    score = base_score - 15
                else:
                    score = max(base_score - 20, 40)  # Don't go below 40%
            
            return f"{score}%"
        except Exception:
            # Fallback only if something goes wrong
            return f"{int(obj.confidence * 100)}%"


class CategorySerializer(serializers.ModelSerializer):
    """Serializes the required fields from the `NewsCategory` model"""
    class Meta:
        model = NewsCategory
        fields = '__all__'


class CategoryDropdownSerializer(serializers.ModelSerializer):
    """Serializer for category dropdown menu"""
    value = serializers.CharField(source='name')
    label = serializers.CharField(source='name')
    
    class Meta:
        model = NewsCategory
        fields = ('value', 'label')
