# CarlaScapes

CarlaScapes dataset sampling from [CARLA](http://carla.org) simulator involving 12 different Towns(Town01-Town07, Town10HD, Town11-Town13, Town15). The dataset contains 5000 images with 19 semantic categories and 9 custom categories. The dataset is divided into 4000 training images and 1000 testing images.


### Directory Structure

File naming format: `{town}_{frame}_{timestamp}_{type}.{suffix}`. 

```
CarlaScapes
├── train
│   ├── Town01
│   │   ├── Town01_000010_074800_bounding_box.xml
│   │   ├── Town01_000010_074800_color.png
│   │   ├── Town01_000010_074800_gnss.json
│   │   ├── Town01_000010_074800_img.png
│   │   ├── Town01_000010_074800_instance.json
│   │   ├── Town01_000010_074800_labelIds.png
│   ├── Town02
│   │   ├── ...
├── test
│   ├── Town15
│   │   ├── ...
`── README.md
```

### Color2LabelIds

The semantic categories are divided into 19 cityscapes classes (bold type) and 9 custom classes (italic form). The 19 cityscapes classes are the same as in the [CityScapes](https://www.cityscapes-dataset.com) dataset. 



Tag | Color          | LabelId
--- |----------------| ---
unlabeled | (0, 0, 0)      | 0
**road** | (128, 64, 128) | 1
**sidewalk** | (244, 35, 232) | 2
**building** | (70, 70, 70)   | 3
**wall** | (102, 102, 156) | 4
**fence** | (190, 153, 153) | 5
**pole** | (153, 153, 153) | 6
**traffic_light** | (250, 170, 30) | 7
**traffic_sign** | (220, 220, 0) | 8
**vegetation** | (107, 142, 35) | 9
**terrain** | (152, 251, 152) | 10
**sky** | (70, 130, 180) | 11
**pedestrian** | (220, 20, 60) | 12
**rider** | (255, 0, 0) | 13
**car** | (0, 0, 142) | 14
**truck** | (0, 0, 70) | 15
**bus** | (0, 60, 100) | 16
**train** | (0, 80, 100) | 17
**motorcycle** | (0, 0, 230) | 18
**bicycle** | (119, 11, 32) | 19
_static_ | (110, 190, 160) | 20
_dynamic_ | (170, 120, 50) | 21
_other_ | (55, 90, 80) | 22
_water_ | (45,60, 150) | 23
_road line_ | (157, 234, 50) | 24
_ground_ | (81, 0, 81) | 25
_bridge_ | (150, 100, 100) | 26
_rail track_ | (230, 150, 140) | 27
_guard rail_ | (180, 165, 180) | 28