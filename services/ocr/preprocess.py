import cv2
import numpy as np

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from path: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("grayscale.png", gray)
    
    # Apply CLAHE to enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    cv2.imwrite("clahe_enhanced.png", gray)
    
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    cv2.imwrite("denoised.png", gray)
    
    # Use Otsu thresholding (good for handwritten strokes)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Enhance strokes with morphological operations
    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    thresh = cv2.erode(thresh, kernel, iterations=1)
    
    cv2.imwrite("thresh.png", thresh)
    return image, gray, thresh

def find_margin_boundary(thresh):
    # Compute vertical projection (sum of white pixels per column)
    vertical_projection = np.sum(thresh, axis=0)
    max_density = np.max(vertical_projection)
    
    # Find first column where density drops below 50% of maximum
    margin_boundary = int(np.argmax(vertical_projection < (max_density * 0.5)))
    
    if margin_boundary == 0:
        print("Margin boundary not found; using default value.")
        margin_boundary = 300
    margin_boundary = max(margin_boundary, 30)
    # Ensure margin does not exceed 10% of image width
    margin_boundary = min(margin_boundary, int(0.1 * thresh.shape[1]))
    
    # Draw visualization on a copy of the threshold image
    vis = thresh.copy()
    cv2.line(vis, (margin_boundary, 0), (margin_boundary, thresh.shape[0]), (0, 0, 255), 2)
    x_size = 20
    y_pos = 30
    cv2.line(vis, (margin_boundary - x_size, y_pos - x_size),
             (margin_boundary + x_size, y_pos + x_size), (0, 0, 255), 2)
    cv2.line(vis, (margin_boundary - x_size, y_pos + x_size),
             (margin_boundary + x_size, y_pos - x_size), (0, 0, 255), 2)
    cv2.imwrite("margin_visualization.png", vis)
    
    return margin_boundary
