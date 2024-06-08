'''
Dataset
---train
    - images
    - labels
---test
    - images
    - labels
---val
    - images
    - labels
'''

import os
import random
import shutil

source_folder = "D:\Code\Face Recognition\Dataset\Real"
destination_folder = "D:\Code\Face Recognition\Dataset\All"

train_folder = os.path.join(destination_folder, "train")
test_folder = os.path.join(destination_folder, "test")
val_folder = os.path.join(destination_folder, "val")

os.makedirs(train_folder, exist_ok=True)
os.makedirs(test_folder, exist_ok=True)
os.makedirs(val_folder, exist_ok=True)

files = os.listdir(source_folder)
image_files = [f.split('.')[0] for f in files if f.endswith(".jpg")]

# Shuffle
random.shuffle(image_files)

# Split data (80% train, 10% test, 10% val)
num_images = len(image_files)
num_train = int(0.8 * num_images)
num_test = int(0.1 * num_images)
num_val = num_images - num_train - num_test

# Move images and labels
for i, image_file in enumerate(image_files):
    source_image_path = os.path.join(source_folder, f"{image_file}.jpg")
    source_label_path = os.path.join(source_folder, f"{image_file}.txt")
    if i < num_train:
        destination_image_path = os.path.join(train_folder, "images", f"{image_file}.jpg")
        destination_label_path = os.path.join(train_folder, "labels", f"{image_file}.txt")
    elif i < num_train + num_test:
        destination_image_path = os.path.join(test_folder, "images", f"{image_file}.jpg")
        destination_label_path = os.path.join(test_folder, "labels", f"{image_file}.txt")
    else:
        destination_image_path = os.path.join(val_folder, "images", f"{image_file}.jpg")
        destination_label_path = os.path.join(val_folder, "labels", f"{image_file}.txt")

    # Copy ảnh và file text đến thư mục đích
    shutil.copyfile(source_image_path, destination_image_path)
    shutil.copyfile(source_label_path, destination_label_path)



