#include <SPI.h>
#include "printf.h"
#include "RF24.h"
#include <stdbool.h>

const int LEFT_SIG = 2;
const int RIGHT_SIG = 3;
const int LEFT_LED = 7;
const int RIGHT_LED = 6;
const int MODE_LED = 4;

const int MODE_BUTTON = A0;

const int MOTOR_CTRL = 5;

volatile int turn = 0;
// 0  = do nothing
// 1 = turn left
// -1 = turn right

volatile int haptic = 0;
// 0  = do nothing
// 1 = vibrate
const long turn_led_blink_time = 750;
const long status_led_blink_time = 500;
const long haptic_off_blink_time = 2000;
const int timeout_time = 3000;
long vibration_time = 200;

int turn_led_state = LOW;  // ledState used to set the LED
int status_led_state = LOW;  // ledState used to set the LED

// 0 - haptic on (normal)
// 1 - haptic off
bool is_haptic_on = true;
bool is_connected = false;

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long turn_led_prev_time = 0;  // will store last time LED was updated
unsigned long status_led_prev_time = 0;  // will store last time LED was updated
unsigned long last_connected_time = 0;

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

  pinMode(LEFT_LED, OUTPUT); // sets all button interrupts as pull ups
  digitalWrite(LEFT_LED, 0);
  pinMode(RIGHT_LED, OUTPUT); // sets all button interrupts as pull ups
  digitalWrite(RIGHT_LED, 0);

  pinMode(MODE_LED, OUTPUT); // led for connecting state
  digitalWrite(MODE_LED, 0);

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
      
      digitalWrite(LEFT_LED, HIGH);
      digitalWrite(RIGHT_LED, HIGH);
      delay(300);
      digitalWrite(LEFT_LED, LOW);
      digitalWrite(RIGHT_LED, LOW);
      delay(300);
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

// https://forum.arduino.cc/t/adding-a-double-click-case-statement/283504/3
/*
To keep a physical interface as simple as possible, this sketch demonstrates generating four output events from a single push-button.
1) Click:  rapid press and release
2) Double-Click:  two clicks in quick succession
3) Press and Hold:  holding the button down
4) Long Press and Hold:  holding the button for a long time 
*/
// Button timing variables
int debounce = 20;          // ms debounce period to prevent flickering when pressing or releasing the button
int DCgap = 250;            // max ms between clicks for a double click event
int holdTime = 2000;        // ms hold period: how long to wait for press+hold event
int longHoldTime = 4000;    // ms long hold period: how long to wait for press+hold event

// Button variables
bool buttonVal = HIGH;   // value read from button
bool buttonLast = HIGH;  // buffered value of the button's previous state
bool DCwaiting = false;  // whether we're waiting for a double click (down)
bool DConUp = false;     // whether to register a double click on next release, or whether to wait and click
bool singleOK = true;    // whether it's OK to do a single click
long downTime = -1;         // time the button was pressed down
long upTime = -1;           // time the button was released
bool ignoreUp = false;   // whether to ignore the button release because the click+hold was triggered
bool waitForUp = false;        // when held, whether to wait for the up event
bool holdEventPast = false;    // whether or not the hold event happened already
bool longHoldEventPast = false;// whether or not the long hold event happened already

int check_mode_button() {    
   int event = 0;
   // poll button - range 655-0, 500 arbitrary toggle value
   buttonVal = analogRead(MODE_BUTTON) < 500? LOW : HIGH;
   // Button pressed down
   if (buttonVal == LOW && buttonLast == HIGH && (millis() - upTime) > debounce)
   {
       downTime = millis();
       ignoreUp = false;
       waitForUp = false;
       singleOK = true;
       holdEventPast = false;
       longHoldEventPast = false;
       if ((millis()-upTime) < DCgap && DConUp == false && DCwaiting == true)  DConUp = true;
       else  DConUp = false;
       DCwaiting = false;
   }
   // Button released
   else if (buttonVal == HIGH && buttonLast == LOW && (millis() - downTime) > debounce)
   {        
       if (!ignoreUp)
       {
           upTime = millis();
           if (DConUp == false) DCwaiting = true;
           else
           {
               event = 2;
               DConUp = false;
               DCwaiting = false;
               singleOK = false;
           }
       }
   }
   // Test for normal click event: DCgap expired
   if ( buttonVal == HIGH && (millis()-upTime) >= DCgap && DCwaiting == true && DConUp == false && singleOK == true && event != 2)
   {
       event = 1;
       DCwaiting = false;
   }
   // Test for hold
   if (buttonVal == LOW && (millis() - downTime) >= holdTime) {
       // Trigger "normal" hold
       if (!holdEventPast)
       {
           event = 3;
           waitForUp = true;
           ignoreUp = true;
           DConUp = false;
           DCwaiting = false;
           //downTime = millis();
           holdEventPast = true;
       }
       // Trigger "long" hold
       if ((millis() - downTime) >= longHoldTime)
       {
           if (!longHoldEventPast)
           {
               event = 4;
               longHoldEventPast = true;
           }
       }
   }
   buttonLast = buttonVal;
   return event;
}


void flash_led(const int led_num, int *led_state, unsigned long* prev_time, int blink_time) {
  if ((long)(millis() - *prev_time >= blink_time)) {
    *prev_time = millis();

    *led_state = (*led_state == LOW)? HIGH : LOW;

    digitalWrite(led_num, *led_state);
  }
}

void loop()
{
  // poll button - range 655-0, 500 arbitrary toggle value
  if (is_connected && check_mode_button() == 3) {
    is_haptic_on = !is_haptic_on;
  }

  // turn led check
  if (turn == 1) {
    flash_led(LEFT_LED, &turn_led_state, &turn_led_prev_time, turn_led_blink_time);
  } else if (turn == -1) {
    flash_led(RIGHT_LED, &turn_led_state, &turn_led_prev_time, turn_led_blink_time);
  } else {
    turn_led_state = LOW;
    digitalWrite(LEFT_LED, LOW);
    digitalWrite(RIGHT_LED, LOW);
  }

  // if it is connected to central controller (central controller always sends message)
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

    if(haptic && is_haptic_on){ //Drives the Haptic Motor if Haptic Enabled
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

    // keep status led on
    if (is_haptic_on) {
      digitalWrite(MODE_LED, HIGH);
    } else {
      flash_led(MODE_LED, &status_led_state, &status_led_prev_time, haptic_off_blink_time);
    }

    // track connected time
    last_connected_time = millis();
    is_connected = true;

  } else{
    // signal_counter -= (signal_counter == 0)? 0 : 1;
    // if (signal_counter == 0) {
    //   digitalWrite(MOTOR_CTRL, 0);
    // }
    digitalWrite(MOTOR_CTRL, 0);

    // flash status led
    if ((long)(millis() - last_connected_time >= timeout_time)) { // disconnected
      is_connected = false;
      is_haptic_on = true;
      flash_led(MODE_LED, &status_led_state, &status_led_prev_time, status_led_blink_time);
    }
  }


  if (haptic) {
    // Serial.println("Vibrating!!!");
    // quick flash
    if (turn_led_state == LOW) {
      // Serial.println("light is low!")
      // int flash_state = LOW;
      digitalWrite(LEFT_LED, HIGH);
      digitalWrite(RIGHT_LED, HIGH);
      delay(100);
      digitalWrite(LEFT_LED, LOW);
      digitalWrite(RIGHT_LED, LOW);
      // flash_led(LEFT_LED, &flash_state, &turn_led_prev_time, turn_led_blink_time);
      // flash_led(RIGHT_LED, &turn_led_state, &turn_led_prev_time, turn_led_blink_time);
      delay(100);
    } else {
      // Serial.println("light is !")

    }
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
