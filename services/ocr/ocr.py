import os
from preprocess import preprocess_image, find_margin_boundary
from ocr_engine import detect_question_markers, segment_answer_regions, extract_text_from_regions

def process_answer_sheet(image_path):
    os.makedirs("output", exist_ok=True)
    
    image, gray, thresh = preprocess_image(image_path)
    margin_boundary = find_margin_boundary(thresh)
    print(f"Margin boundary detected at: {margin_boundary} pixels")
    
    # Extract the left margin region from the threshold image
    margin = thresh[:, :margin_boundary]
    
    markers = detect_question_markers(margin)
    if not markers:
        print("No question markers found. Please adjust OCR settings or verify the image.")
        return {}
    print("Detected markers:", markers)
    
    answer_regions = segment_answer_regions(image, markers, margin_boundary)
    for q_num, region in answer_regions.items():
        filename = f"output/question_{q_num}_answer.png"
        # Save each segmented answer region for review
        import cv2
        cv2.imwrite(filename, region)
        print(f"Saved answer region for Question {q_num} as {filename}")
    
    # Extract text from each answer region
    extracted_text = extract_text_from_regions(answer_regions)
    
    # Save the extracted text to a file for review
    with open("output/extracted_text.txt", "w", encoding="utf-8") as f:
        for q_num, text in extracted_text.items():
            f.write(f"Question {q_num}:\n{text}\n\n")
    
    return extracted_text

if __name__ == "__main__":
    result = process_answer_sheet("template-2.png")
    print("\nExtracted text by question number:")
    for q_num, text in result.items():
        print(f"Question {q_num}:")
        print(text)