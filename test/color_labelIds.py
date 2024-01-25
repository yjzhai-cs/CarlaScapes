
import cv2

image_path = '../outputs/Town07/Town07_000050_075600_color.png'  # PASCAL VOC格式的XML文件路径
labelIds_path = '../outputs/Town07/Town07_000050_075600_labelIds.png'  # 对应的图像文件路径

image = cv2.imread(image_path)
print(image)
labelIds = cv2.imread(labelIds_path)
print(labelIds)