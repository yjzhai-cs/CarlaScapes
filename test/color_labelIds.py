
import cv2

image_path = '../outputs/Town07/Town07_000050_075600_color.png'
labelIds_path = '../outputs/Town07/Town07_000050_075600_labelIds.png'

image = cv2.imread(image_path)
print(image)
labelIds = cv2.imread(labelIds_path)
print(labelIds)