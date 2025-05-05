# ai_service.py
import cohere
import numpy as np
import re
import logging
from typing import Dict, List
from google_vision import GoogleVisionService
from config import Config
from googleapiclient.discovery import build
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
            """Main text analysis pipeline with scoring"""
            analysis = {
                'direct_quotes': self._find_direct_quotes(text),
                'paraphrased': self._find_paraphrased_content(text),
                'references': self._analyze_reference_section(text),
                'plagiarism_score': 0.0  # Initialize score
            }
            analysis['plagiarism_score'] = self._calculate_plagiarism_score(analysis)
            return analysis

    def _calculate_plagiarism_score(self, analysis: Dict) -> float:
        """More nuanced scoring"""
        quote_score = len(analysis['direct_quotes']) * 2  # 2% per quote
        para_score = len(analysis['paraphrased']) * 1.5  # 1.5% per paraphrase
        ref_score = 0
        
        if analysis['references']:
            valid_refs = sum(1 for r in analysis['references'] if r['valid'])
            ref_score = 10 if valid_refs/len(analysis['references']) > 0.8 else 30
        
        return min(quote_score + para_score + ref_score, 100)

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
        """Better quote detection with Google Search integration"""
        try:
            # Find all quoted text including angled quotes
            quotes = re.findall(r'“[^”]+”|"[^"]+"|\'[^\']+\'', text)
            unique_quotes = list(set(q[1:-1] for q in quotes))  # Remove surrounding quotes
            
            detected = []
            for quote in unique_quotes:
                if len(quote) > 15:  # Reduced minimum length
                    # Use Google Custom Search for verification
                    google_results = self._google_search(quote)
                    
                    if google_results:
                        detected.append({
                            'text': quote,
                            'sources': google_results[:3]  # Top 3 results
                        })
            return detected
        except Exception as e:
            logging.error(f"Direct quote detection failed: {e}")
            return []

    def _google_search(self, query: str) -> List[str]:
        """Use Google Custom Search API with proper initialization"""
        try:
            # Initialize Google Search service
            service = build(
                "customsearch", 
                "v1", 
                developerKey=Config.GOOGLE_SEARCH_KEY
            )
            
            # Execute search
            res = service.cse().list(
                q=f'"{query}"',  # Exact phrase search
                cx=Config.GOOGLE_CSE_ID,
                num=3,
                exactTerms=query.split()[0]  # Improve relevance
            ).execute()
            
            return [item['link'] for item in res.get('items', [])]
        
        except Exception as e:
            logging.error(f"Google search failed: {e}")
            return []

    def _analyze_reference_section(self, text: str) -> List[Dict]:
        """Comprehensive reference detection"""
        try:
            # Broader section detection
            ref_section = re.search(
                r'(REFERENCES|BIBLIOGRAPHY|WORKS CITED|LITERATURE CITED)(.*?)($|\n\s*(APPENDIX|ACKNOWLEDG))',
                text, 
                re.DOTALL|re.IGNORECASE
            )
            
            if not ref_section:
                return []

            references = []
            # Split using common reference patterns
            ref_entries = re.split(r'\n(?=\[?\d+[\.\)]? |\•|\d+\.\s|\[[A-Z]+\])', ref_section.group(2).strip())
            
            for entry in ref_entries:
                if not entry.strip():
                    continue

                
                is_valid = bool(re.search(
                    r'(doi\.org|https?://|ISBN|\(\d{4}\))', 
                    entry, 
                    re.IGNORECASE
                ))
                
                references.append({
                    'reference': entry.strip(),
                    'valid': is_valid
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
