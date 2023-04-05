#define MOT1 PIN_PB1
#define MOT2 PIN_PB4

void setup(){
    pinMode(MOT1, OUTPUT);
    pinMode(MOT2, OUTPUT);
}

void loop(){
    analogWrite(MOT1, 100);
    analogWrite(MOT2, 100);
    delay(3000);
    analogWrite(MOT1, 255);
    analogWrite(MOT2, 255);
    delay(3000);
}