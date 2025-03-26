import os
import pytesseract
from PIL import Image

from services.ocr import preprocess
from services.ocr.ocr_postprocess import formula_detector, merger

def process_image(image_path):
    """
    Process an image with OCR to extract text.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text
    """
    
    return 

def batch_process(image_paths):
    """
    Process multiple images and combine their text.
    
    Args:
        image_paths (list): List of paths to image files
        
    Returns:
        str: Combined extracted text
    """
    return