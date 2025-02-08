import cv2
from argparse import ArgumentParser
import numpy as np
from tqdm import tqdm

def frame_to_text(frame, threshold=128, width=80, height=None):
    """Convert a single frame to text using ASCII characters."""
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Resize the frame to a manageable size
    true_height, true_width = gray_frame.shape
    aspect_ratio = true_width / true_height
    new_width = width if width is not None else int(height * aspect_ratio)
    new_height = height if height is not None else int(new_width / aspect_ratio)
    resized_frame = cv2.resize(gray_frame, (new_width, new_height))

    # Create a text representation
    text_representation = ""
    for row in resized_frame:
        for pixel in row:
            # Map pixel value to ASCII character
            if pixel < threshold:
                text_representation += 's'  # Black block
            else:
                text_representation += '_'  # White space
        text_representation += '\n'  # New line for the next row

    return text_representation

def video_to_text(video_path, output_path, threshold=128, width=80, height=None):
    """Convert a video to a text file using ASCII characters."""
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    with open(output_path, 'w') as f:
        for _ in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            # Convert the frame to text
            text_frame = frame_to_text(frame, threshold, width, height)
            f.write(text_frame)
            f.write('\n\n')  # Separate frames with new lines

    cap.release()
    print(f"Video converted to text and saved to {output_path}")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--video", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--threshold", type=int, default=128)
    parser.add_argument("--width", type=int, default=80)
    parser.add_argument("--height", type=int, default=None) 
    args = parser.parse_args()

    video_to_text(args.video, args.output, args.threshold, args.width, args.height)
