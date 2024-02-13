#include <SPI.h>
#include "printf.h"
#include "RF24.h"

const int LEFT_SIG = 2;
const int RIGHT_SIG = 3;
const int LEFT_LED = 6;
const int RIGHT_LED = 7;

const int MOTOR_CTRL = 5;

volatile int turn = 0;
// 0  = do nothing
// 1 = turn left
// -1 = turn right

volatile int haptic = 0;
// 0  = do nothing
// 1 = vibrate
long blink_time = 100;
long vibration_time = 200;

int ledState = LOW;  // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;  // will store last time LED was updated

int haptic_drive = 0;
int signal_counter = 0;

// These are used for interrupt button handling
long debouncing_time = 300; // Debouncing Time in Milliseconds
volatile unsigned long last_micros;
volatile unsigned long last_vib_micros;

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
  // char message[9];
  int stat;
};
PayloadStruct payload;

void setup()
{
  // pinMode(LEFT_SIG, INPUT_PULLUP);  // sets all button interrupts as pull ups
  // pinMode(RIGHT_SIG, INPUT_PULLUP); // sets all button interrupts as pull ups

  pinMode(MOTOR_CTRL, OUTPUT); // sets all button interrupts as pull ups
  digitalWrite(MOTOR_CTRL, 0);

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
  radio.setPALevel(RF24_PA_HIGH); // RF24_PA_MAX is default.
  radio.setChannel(127);
  radio.setDataRate(RF24_250KBPS);

  // to use ACK payloads, we need to enable dynamic payload lengths (for all nodes)
  radio.setPayloadSize(2);
  // Acknowledgement packets have no payloads by default. We need to enable
  // this feature for all nodes (TX & RX) to use ACK payloads.
  radio.enableAckPayload();

  // set the TX address of the RX node into the TX pipe
  radio.openWritingPipe(address[radioNumber]); // always uses pipe 0

  // set the RX address of the TX node into a RX pipe
  radio.openReadingPipe(1, address[!radioNumber]); // using pipe 1

  // memcpy(payload.message, "Turn: ", 6); // set the payload message
  // load the payload for the first received transmission on pipe 0
  radio.writeAckPayload(1, &payload, sizeof(payload));

  radio.startListening(); // put radio in RX mode

  // For debugging info
  // printf_begin();             // needed only once for printing details
  // radio.printDetails();       // (smaller) function that prints raw register values
  // radio.printPrettyDetails(); // (larger) function that prints human readable data
}

void loop()
{
  if(turn != 0){
    if ((long)(millis() - previousMillis >= blink_time)) {
      previousMillis = millis();

      if (ledState == LOW) {
        ledState = HIGH;
      } else {
        ledState = LOW;
      }

      if(turn == 1){
        digitalWrite(LEFT_LED, ledState);
      }else if (turn == -1){
        digitalWrite(RIGHT_LED, ledState);
      }
    }
  }else if (turn == 0){
    ledState = LOW;
    digitalWrite(LEFT_LED, LOW);
    digitalWrite(RIGHT_LED, LOW);
  }

  uint8_t pipe;
  if (radio.available(&pipe))
  {                                                // is there a payload? get the pipe number that recieved it
    // signal_counter += (signal_counter == 50)? 0 : 1;
    uint8_t bytes = radio.getDynamicPayloadSize(); // get the size of the payload
    PayloadStruct received;
    radio.read(&received, sizeof(received)); // get incoming payload
    // Serial.print(F("Received "));
    // Serial.print(bytes); // print the size of the payload
    // Serial.print(F(" bytes on pipe "));
    // Serial.print(pipe); // print the pipe number
    // Serial.print(F(": "));
    // Serial.print(received.message); // print incoming message
     Serial.print(received.stat); // print incoming status
    haptic = received.stat;

    if(haptic){ //Drives the Haptic Motor if Haptic Enabled
      // Serial.print(F("  !!!Haptic Enabled!!!  "));

      if ((long)(micros() - last_vib_micros) >= vibration_time * 1000)
      {
        // digitalWrite(MOTOR_CTRL, haptic_drive);
        digitalWrite(MOTOR_CTRL, 1);
        delay(100);
        digitalWrite(MOTOR_CTRL, 0);
        
        haptic_drive = !haptic_drive;
        last_vib_micros = micros();
      }
    }

    //Load the Payload Acknowledgement
    payload.stat = turn;
    // Serial.print(F(" Sent: "));
    // Serial.print(payload.message);   // print outgoing message
    // Serial.println(payload.stat); // print outgoing counter
    radio.writeAckPayload(1, &payload, sizeof(payload));

  } else{
    // signal_counter -= (signal_counter == 0)? 0 : 1;
    // if (signal_counter == 0) {
    //   digitalWrite(MOTOR_CTRL, 0);
    // }
    digitalWrite(MOTOR_CTRL, 0);
  }
} // loop

void left_ISR()
{ // increments mode selection
  if ((long)(micros() - last_micros) >= debouncing_time * 1000)
  {
    turn = (turn == 0)? 1 : 0;
    last_micros = micros();
  }
}

void right_ISR()
{ // increments mode selection
  if ((long)(micros() - last_micros) >= debouncing_time * 1000)
  {
    // Serial.println("H");
    turn = (turn == 0)? -1 : 0;
    last_micros = micros();
  }
}
