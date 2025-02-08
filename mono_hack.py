from PIL import ImageFont, ImageDraw, Image
import numpy as np
import string
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import itertools

def load_font(font_name):
    fonts_folder = "/System/Library/Fonts/"
    # ttf / ttc / otf
    # recursive search
    for file in os.listdir(fonts_folder):
        if font_name in file.lower() and "bold" not in file.lower() and "italic" not in file.lower() and "oblique" not in file.lower() and "light" not in file.lower() and "thin" not in file.lower() and "semibold" not in file.lower() and "medium" not in file.lower() and "regular" not in file.lower() and "mono" not in file.lower() and "narrow" not in file.lower() and "condensed" not in file.lower() and "expanded" not in file.lower():
            return os.path.join(fonts_folder, file)
    print(f"Font {font_name} not found")
    return None

# List of most used fonts 
fonts = [
    "arial",
    "times",
    "courier",
    "verdana",
    "monaco",
    "calibri",
    "helvetica",
    "georgia",
    "montserrat",
    "tahoma",
    "trebuchet",
    "georgia",
    # Add paths to other fonts as needed
]

# ASCII characters to measure
ascii_chars = string.ascii_letters + string.digits + string.punctuation

# Dictionary to hold character widths for each font
char_widths = {font: {} for font in fonts}

# Measure character widths
for font in fonts:
    try:
        # Load the font
        font_size = 20  # You can adjust the font size
        font_obj = ImageFont.truetype(load_font(font), font_size)
        for char in ascii_chars:
            # Create an image to draw on
            image = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(image)
            # Measure the width of the character
            width = draw.textlength(char, font=font_obj)
            char_widths[font][char] = width
    except Exception as e:
        del char_widths[font]
        print(f"Could not load font {font}: {e}")

# print(char_widths)

#Create a DataFrame for explicit widths_array
widths_df = pd.DataFrame(char_widths).T  # Transpose to have fonts as rows

# Calculate the standard deviation for each character
std_devs = widths_df.std(axis=0)

# Initialize variables to track the best pair and the smallest std deviation
best_pair = None
smallest_std_dev = float('inf')

# Initialize a list to store pairs and their standard deviations
pairs_std_devs = []

# Iterate over all pairs of characters
for char1, char2 in itertools.combinations(ascii_chars, 2):
    # Calculate the standard deviation of the widths for the pair of characters
    pair_widths = widths_df[[char1, char2]]
    pair_std_dev = pair_widths.std(axis=1).mean()  # Mean of std deviations for the pair

    # Store the pair and its standard deviation
    pairs_std_devs.append(((char1, char2), pair_std_dev))

    # Check if this is the smallest std deviation found
    if pair_std_dev < smallest_std_dev:
        smallest_std_dev = pair_std_dev
        best_pair = (char1, char2)

# Print the result for the best pair
print(f"The most consistently sized characters across fonts are: '{best_pair[0]}' and '{best_pair[1]}' with a standard deviation of {smallest_std_dev:.2f}")

# Print all pairs and their standard deviations sorted by std deviations
print("\nAll character pairs and their standard deviations:")
for (char1, char2), std_dev in sorted(pairs_std_devs, key=lambda x: x[1])   :
    print(f"Characters: '{char1}' and '{char2}', Standard Deviation: {std_dev:.2f}")

# Print the DataFrame
print(widths_df)

# Convert to a NumPy array if needed
widths_array = widths_df.to_numpy()

# Analyze widths (e.g., calculate mean and std deviation)
mean_widths = widths_df.mean(axis=0)
std_widths = widths_df.std(axis=0)

#print the mean and std widths sorted by std widths
print("Std Widths:")
print(std_widths.sort_values(ascending=False).to_string())
print("Mean Widths:")
print(mean_widths.sort_values(ascending=False).to_string())