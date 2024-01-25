import xml.etree.ElementTree as ET
import cv2


def parse_voc_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    boxes = []
    for object in root.findall('object'):
        name = object.find('name').text
        bndbox = object.find('bndbox')
        xmin = int(round(float(bndbox.find('xmin').text)))
        ymin = int(round(float(bndbox.find('ymin').text)))
        xmax = int(round(float(bndbox.find('xmax').text)))
        ymax = int(round(float(bndbox.find('ymax').text)))
        boxes.append((name, (xmin, ymin, xmax, ymax)))

    return boxes

def draw_boxes(image_path, boxes):
    # 读取图像
    image = cv2.imread(image_path)

    # 在图像上绘制每个边界框和类别名称
    for box in boxes:
        name, (xmin, ymin, xmax, ymax) = box
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 1)
        cv2.putText(image, name, (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 1)

    # 显示图像
    cv2.imshow('Image with Bounding Boxes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

xml_file = '../outputs/Town10HD/Town10HD_000015_2155300_bounding_box.xml'  # PASCAL VOC格式的XML文件路径
image_path = '../outputs/Town10HD/Town10HD_000015_2155300_img.png'  # 对应的图像文件路径

# 解析XML文件获取边界框
boxes = parse_voc_xml(xml_file)

# 在图像上绘制边界框
draw_boxes(image_path, boxes)