# ai_service.py
import cohere
import numpy as np
import re
import logging
from typing import Dict, List
from google_vision import GoogleVisionService

class AIService:
    def __init__(self, api_key: str):
        """Initialize AI services with Cohere and Google Vision"""
        try:
            self.co = cohere.Client(api_key)
            self.vision_service = GoogleVisionService()
        except Exception as e:
            logging.error(f"AI Service initialization failed: {e}")
            raise

    def analyze_content(self, text: str) -> Dict:
        """Main text analysis pipeline"""
        if not text.strip():
            return {
                'direct_quotes': [],
                'paraphrased': [],
                'references': []
            }

        return {
            'direct_quotes': self._find_direct_quotes(text),
            'paraphrased': self._find_paraphrased_content(text),
            'references': self._analyze_reference_section(text)
        }

    def analyze_image(self, image_path: str) -> Dict:
        """Complete image analysis pipeline"""
        try:
            # First get vision analysis
            vision_analysis = self.vision_service.analyze_image(image_path)
            
            # Then analyze extracted text
            text_analysis = self.analyze_content(vision_analysis.get('text', ''))

            return {
                'vision_analysis': vision_analysis,
                'text_analysis': text_analysis,
                'matching_images': vision_analysis.get('matching_images', []),
                'colors': vision_analysis.get('colors', [])
            }
        except Exception as e:
            logging.error(f"Image analysis failed: {e}")
            return {}

    def _find_direct_quotes(self, text: str) -> List[Dict]:
        """Identify and source direct quotes using Cohere"""
        try:
            quotes = re.findall(r'\"(.*?)\"|\'(.*?)\'', text)
            unique_quotes = list(set([q[0] or q[1] for q in quotes]))
            
            detected = []
            for quote in unique_quotes:
                if len(quote) > 20:  # Ignore short phrases
                    response = self.co.chat(
                        message=f"Source this quote: {quote}",
                        model="command-r-plus",
                        citation_quality="accurate"
                    )
                    if response.citations:
                        detected.append({
                            'text': quote,
                            'sources': [c.text for c in response.citations]
                        })
            return detected
        except Exception as e:
            logging.error(f"Direct quote detection failed: {e}")
            return []

    def _analyze_reference_section(self, text: str) -> List[Dict]:
        """Validate academic references using Cohere"""
        try:
            ref_section = re.search(r'REFERENCES(.*?)(?=APPENDIX|$)', text, re.DOTALL)
            if not ref_section:
                return []

            references = []
            for line in ref_section.group(1).split('\n'):
                if line.strip():
                    response = self.co.chat(
                        message=f"Verify academic reference: {line}",
                        model="command-r-plus"
                    )
                    references.append({
                        'reference': line,
                        'valid': "valid" in response.text.lower()
                    })
            return references
        except Exception as e:
            logging.error(f"Reference analysis failed: {e}")
            return []

    def _find_paraphrased_content(self, text: str) -> List[Dict]:
        """Detect potentially paraphrased content"""
        try:
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            paraphrased = []
            
            for chunk in chunks:
                response = self.co.chat(
                    message=f"Identify potentially paraphrased content: {chunk}",
                    model="command-r-plus",
                    temperature=0.3
                )
                if response.citations:
                    paraphrased.extend([{
                        'text': c.text,
                        'sources': [s.text for s in c.documents],
                        'similarity': c.confidence
                    } for c in response.citations])
            
            return paraphrased
        except Exception as e:
            logging.error(f"Paraphrase detection failed: {e}")
            return []

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            dot = np.dot(vec1, vec2)
            norm = (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(dot / norm) if norm != 0 else 0.0
        except Exception as e:
            logging.error(f"Similarity calculation failed: {e}")
            return 0.0