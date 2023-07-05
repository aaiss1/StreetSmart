#include <SPI.h>
#include "printf.h"
#include "RF24.h"

const int LEFT_SIG = 2;
const int RIGHT_SIG = 3;

const int MOTOR_CTRL = 5;

volatile int turn = 0;
// 0  = do nothing
// 1 = turn left
// -1 = turn right

// These are used for interrupt button handling
long debouncing_time = 300; // Debouncing Time in Milliseconds
volatile unsigned long last_micros;

/*
 * See documentation at https://nRF24.github.io/RF24
 * See License information at root directory of this library
 * Author: Brendan Doherty (2bndy5)
 */

/**
 * A simple example of sending data from 1 nRF24L01 transceiver to another
 * with Acknowledgement (ACK) payloads attached to ACK packets.
 *
 * This example was written to be used on 2 devices acting as "nodes".
 * Use the Serial Monitor to change each node's behavior.
 */

#define CE_PIN 9
#define CSN_PIN 10
// instantiate an object for the nRF24L01 transceiver
RF24 radio(CE_PIN, CSN_PIN);

// an identifying device destination
// Let these addresses be used for the pair
uint8_t address[][6] = {"1Node", "2Node"};
// It is very helpful to think of an address as a path instead of as
// an identifying device destination
// to use different addresses on a pair of radios, we need a variable to

// uniquely identify which address this radio will use to transmit
bool radioNumber = 1; // 0 uses address[0] to transmit, 1 uses address[1] to transmit

// Used to control whether this node is sending or receiving
bool role = false; // true = TX role, false = RX role

// For this example, we'll be using a payload containing
// a string & an integer number that will be incremented
// on every successful transmission.
// Make a data structure to store the entire payload of different datatypes
struct PayloadStruct
{
  char message[7]; // only using 6 characters for TX & ACK payloads
  int counter;
};
PayloadStruct payload;

void setup()
{
  pinMode(LEFT_SIG, INPUT_PULLUP);  // sets all button interrupts as pull ups
  pinMode(RIGHT_SIG, INPUT_PULLUP); // sets all button interrupts as pull ups

  pinMode(MOTOR_CTRL, OUTPUT); // sets all button interrupts as pull ups

  // attach interrupts to pins
  attachInterrupt(digitalPinToInterrupt(LEFT_SIG), left_ISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(RIGHT_SIG), right_ISR, FALLING);
  Serial.begin(115200);
  while (!Serial)
  {
    // some boards need to wait to ensure access to serial over USB
  }

  // initialize the transceiver on the SPI bus
  if (!radio.begin())
  {
    Serial.println(F("radio hardware is not responding!!"));
    while (1)
    {
    } // hold in infinite loop
  }

  radioNumber = 1;
  Serial.print(F("radioNumber = "));
  Serial.println((int)radioNumber);

  // Set the PA Level low to try preventing power supply related problems
  // because these examples are likely run with nodes in close proximity to
  // each other.
  radio.setPALevel(RF24_PA_MIN); // RF24_PA_MAX is default.
  radio.setChannel(150);

  // to use ACK payloads, we need to enable dynamic payload lengths (for all nodes)
  radio.enableDynamicPayloads(); // ACK payloads are dynamically sized

  // Acknowledgement packets have no payloads by default. We need to enable
  // this feature for all nodes (TX & RX) to use ACK payloads.
  radio.enableAckPayload();

  // set the TX address of the RX node into the TX pipe
  radio.openWritingPipe(address[radioNumber]); // always uses pipe 0

  // set the RX address of the TX node into a RX pipe
  radio.openReadingPipe(1, address[!radioNumber]); // using pipe 1

  // additional setup specific to the node's role
  if (role)
  {
    // setup the TX payload

    memcpy(payload.message, "Hello ", 6); // set the payload message
    radio.stopListening();                // put radio in TX mode
  }
  else
  {
    // setup the ACK payload & load the first response into the FIFO

    memcpy(payload.message, "World ", 6); // set the payload message
    // load the payload for the first received transmission on pipe 0
    radio.writeAckPayload(1, &payload, sizeof(payload));

    radio.startListening(); // put radio in RX mode
  }

  // For debugging info
  // printf_begin();             // needed only once for printing details
  // radio.printDetails();       // (smaller) function that prints raw register values
  // radio.printPrettyDetails(); // (larger) function that prints human readable data
}

void loop()
{

  uint8_t pipe;
  if (radio.available(&pipe))
  {                                                // is there a payload? get the pipe number that recieved it
    uint8_t bytes = radio.getDynamicPayloadSize(); // get the size of the payload
    PayloadStruct received;
    radio.read(&received, sizeof(received)); // get incoming payload
    Serial.print(F("Received "));
    Serial.print(bytes); // print the size of the payload
    Serial.print(F(" bytes on pipe "));
    Serial.print(pipe); // print the pipe number
    Serial.print(F(": "));
    Serial.print(received.message); // print incoming message
    Serial.print(received.counter); // print incoming counter
    Serial.print(F(" Sent: "));
    Serial.print(payload.message);   // print outgoing message
    Serial.println(payload.counter); // print outgoing counter

    // save incoming counter & increment for next outgoing
    payload.counter = turn;
    // load the payload for the first received transmission on pipe 0
    radio.writeAckPayload(1, &payload, sizeof(payload));
  } // role

  if (Serial.available())
  {
    // change the role via the serial monitor
    // Become the RX node

    Serial.println(F("*** CHANGING TO RECEIVE ROLE -- PRESS 'T' TO SWITCH BACK"));
    memcpy(payload.message, "World ", 6); // change payload message

    // load the payload for the first received transmission on pipe 0
    radio.writeAckPayload(1, &payload, sizeof(payload));
    radio.startListening();
  }

  // Serial.println(turn);
  // if(turn){
  //   digitalWrite(MOTOR_CTRL, 1);
  // }else{
  //   digitalWrite(MOTOR_CTRL, 0);
  // }
} // loop

void left_ISR()
{ // increments mode selection
  if ((long)(micros() - last_micros) >= debouncing_time * 1000)
  {
    turn++;
    if (turn >= 1)
    {
      turn = 1;
    }
    last_micros = micros();
  }
}

void right_ISR()
{ // increments mode selection
  if ((long)(micros() - last_micros) >= debouncing_time * 1000)
  {
    turn--;
    if (turn <= -1)
    {
      turn = -1;
    }
    last_micros = micros();
  }
}
