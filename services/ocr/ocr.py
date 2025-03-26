import cv2
import numpy as np
import pytesseract

def preprocess_image(image_path):
    """
    Load and preprocess the image for analysis.
    
    Args:
        image_path (str): Path to the input image
    
    Returns:
        tuple: Original image, grayscale image, and binary threshold image
    """
    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from path: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to get a binary image
    # Save grayscale image
    cv2.imwrite('grayscale.png', gray)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    cv2.imwrite('thresh.png', thresh)
    
    return image, gray, thresh

def find_margin_boundary(thresh):
    """
    Find the boundary between the left margin and the main content using a vertical projection.
    
    Args:
        thresh (numpy.ndarray): Binary threshold image
    
    Returns:
        int: X-coordinate of the margin boundary
    """
    # Sum pixel values for each column to create a vertical projection
    vertical_projection = np.sum(thresh, axis=0)
    
    # Find maximum density (the printed numbers should contribute high values)
    max_density = np.max(vertical_projection)
    
    # Find the first column where the density drops below half of the maximum density
    margin_boundary = np.argmax(vertical_projection > max_density * 0.5)
    
    # In case no drop is found, use a default search width
    if margin_boundary == 0:
        print("Margin boundary not found")
        margin_boundary = 300  # Adjust this default if needed
    # Draw a vertical red line at the margin boundary
    cv2.line(thresh, (margin_boundary, 0), (margin_boundary, thresh.shape[0]), (0, 0, 255), 2)

    # Add an 'X' marker at the top of the line
    x_size = 20
    x_pos = margin_boundary
    y_pos = 30
    cv2.line(thresh, (x_pos - x_size, y_pos - x_size), (x_pos + x_size, y_pos + x_size), (0, 0, 255), 2)
    cv2.line(thresh, (x_pos - x_size, y_pos + x_size), (x_pos + x_size, y_pos - x_size), (0, 0, 255), 2)

    # Save the visualization
    cv2.imwrite('margin_visualization.png', thresh)
    return margin_boundary

def detect_question_markers(margin):
    """
    Detect question numbers in the margin using OCR.
    
    Args:
        margin (numpy.ndarray): Margin image
    
    Returns:
        list: List of dictionaries with question number and position
    """
    # Configure Tesseract for best OCR results, limiting recognized characters to digits only
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    
    # Perform OCR on the margin
    details = pytesseract.image_to_data(margin, output_type=pytesseract.Output.DICT, config=custom_config)
    # print(details)
    markers = []
    for i in range(len(details['text'])):
        text = details['text'][i].strip()
        print(text)
        try:
            conf = float(details['conf'][i])
        except ValueError:
            conf = 0.0
        
        # Filter for digit text with a reasonable confidence
        if text.isdigit() and conf > 51:
            print(text)
            markers.append({
                'number': int(text),
                'y': details['top'][i],
                'height': details['height'][i]
            })
    
    # Sort markers by vertical position
    markers.sort(key=lambda x: x['y'])
    return markers

def segment_answer_regions(image, markers, margin_boundary):
    """
    Segment answer regions based on question markers.
    
    Args:
        image (numpy.ndarray): Original image
        markers (list): List of question markers
        margin_boundary (int): X-coordinate of margin boundary
    
    Returns:
        dict: Dictionary of answer regions for each question
    """
    print(markers)
    h, w, _ = image.shape
    answer_regions = {}
    
    # Use the markers' vertical positions to define the answer areas.
    for i, marker in enumerate(markers):
        # The answer starts right below the marker's box
        y_start = marker['y'] 
        # The end is defined by the next marker's top, or the bottom of the image for the last question
        y_end = markers[i+1]['y'] if i < len(markers) - 1 else h
        
        # Crop the answer region from the image (excluding the left margin)
        answer_region = image[y_start:y_end, margin_boundary:w]
        answer_regions[marker['number']] = answer_region
    
    return answer_regions

def process_answer_sheet(image_path):
    """
    Main processing function for answer sheet segmentation.
    
    Args:
        image_path (str): Path to the input image
    
    Returns:
        dict: Segmented answer regions
    """
    # Preprocess the image
    image, gray, thresh = preprocess_image(image_path)
    
    # Dynamically find the margin boundary
    margin_boundary = find_margin_boundary(thresh)
    print(f"Margin boundary detected at: {margin_boundary} pixels")
    
    # Extract the left margin region
    margin = thresh[:, :margin_boundary]
    
    # Detect question markers in the margin
    markers = detect_question_markers(margin)
    if not markers:
        print("No question markers found. Please check the image or OCR configuration.")
        return {}
    
    # Segment answer regions based on detected markers
    answer_regions = segment_answer_regions(image, markers, margin_boundary)
    
    # Save segmented answer regions for verification
    for q_num, region in answer_regions.items():
        filename = f"question_{q_num}_answer.png"
        cv2.imwrite(filename, region)
        print(f"Saved answer region for Question {q_num} as {filename}")
    
    return answer_regions

if __name__ == "__main__":
    # Replace "template-e.png" with the path to your scanned answer sheet image
    process_answer_sheet("template-2.png")
