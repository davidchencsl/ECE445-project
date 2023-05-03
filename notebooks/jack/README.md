# Lyuxing Lab Notebook
# Table of contents
1. [Shopping List Confirmed](#Shopping List Confirmed)


## 2023-02-14 - Shopping List Confirmed <a name="Shopping List Confirmed"></a>
- 20W DC-DC buck converter power module with 7~24V input and 5V/4A output
- N-channel power MOSFET - 30V / 60A

## 2023-02-18 - PCB functionality
The PCB needs to accomplish the following:
- accept 12 V battery input
- provide stable 5V 4A
- convert two 3.3V PWM inputs into 12V PWM

## 2023-02-19 - Jetson Nano
Due to the shortage of Raspberry Pi 4, we decided to switch to jetson nano 4G. It costs more and it also has cuda support to run larger model. We will use the yolov4-deepsort project to implement owner tracking: [davidchencsl/yolov4-deepsort: Object tracking implemented with YOLOv4, DeepSort, and TensorFlow. (github.com)](https://github.com/davidchencsl/yolov4-deepsort)

## 2023-02-25 - PCB Design
We bought a 24V - 5V buck converter to convert the battery voltage to power the PCB and the Jetson. The plan right now is to use ATTiny85 as the microcontroller. Jetson will send the desired speed data to ATTiny85 through I2C using only 2 pins, and ATTiny85 will output PWM signals to MOSFETS which will be 24V PWM signals that drives the motor.

## 2023-03-10 - Controller
The controller is implemented in Jetson Nano in python. We have 2 pid controllers that regulates the motor and keep it at the desired speed. We also have an additional controller to control the steering of the robot based on the deviate angles provided by the human identification subsystem.