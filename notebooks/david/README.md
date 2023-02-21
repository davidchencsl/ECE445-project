# David Lab Notebook

## 2023-02-14 - Shopping List Confirmed
- 2 Geared Motors
- 2 8-inch wheels
- 2 roller wheels
- 1 12V battery

## 2023-02-18 - PCB functionality
The PCB needs to accomplish the following:
- accept 12 V battery input
- provide stable 5V 4A
- convert two 3.3V PWM inputs into 12V PWM

## 2023-02-19 - Jetson Nano
Due to the shortage of Raspberry Pi 4, we decided to switch to jetson nano 4G. It costs more and it also has cuda support to run larger model. We will use the yolov4-deepsort project to implement owner tracking: [davidchencsl/yolov4-deepsort: Object tracking implemented with YOLOv4, DeepSort, and TensorFlow. (github.com)](https://github.com/davidchencsl/yolov4-deepsort)