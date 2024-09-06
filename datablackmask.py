import os
from PIL import Image, ImageDraw

def apply_polygon_mask(image_path, polygon_points, output_path):
    # Open the image
    image = Image.open(image_path)

    # Create a mask with a black polygon
    mask = Image.new('L', image.size, 255)  # Start with a white mask
    draw = ImageDraw.Draw(mask)
    for i in polygon_points:
        draw.polygon(i, fill=0)  # Draw the polygon in black

    # Apply the mask to the image
    masked_image = Image.new('RGB', image.size)
    masked_image.paste(image, mask=mask)

    # Save the modified image
    masked_image.save(output_path)

# Specify the folder path
folder_path = r'D:\full_data\last'

# Specify the polygon points
polygon_points = {
    #'110': [[(980, 150), (980, 195), (1055, 195), (1055, 150)],[(1120,135),(1280,135),(1280,230),(1120,230)],[(845,130),(845,175),(960,175),(960,130)]],
    #'112': [[(0, 190), (230, 190), (230, 285), (0, 285)]],
    # '113': [[(1255, 310), (1255, 375), (1280, 375), (1280, 310)],[(1100, 145), (1100, 190), (1145, 190), (1145, 145)],[(490, 60), (490, 80), (515, 80), (515, 60)]],
    # '116':[[ (1065, 225), (1055, 244), (1100, 273), (1110, 260)]],
    'ab':[[ (950, 170), (950, 200), (1035, 200), (1035, 170)],[ (790, 140), (830, 140), (830, 175), (790, 175)]],
}

# Iterate over all the jpg files in the folder
for folder in polygon_points.keys():
    new_folder_path = os.path.join(folder_path, f'{folder}_2407')
    os.makedirs(new_folder_path, exist_ok=True)  # Create the new folder if it doesn't exist
    for filename in os.listdir(os.path.join(folder_path, folder)):
        for i in range(2,12):
            if filename.endswith('.jpg') and filename.startswith(f'b{i}'):
                image_path = os.path.join(folder_path, folder, filename)
                output_path = os.path.join(new_folder_path, filename)
                apply_polygon_mask(image_path, polygon_points[folder], output_path)