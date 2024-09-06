import os
import json
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
from collections import defaultdict
import shutil
import datetime

# 定義要合併的類別
merge_categories = {
    "car_Taxi": "car",
    "spc_Cement": "spc",
    "car_CY": "car",
    "truck_CYF": "cyf",
    "car_Doll": "car",
    "spc_WaterTruck": "spc",
    "spc_TankTruck": "spc",
    "truck_CYA": "cya",
    "car_Police": "car",
    "spc_Garbage": "spc",
    "bus_B": "bus_b",
    "bus": "bus_a",
    "spc_Recycling": "spc",
    "car_Amb": "car",
    "truck_Postal": "truck",
    "truck_ENG": "truck",
    "spc_hearse": "spc",
    "car_Postal": "car",
}

rare_categories = ["truck_CYA", "bus_B", "bus", "bicycle", "truck_CYF"]
rare_categories2 = ["truck_CYA", "bicycle", "truck_CYF"]

# 假設 name_list 是根據名字順序的列表
name_list = ["car", "person", "truck", "motorbike", "bicycle", "bus_a", "bus_b", "cyf", "cya", "spc"]

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    image_info = {
        "file_name": os.path.splitext(os.path.basename(xml_file))[0]+'.jpg',
        "height": int(root.find('size/height').text),
        "width": int(root.find('size/width').text),
        "id": None  # 暫時不設置 ID
    }

    annotations = []
    categories_in_file = set()
    for obj in root.findall('object'):
        category = obj.find('name').text
        categories_in_file.add(category)
        # 合併類別
        category = merge_categories.get(category, category)
        bndbox = obj.find('bndbox')
        bbox = [
            int(bndbox.find('xmin').text),
            int(bndbox.find('ymin').text),
            int(bndbox.find('xmax').text) - int(bndbox.find('xmin').text),
            int(bndbox.find('ymax').text) - int(bndbox.find('ymin').text)
        ]
        annotation = {
            "image_id": None,  # 暫時不設置 ID
            "category_id": name_list.index(category) + 1,
            "bbox": bbox,
            "area": bbox[2] * bbox[3],
            "iscrowd": 0,
            "segmentation": [],
            "id": None  # 暫時不設置 ID
        }
        if annotation["area"] < 256:
            print(f"Warning: {xml_file} contains a small annotation with area < 256")
        else:
            annotations.append(annotation)

    if all(category not in categories_in_file for category in rare_categories):
        return None, None
    elif "last" in xml_file:
        if all(category not in categories_in_file for category in rare_categories2):
            return None, None

    return image_info, annotations

def filter_and_parse_xml_files(xml_files):
    parsed_files = []
    for xml_file in xml_files:
        image_info, annotations = parse_xml(xml_file)
        if image_info is not None and annotations is not None:
            parsed_files.append((xml_file, image_info, annotations))
    return parsed_files

def convert_to_coco(parsed_files, output_directory, split):
    coco_format = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    category_set = set()
    global_id_counter = 1
    global_aid_counter = 1
    for xml_file, image_info, annotations in parsed_files:
        image_info["id"] = global_id_counter
        for annotation in annotations:
            annotation["image_id"] = global_id_counter
            annotation["id"] = global_aid_counter
            global_aid_counter += 1

        global_id_counter += 1
        coco_format["images"].append(image_info)
        coco_format["annotations"].extend(annotations)
        for annotation in annotations:
            category_set.add(annotation["category_id"])

        # 複製對應的 JPG 圖片到輸出資料夾
        src_image_path = os.path.splitext(xml_file)[0] + '.jpg'
        dst_image_path = os.path.join(output_directory, f'{split}2017', image_info["file_name"])
        if os.path.exists(src_image_path):
            os.makedirs(os.path.dirname(dst_image_path), exist_ok=True)
            shutil.copy(src_image_path, dst_image_path)
        else:
            print(f"Warning: {src_image_path} does not exist and will not be copied.")
        print(f"Processed {xml_file}")

    # 根據 name_list 的順序來填充 id
    coco_format["categories"] = [{"id": cat, "name": name_list[cat-1], "supercategory": "none"} for cat in category_set]

    return coco_format

def get_all_xml_files(directory):
    xml_files = []
    roots = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
                roots.add(root)
    return roots, xml_files

def count_category_labels(annotations):
    category_counts = defaultdict(int)
    for annotation in annotations:
        category_counts[annotation["category_id"]] += 1
    return category_counts

def main(input_directory, output_directory):
    roots, xml_files = get_all_xml_files(input_directory)

    # 先篩選並解析 XML 檔案
    parsed_files = filter_and_parse_xml_files(xml_files)

    # 分割資料集
    train_files, val_files = train_test_split(parsed_files, test_size=0.4, random_state=42)

    # 轉換並保存 COCO 格式
    for split, files in zip(['train', 'val'], [train_files, val_files]):
        coco_data = convert_to_coco(files, output_directory, split)
        output_file = os.path.join(output_directory, 'annotations', f'instances_{split}2017.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(coco_data, f, indent=4)
        print(f"Saved {split} data to {output_file}")

        # 計算並輸出每個類別的標籤數量
        category_counts = count_category_labels(coco_data["annotations"])
        print(f"{split} data category counts:")
        for category, count in category_counts.items():
            print(f"  {name_list[category-1]}: {count}")

        date = datetime.datetime.now().strftime("%Y-%m-%d")
        output_txt = os.path.join(output_directory, f'{split}_output_{date}.txt')
        with open(output_txt, 'w') as f:
            f.write("All data:\n\n")
            for category, count in category_counts.items():
                f.write(f"{name_list[category-1]}: {count}\n")
            f.write("\nAll roots:\n\n")
            for root in roots:
                f.write(f"{root}\n")
        print(f"Saved {split} output to {output_txt}")
        # 輸出annotation的area<256的數量
        small_area_count = sum(1 for annotation in coco_data["annotations"] if annotation["area"] < 256)
        print(f"Number of annotations with area < 256: {small_area_count}")
        # 輸出面積<256的圖片檔名
        small_area_images = [annotation["image_id"] for annotation in coco_data["annotations"] if annotation["area"] < 256]
        # Convert image IDs to image names
        image_names = [image_info["file_name"] for image_info in coco_data["images"] if image_info["id"] in small_area_images]
        print(f"Images with area < 256: {image_names}")

if __name__ == "__main__":
    input_directory = r"D:\full_data\new"
    output_directory = r"data_all_0830"
    main(input_directory, output_directory)