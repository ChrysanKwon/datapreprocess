import os
import xml.etree.ElementTree as ET
import PIL.Image as Image

def delete_xml_without_jpg(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            filepath = os.path.join(directory, filename)
            tree = ET.parse(filepath)
            root = tree.getroot()
            # 找到與xml檔名稱相同的jpg檔案
            jpg_filename = os.path.splitext(filename)[0] + '.jpg'
            jpg_filepath = os.path.join(directory, jpg_filename)

            # 如果jpg檔案存在，則執行相應的操作
            if os.path.exists(jpg_filepath):
                # 執行你想要的操作
                pass
            else:
                # 刪除xml檔案
                os.remove(filepath)
                print(f"Deleted XML file: {filename}")

def update_xml_filename(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            filepath = os.path.join(directory, filename)
            tree = ET.parse(filepath)
            root = tree.getroot()
            # 找到 <filename> 標籤並更新其內容為 XML 文件名，但擴展名改為 .jpg
            xml_filename_element = root.find('filename')
            if xml_filename_element is not None:
                new_filename = os.path.splitext(filename)[0] + '.jpg'
                xml_filename_element.text = new_filename

                # 保存修改後的 XML 文件
                tree.write(filepath)
                print(f"Updated filename in XML: {new_filename}")

def correct_wrong_bbox(directory, class_name=None):

    def correct_bbox(tree, filename, width, height):
        bndbox = obj.find('bndbox')
        name = obj.find('name').text
        xmin = bndbox.find('xmin').text
        ymin = bndbox.find('ymin').text
        xmax = bndbox.find('xmax').text
        ymax = bndbox.find('ymax').text
        if int(ymax)>height or int(ymin)<1 or int(xmax)>width or int(xmin)<1:
            print(f"File: {filename}, class={name}, bndbox: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}")
            if int(ymax)>height:
                bndbox.find('ymax').text = str(height)
                print(f"File: {filename}, class={name}, ymax={height}")
            if int(ymin)<1:
                bndbox.find('ymin').text = '1'
                print(f"File: {filename}, class={name}, ymin=1")
            if int(xmax)>width:
                bndbox.find('xmax').text = str(width)
                print(f"File: {filename}, class={name}, xmax={width}")
            if int(xmin)<1:
                bndbox.find('xmin').text = '1'
                print(f"File: {filename}, class={name}, xmin=1")
            # 保存修改後的 XML 文件
            tree.write(filepath)
            print(f"Updated filename in XML: {filename}")


    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            filepath = os.path.join(directory, filename)
            tree = ET.parse(filepath)
            root = tree.getroot()

            # 讀取相同名稱的圖片大小
            jpg_filename = os.path.splitext(filename)[0] + '.jpg'
            jpg_filepath = os.path.join(directory, jpg_filename)
            # 如果jpg檔案存在，則讀取圖片大小
            if os.path.exists(jpg_filepath):
                image = Image.open(jpg_filepath)
                width, height = image.size
            else:
                print(f"Image not found: {jpg_filename}")

            for obj in root.findall('object'):
                name = obj.find('name').text
                if class_name is None:
                    correct_bbox(tree, filename, width, height)
                elif name == class_name:
                    correct_bbox(tree, filename, width, height)


def delete_normal_thing(directory):
    normal_categories = {"motorbike", "car"}
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            filepath = os.path.join(directory, filename)
            tree = ET.parse(filepath)
            root = tree.getroot()

            # 檢查 XML 檔案中是否只包含 normal_categories 中的類別
            categories_in_file = {obj.find('name').text for obj in root.findall('object')}
            if categories_in_file.issubset(normal_categories):
                os.remove(filepath)
                print(f"Deleted XML file: {filename}")
                jpg_filename = os.path.splitext(filename)[0] + '.jpg'
                jpg_filepath = os.path.join(directory, jpg_filename)
                if os.path.exists(jpg_filepath):
                    os.remove(jpg_filepath)
                    print(f"Deleted JPG file: {jpg_filename}")

def main():
    directory = r'D:\full_data\new\16road2408'
    for foldername in os.listdir(directory):
        folderpath = os.path.join(directory, foldername)
        if os.path.isdir(folderpath):
            update_xml_filename(folderpath)
            delete_xml_without_jpg(folderpath)
            correct_wrong_bbox(folderpath)
            delete_normal_thing(folderpath)
if __name__ == '__main__':
    main()
