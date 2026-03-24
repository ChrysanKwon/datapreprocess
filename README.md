# datapreprocess

Data preprocessing utilities for object detection datasets using LabelImg XML annotations.

## Scripts

### `XMLtoCOCO.py`
Converts LabelImg XML annotations to COCO JSON format.

- Merges similar categories (e.g. `car_Taxi` → `car`)
- Filters out files without rare/target categories
- Splits dataset into train/val (60/40)
- Copies corresponding images to output directory
- Outputs per-category count statistics

**Usage:**
Edit `input_directory` and `output_directory` at the bottom of the file, then run:
```bash
python XMLtoCOCO.py
```

**Output structure:**
```
output_directory/
├── annotations/
│   ├── instances_train2017.json
│   └── instances_val2017.json
├── train2017/
└── val2017/
```

---

### `readxml.py`
XML annotation utility functions.

- `delete_xml_without_jpg`: Removes XML files that have no matching image
- `update_xml_filename`: Syncs `<filename>` tag in XML to match the actual filename
- `correct_wrong_bbox`: Clamps bounding boxes that exceed image boundaries
- `delete_normal_thing`: Removes images that contain only common categories (no target classes)

**Usage:**
Edit `directory` in `main()`, then run:
```bash
python readxml.py
```

---

### `datablackmask.py`
Blacks out specified polygon regions in images (e.g. to hide timestamps or watermarks before annotation).

**Usage:**
1. Edit `folder_path` to your image base directory
2. Edit `polygon_points` dict — keys are subfolder names, values are lists of polygon vertex coordinates
3. Run:
```bash
python datablackmask.py
```

## Installation

```bash
pip install -r requirements.txt
```
