from RF24 import *
import global_vars
import sys
import time


CSN_PIN = 0  # connected to GPIO8
CE_PIN = 17  # connected to GPIO22
radio = RF24(CE_PIN, CSN_PIN)

def start_comm():
     # initialize the nRF24L01 on the spi bus
    if not radio.begin():
        raise RuntimeError("radio hardware is not responding")

    # For this example, we will use different addresses
    # An address need to be a buffer protocol object (bytearray)
    address = [b"1Node", b"2Node"]
    # It is very helpful to think of an address as a path instead of as
    # an identifying device destination

    print(sys.argv[0])  # print example name

    # to use different addresses on a pair of radios, we need a variable to
    # uniquely identify which address this radio will use to transmit
    # 0 uses address[0] to transmit, 1 uses address[1] to transmit
    radio_number = 0  # uses default value from `parser`

    # ACK payloads are dynamically sized.
    radio.enableDynamicPayloads()  # to use ACK payloads

    # to enable the custom ACK payload feature
    radio.enableAckPayload()

    # set the Power Amplifier level to -12 dBm since this test example is
    # usually run with nRF24L01 transceivers in close proximity of each other
    radio.setPALevel(RF24_PA_MIN)  # RF24_PA_MAX is default
    
    radio.setChannel(150)

    # set the TX address of the RX node into the TX pipe
    radio.openWritingPipe(address[radio_number])  # always uses pipe 0

    # set the RX address of the TX node into a RX pipe
    radio.openReadingPipe(1, address[not radio_number])  # using pipe 1

    # for debugging, we have 2 options that print a large block of details
    # (smaller) function that prints raw register values
    # radio.printDetails()
    # (larger) function that prints human readable data
    # radio.printPrettyDetails()
    
    """Transmits a message and an incrementing integer every second."""
    radio.stopListening()  # put radio in TX mode
    failures = 0
    while not global_vars.kill_comm_thread.is_set():
        # construct a payload to send
        buffer = b"Haptic: \x00" + global_vars.haptic.to_bytes(2, "little", signed=True)
        # send the payload and prompt
        start_timer = time.monotonic_ns()  # start timer
        result = radio.write(buffer)  # save the report
        end_timer = time.monotonic_ns()  # stop timer
        if result:
            # print timer results upon transmission success
            decoded = buffer[:8].decode("utf-8")
            print(
                "Transmission successful! Time to transmit:",
                f"{int((end_timer - start_timer) / 1000)} us.",
                f"Sent: {decoded}{global_vars.haptic}",
                end=" ",
            )
            has_payload, pipe_number = radio.available_pipe()
            if has_payload:
                # print the received ACK that was automatically sent
                length = radio.getDynamicPayloadSize()
                response = radio.read(length)
                decoded = bytes(response[:6]).decode("utf-8")
                global_vars.turn = int.from_bytes(bytes(response[9:12]), byteorder='little', signed=True)
                print(
                    f"Received {length} on pipe {pipe_number}:",
                    f"{decoded}{global_vars.turn}",
                )

            else:
                print("Received an empty ACK packet")
        else:
            failures += 1
            print("Transmission failed or timed out")
        time.sleep(0.1)  # let the RX node prepare a new ACK payload
    end_comm()
    print("Comms Killed")


def end_comm():
    radio.powerDown()
