import machine
import time
import feathers3
import array

# Define analog input pins
inp1_pin = 14 #A2 reference voltage
inp2_pin = 6 #A4 flex sensor voltage

# enable 3v3 LDO
test_counter = 0

while True:
    deltaReading = []
    for i in range(50):
        # Read analog input values
        inp1 = machine.ADC(machine.Pin(inp1_pin))
        inp2 = machine.ADC(machine.Pin(inp2_pin))
        deltaADC = inp2.read() - inp1.read()
        deltaReading.append(deltaADC)
        time.sleep_ms(50)
    
    deltaSum = 0
    deltaMax = 0
    deltaMin = 4095
    for reading in deltaReading:
        deltaSum = deltaSum + reading
        if reading > deltaMax:
            deltaMax = reading
        elif reading < deltaMin:
            deltaMin = reading

    print("Test " + str(test_counter))
    # Calculate average and voltage values
    deltaAvg = deltaSum / len(deltaReading)
    deltaVoltage = deltaAvg * (3.3 / 4095)
    
    # Print results
    print("Min: " + str(int(deltaMin)))
    print("Avg: " + str(int(deltaAvg)))
    print("Max: " + str(int(deltaMax)))
    print("ADC Range: " + str(int(deltaMax - deltaMin)))
    print("Delta Voltage: " + str(deltaVoltage) + "\n")
    
    test_counter = test_counter + 1
    # Record 6th reading as measured min avg max test_counter = 5