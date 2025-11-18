#include <Servo.h>
#include <BraccioRobot.h>

#define END_CHAR          0x7C  //|
#define INPUT_BUFFER_SIZE 50

static char inputBuffer[INPUT_BUFFER_SIZE];
Position armPosition;

void setup() {
  Serial.begin(115200);
  BraccioRobot.init();
}

void loop() {
    if (Serial.available() > 0){
        byte result = Serial.readBytesUntil(END_CHAR, inputBuffer, INPUT_BUFFER_SIZE);
        inputBuffer[result] = 0;
        interpretCommand(inputBuffer);
    }
    delay(100);
}

void interpretCommand(char* inputBuffer) {
    if (inputBuffer[0] == 'P') {
        positionArm(&inputBuffer[0]);
    } else if (inputBuffer[0] == 'H') {
        homePositionArm();
    } else if (inputBuffer[0] == '0') {
        BraccioRobot.powerOff();
        Serial.print(0); // OK
    }  else if (inputBuffer[0] == '1') {
        BraccioRobot.powerOn();
        Serial.print(0); // OK
    } else {
        Serial.print(1); //E0
    }
}

void positionArm(char *in) {
    int speed = armPosition.setFromString(in);
    speed = 200;
    if (speed > 0) {
        BraccioRobot.moveToPosition(armPosition, speed);
        Serial.print(0); // OK
    } else {
        Serial.print(2); // E1
    }
}

void homePositionArm() {
    BraccioRobot.moveToPosition(armPosition.set(90, 90, 90, 90, 90, 73), 150);
    Serial.print(0); // OK
}
