from RF24 import *
import time
import spidev
import struct 

address = [b"1Node", b"2Node"]

CSN_PIN = 0  # connected to GPIO8
CE_PIN = 17  # connected to GPIO17
radio = RF24(CE_PIN, CSN_PIN)
radio.begin()

radio.setPayloadSize(32)
radio.setChannel(150)
radio.setDataRate(RF24_1MBPS)
radio.setPALevel(RF24_PA_LOW)

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(address[0])
radio.openReadingPipe(1, address[1])
radio.printDetails()
#radio.startListening()

message = list("GETSTRING")
while len(message) < 32:
    message.append(0)

while True:
    start = time.time()

    radio.write(b"1Node")
    print("Sent the message: {}".format(message))
    radio.startListening()
    
    # while not radio.available(0):
    #     time.sleep(1/100)
    #     if time.time() - start > 2:
    #         print("Timed out.")
    #         break

    receivedMessage = []
    buffer = radio.read(radio.payloadSize)
    print("Received: {}".format(receivedMessage))

    print("Translating our received Message into unicode characters...")
    string = ""

    for n in receivedMessage:
        if (n >= 32 and n <= 126):
            string += chr(n)
    print("Our received message decodes to: {}".format(string))

    radio.stopListening()
    time.sleep(1)
