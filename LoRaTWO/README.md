# handmade LoraWAN

LoRaWAN is a Media Access Control (MAC) layer protocol built on top of LoRa modulation.

End Devices - sensors or actuators send LoRa modulated wireless messages to the gateways or receive messages wirelessly back from the gateways.
Gateways - receive messages from end devices and forward them to the Network Server.
Network Server - manages the entire network.
Application server - is responsible for securely processing application data.
Join Server - a piece of software running on a server that processes join-request messages sent by end devices. 

# network server
-> Establishing secure 128-bit AES connections for the transport of messages between end-devices and the Application Server (end-to-end security)
-> Validating the authenticity of end devices and integrity of messages.
-> Deduplicating uplink messages.
Selecting the best gateway for routing downlink messages.
Selecting the best gateway for routing downlink messages.
-> (for actuators) Providing acknowledgements of confirmed uplink data messages.
Routing uplink application payloads to the appropriate Application Server.
Forwarding Join-request and Join-accept messages between the devices and the join server.
Responding to all MAC layer commands.

# application server
The Application Server processes application-specific data messages received from end devices.
It also generates all the application-layer downlink payloads and sends them to the connected end devices through the Network Server.
A LoRaWAN network can have more than one Application Server. The collected data can be interpreted by applying techniques like machine learning and artificial intelligence to solve business problems.

# end device acrtivation
Every end device must be registered with a network before sending and receiving messages. This procedure is known as activation. There are two activation methods available:
-> Over-The-Air-Activation (OTAA) - the most secure and recommended activation method for end devices. Devices perform a join procedure with the network, during which a dynamic device address is assigned and security keys are negotiated with the device.
Activation By Personalization (ABP) - requires hardcoding the device address as well as the security keys in the device. ABP is less secure than OTAA and also has the downside that devices can not switch network providers without manually changing keys in the device

# loraWAN device classes
A for battery powered sensors
B for battery powered actuators
C for mains powered actuators

# class A
All LoRaWAN end-devices must support Class A implementation. Class A communication is always initiated by the end-device.
A device can send an uplink message at any time. Once the uplink transmission is completed the device opens two short receive (downlink) windows. There is a delay between the end of the uplink transmission and the start of the receive windows (RX1 and RX2 respectively). If the network server does not respond during these two receive windows, the next downlink will be after the next uplink transmission.

# class B
In addition to the class A initiated receive windows, Class B devices open scheduled receive windows for receiving downlink messages from the network server. Using time-synchronized beacons transmitted by the gateway, the devices periodically open receive windows. The time between two beacons is known as the beacon period. The device opens downlink ‘ping slots’ at scheduled times for receiving downlink messages from the network server. Class B devices also open receive windows after sending an uplink.

# class C
Class C devices extend Class A by keeping the receive windows open unless they are transmitting, as shown in the figure below. This allows for low-latency communication but is many times more energy consuming than Class A devices.

# questions
ttn puo fare anche da concentrator?
se no è possibile fare una rete loraWAN senza concentrator?