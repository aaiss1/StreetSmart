#include<SPI.h>
#include<RF24.h>

// ce, csn pins
RF24 radio(9, 10) ;

void setup(void){
  while (!Serial) ;
  Serial.begin(9600) ;
  uint8_t address[][6] = { "1Node", "2Node" };

  radio.begin() ;
  radio.setPALevel(RF24_PA_MAX) ;
  radio.setChannel(150);
  radio.setDataRate(RF24_1MBPS);
  radio.openWritingPipe(address[1]);
  radio.openReadingPipe(1, address[0]) ;
  
  radio.enableDynamicPayloads() ;
  radio.powerUp() ;
  
}

void loop(void){
  radio.startListening() ;
  Serial.println("Starting loop. Radio on.") ;
  char receivedMessage[32] = {0} ;
  if (radio.available()){
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage) ;
    Serial.println("Turning off the radio.") ;
    radio.stopListening() ;
    
    String stringMessage(receivedMessage) ;
    
    if (stringMessage == "GETSTRING"){
      Serial.println("Looks like they want a string!") ;
      const char text[] = "Hello World!" ;
      radio.write(text, sizeof(text)) ;
      Serial.println("We sent our message.") ;
    }
    
  }
  
  delay(100) ;
  
  
}