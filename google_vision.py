#google_vision.py
from google.cloud import vision
import os
import logging

class GoogleVisionService:
    def __init__(self, credentials_path='secrets/vision-service-account.json'):
        self.client = self._authenticate(credentials_path)
    
    def _authenticate(self, credentials_path):
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            return vision.ImageAnnotatorClient()
        except Exception as e:
            logging.error(f"Google Vision authentication failed: {e}")
            raise

    def analyze_image(self, image_path):
        """Perform advanced image analysis using Google Vision API"""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.client.annotate_image({
                'image': image,
                'features': [
                    {'type_': vision.Feature.Type.TEXT_DETECTION},
                    {'type_': vision.Feature.Type.WEB_DETECTION},
                    {'type_': vision.Feature.Type.IMAGE_PROPERTIES}
                ]
            })

            return {
                'text': response.text_annotations[0].description if response.text_annotations else '',
                'web_entities': [entity.description for entity in response.web_detection.web_entities],
                'matching_images': [img.url for img in response.web_detection.full_matching_images],
                'colors': response.image_properties_annotation.dominant_colors.colors
            }
        except Exception as e:
            logging.error(f"Image analysis failed: {e}")
            return {}