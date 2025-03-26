import cv2
import numpy as np
import pytesseract
import platform
import os

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def cluster_markers(markers, y_threshold=30):
    """Group markers that are closer than y_threshold pixels."""
    if not markers:
        return []
    markers.sort(key=lambda m: m['y'])
    clustered = [markers[0]]
    for marker in markers[1:]:
        last = clustered[-1]
        if abs(marker['y'] - last['y']) < y_threshold:
            last['y'] = (last['y'] + marker['y']) // 2
            last['height'] = max(last.get('height', 20), marker.get('height', 20))
        else:
            clustered.append(marker)
    return clustered

def detect_digit_contours(margin):
    """
    Fallback method to detect potential digit contours in the margin.
    """
    working_margin = margin.copy()
    kernel = np.ones((3, 3), np.uint8)
    working_margin = cv2.morphologyEx(working_margin, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(working_margin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    vis_contours = cv2.cvtColor(working_margin, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(vis_contours, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("contour_detection.png", vis_contours)
    
    digit_markers = []
    min_area = 100
    max_area = 1500
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    expected_numbers = range(1, 11)  # Assume up to 10 questions
    
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = float(w) / h if h > 0 else 0
        if min_area < area < max_area and 0.25 < aspect_ratio < 2.0:
            if i < len(expected_numbers):
                number = expected_numbers[i]
                digit_markers.append({
                    'number': number,
                    'y': y,
                    'height': h,
                    'confidence': 30,
                    'config': "contour detection"
                })
    return digit_markers

def detect_question_markers(margin):
    """
    Run OCR on the margin and detect digit markers with improved handwritten detection.
    Uses multiple configurations to increase detection chances.
    """
    markers = []
    configurations = [
        {'psm': 10, 'threshold': 30, 'scale': 3},
        {'psm': 6, 'threshold': 25, 'scale': 3},
        {'psm': 7, 'threshold': 20, 'scale': 4},
    ]
    
    for config in configurations:
        psm = config['psm']
        confidence_threshold = config['threshold']
        scale_factor = config['scale']
        custom_config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789'
        
        working_margin = margin.copy()
        kernel = np.ones((2, 2), np.uint8)
        working_margin = cv2.dilate(working_margin, kernel, iterations=1)
        
        margin_scaled = cv2.resize(working_margin, None, 
                                   fx=scale_factor, 
                                   fy=scale_factor,
                                   interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(f"margin_for_ocr_psm{psm}.png", margin_scaled)
        
        details = pytesseract.image_to_data(margin_scaled, 
                                            output_type=pytesseract.Output.DICT, 
                                            config=custom_config)
        
        config_markers = []
        for i in range(len(details['text'])):
            text = details['text'][i].strip()
            try:
                conf = float(details['conf'][i])
            except ValueError:
                conf = 0.0
            if text.isdigit() and conf > confidence_threshold:
                config_markers.append({
                    'number': int(text),
                    'y': int(details['top'][i] / scale_factor),
                    'height': int(details['height'][i] / scale_factor),
                    'confidence': conf,
                    'config': f"PSM {psm}, conf {confidence_threshold}"
                })
        if config_markers:
            print(f"Found {len(config_markers)} markers using PSM {psm}")
            markers.extend(config_markers)
    
    if not markers:
        print("OCR detection failed. Attempting contour-based detection...")
        contour_markers = detect_digit_contours(margin)
        if contour_markers:
            print(f"Found {len(contour_markers)} markers using contour detection")
            markers.extend(contour_markers)
    
    markers = cluster_markers(markers, y_threshold=30)
    return markers

def segment_answer_regions(image, markers, margin_boundary):
    """
    Segment answer regions based on detected markers.
    Each region spans from one marker's y coordinate to the next, excluding the margin.
    """
    h, w, _ = image.shape
    answer_regions = {}
    markers.sort(key=lambda m: m['y'])
    for i, marker in enumerate(markers):
        y_start = marker['y']
        y_end = markers[i+1]['y'] if i < len(markers)-1 else h
        if y_end - y_start < 20:
            continue
        region = image[y_start:y_end, margin_boundary:w]
        answer_regions[marker['number']] = region
    return answer_regions

def extract_text_from_regions(answer_regions, use_easyocr_fallback=True):
    """
    Extract text from segmented answer regions using OCR.
    
    Args:
        answer_regions (dict): Dictionary mapping question numbers to image regions
        use_easyocr_fallback (bool): Whether to use EasyOCR as fallback if pytesseract fails
        
    Returns:
        dict: Dictionary mapping question numbers to extracted text
    """
    extracted_text = {}
    easyocr_reader = None  # Initialize only if needed
    
    for question_num, region in answer_regions.items():
        # Convert to grayscale for better OCR
        gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to handle varying lighting
        thresh = cv2.adaptiveThreshold(
            gray_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Save the preprocessed region for debugging
        cv2.imwrite(f"output/question_{question_num}_processed.png", thresh)
        
        # Use multiple OCR configurations for better accuracy
        configs = [
            '--oem 3 --psm 6',  # Assume a single uniform block of text
            '--oem 3 --psm 4',  # Assume a single column of text
            '--oem 3 --psm 3',  # Fully automatic page segmentation
        ]
        
        best_text = ""
        max_confidence = 0
        
        for config in configs:
            # Get both text and confidence
            data = pytesseract.image_to_data(thresh, config=config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence for non-empty text
            confidences = []
            text_parts = []
            
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    try:
                        conf = float(data['conf'][i])
                        if conf > 0:  # Only consider positive confidence
                            confidences.append(conf)
                            text_parts.append(data['text'][i])
                    except ValueError:
                        continue
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                if avg_confidence > max_confidence:
                    max_confidence = avg_confidence
                    best_text = " ".join(text_parts)
    
        
        extracted_text[question_num] = best_text.strip()
        print(f"Question {question_num}: Extracted text with confidence {max_confidence:.2f}")
    
    return extracted_text