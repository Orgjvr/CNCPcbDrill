from . import serial_rx_tx



def setupSerial():
    global serialPort
    serialPort = serial_rx_tx.SerialPort()
    getSerialPorts()
    printSerialPorts()

def getSerialPorts():
    global sPorts
    sPorts = serialPort.GetSerialPorts()

def printSerialPorts():
    print("Ports=")
    print(sPorts)



# serial data callback function
def OnReceiveSerialData(message):
    str_message = message.decode("utf-8")

    print("COM:%s"%(str_message))
    

setupSerial()   



# Register the callback above with the serial port object
serialPort.RegisterReceiveCallback(OnReceiveSerialData)
