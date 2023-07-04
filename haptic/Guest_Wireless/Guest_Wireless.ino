#include "Arduino.h"
#include <SPI.h>
#include <RF24.h>

const int LEFT_SIG = 2;
const int RIGHT_SIG = 3;

const int MOTOR_CTRL = 5;

volatile int turn = 0;
// 0  = do nothing
// 1 = turn left
// -1 = turn right

//These are used for interrupt button handling
long debouncing_time = 300;  //Debouncing Time in Milliseconds
volatile unsigned long last_micros;


// This is just the way the RF24 library works:
// Hardware configuration: Set up nRF24L01 radio on SPI bus (pins 10, 11, 12, 13) plus pins 7 & 8
RF24 radio(7, 8);

byte addresses[][6] = { "1Node", "2Node" };

void setup() {
  Serial.begin(9600);
  Serial.println("THIS IS THE RECEIVER CODE - YOU NEED THE OTHER ARDUINO TO TRANSMIT");


  pinMode(LEFT_SIG, INPUT_PULLUP);   //sets all button interrupts as pull ups
  pinMode(RIGHT_SIG, INPUT_PULLUP);  //sets all button interrupts as pull ups

  pinMode(MOTOR_CTRL, OUTPUT);  //sets all button interrupts as pull ups

  //attach interrupts to pins
  attachInterrupt(digitalPinToInterrupt(LEFT_SIG), left_ISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(RIGHT_SIG), right_ISR, FALLING);


  // Initiate the radio object
  radio.begin();

  // Set the transmit power to lowest available to prevent power supply related issues
  radio.setPALevel(RF24_PA_MIN);

  // Set the speed of the transmission to the quickest available
  radio.setDataRate(RF24_2MBPS);

  // Use a channel unlikely to be used by Wifi, Microwave ovens etc
  radio.setChannel(124);

  // Open a writing and reading pipe on each radio, with opposite addresses
  radio.openWritingPipe(addresses[0]);
  radio.openReadingPipe(1, addresses[1]);

  // Start the radio listening for data
  radio.startListening();
}

// -----------------------------------------------------------------------------
// We are LISTENING on this device only (although we do transmit a response)
// -----------------------------------------------------------------------------
void loop() {

  // This is what we receive from the other device (the transmitter)
  unsigned char data;
// NEED TO CHANGE THIS CODE TO NON BLOCKING INTERRUPT BASED
  // // Is there any data for us to get?
  // if (radio.available()) {

  //   // Go and read the data and put it into that variable
  //   while (radio.available()) {
  //     radio.read(&data, sizeof(char));
  //   }

  //   // No more data to get so send it back but add 1 first just for kicks
  //   // First, stop listening so we can talk
  //   radio.stopListening();
  //   data++;
  //   radio.write(&data, sizeof(char));

  //   // Now, resume listening so we catch the next packets.
  //   radio.startListening();

  //   // Tell the user what we sent back (the random numer + 1)
  //   Serial.print("Sent response ");
  //   Serial.println(data);
  // }

  Serial.println(turn);
  if(turn){
    digitalWrite(MOTOR_CTRL, 1);
  }else{
    digitalWrite(MOTOR_CTRL, 0);
  }
}


void left_ISR() {  // increments mode selection
  if ((long)(micros() - last_micros) >= debouncing_time * 1000) {
    turn++;
    if(turn >= 1){
      turn = 1;
    }
    last_micros = micros();
  }
}

void right_ISR() {  // increments mode selection
  if ((long)(micros() - last_micros) >= debouncing_time * 1000) {
    turn--;
    if(turn<= -1){
      turn = -1;
    }
    last_micros = micros();
  }
}
