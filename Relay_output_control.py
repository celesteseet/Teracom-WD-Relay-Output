from pysnmp.hlapi import *
import time
import subprocess

# SNMP Configuration
DEVICE_IP = '192.168.1.2'  # TCW122B-WD IP address
COMMUNITY = 'private'       # SNMP Community String

# OIDs (Object Identifiers) for different functionalities
LED_STATE_OID = '1.3.6.1.4.1.38783.3.4.0'  # OID for controlling the LED state
BUZZER_OID = '1.3.6.1.4.1.38783.3.5.0'  # OID for controlling the buzzer state
DIGITAL_INPUT_OID = '1.3.6.1.4.1.38783.3.6.0'  # OID for monitoring button press (Digital Input)

# LED State Values (Defined by the Status Table)
LED_GREEN = 1           # Green: System is OK
LED_AMBER = 2           # Amber: No Communication
LED_BLINKING_RED = 3    # Blinking Red: Alarm (Unacknowledged)
LED_SOLID_RED = 4       # Solid Red: Alarm (Acknowledged)

# Buzzer State Values
BUZZER_ON = 1           # Buzzer ON
BUZZER_OFF = 0          # Buzzer OFF

# Function to set SNMP value (change LED or buzzer state etc.)
def set_snmp_value(ip, community, oid, value):
    """
    Sends an SNMP SET command to modify a value on the device.

    Parameters:
    ip (str): Device IP address
    community (str): SNMP community string
    oid (str): OID to be modified
    value (int): Value to set (e.g., LED or Buzzer state)
    """
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid), Integer(value)))
    )
    if errorIndication:
        print(f"Error: {errorIndication}")
    elif errorStatus:
        print(f"Error: {errorStatus.prettyPrint()}")
    else:
        print(f"Set {oid} to {value} successfully.")

# Function to get SNMP value (monitor button press or relay state etc.)
def get_snmp_value(ip, community, oid):
    """
    Sends an SNMP GET command to retrieve a value from the device.

    Parameters:
    ip (str): Device IP address
    community (str): SNMP community string
    oid (str): OID to retrieve value from

    Returns:
    int: Value retrieved from the device
    """
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication:
        print(f"Error: {errorIndication}")
        return None
    elif errorStatus:
        print(f"Error: {errorStatus.prettyPrint()}")
        return None
    else:
        for name, val in varBinds:
            return int(val)

# Main Function to Control LED and Buzzer Based on System Status and Acknowledgment
def control_led_and_buzzer():
    """
    Main function to monitor the system status, control LED states, and manage the buzzer.
    """
    try:
        current_state = LED_GREEN  # Start with system OK state (Green LED)

        while True:
            # Simulate system conditions (replace this with actual logic to monitor system status)
            system_status = check_system_status()  # Returns 'ok', 'no_comm', or 'alarm'

            # State 1: No Communication Detected (Amber LED)
            if system_status == "no_comm":
                current_state = LED_AMBER
                set_snmp_value(DEVICE_IP, COMMUNITY, LED_STATE_OID, LED_AMBER)  # Set LED to Amber
                set_snmp_value(DEVICE_IP, COMMUNITY, BUZZER_OID, BUZZER_OFF)    # Ensure Buzzer is OFF

            # State 2: Alarm Detected (Blinking Red LED & Buzzer ON)
            elif system_status == "alarm":
                # Check Digital Input (Button) for Acknowledgment
                button_state = get_snmp_value(DEVICE_IP, COMMUNITY, DIGITAL_INPUT_OID)
                if button_state == 1:  # Button Pressed
                    current_state = LED_SOLID_RED
                    set_snmp_value(DEVICE_IP, COMMUNITY, LED_STATE_OID, LED_SOLID_RED)  # Set LED to Solid Red
                    set_snmp_value(DEVICE_IP, COMMUNITY, BUZZER_OID, BUZZER_OFF)        # Turn Buzzer OFF
                else:
                    current_state = LED_BLINKING_RED
                    set_snmp_value(DEVICE_IP, COMMUNITY, LED_STATE_OID, LED_BLINKING_RED)  # Set LED to Blinking Red
                    set_snmp_value(DEVICE_IP, COMMUNITY, BUZZER_OID, BUZZER_ON)            # Turn Buzzer ON

            # State 3: System OK (Green LED)
            elif system_status == "ok":
                current_state = LED_GREEN
                set_snmp_value(DEVICE_IP, COMMUNITY, LED_STATE_OID, LED_GREEN)  # Set LED to Green
                set_snmp_value(DEVICE_IP, COMMUNITY, BUZZER_OID, BUZZER_OFF)    # Ensure Buzzer is OFF

            # Wait before next iteration (polling interval)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program stopped by user.")


# Simulated Function to Check System Status (Actual logic TBD)
def check_system_status():
    """
    Simulates checking the system status.

    Returns:
    str: System status ('ok', 'no_comm', 'alarm')
    """
    return "ok"  # Placeholder: tbd

# Run the Main Control Function
control_led_and_buzzer()



# Network Loss Detection
# Pings the device using its IP address.
# If the ping succeeds, the function returns "ok".
# If the ping fails, the function returns "no_comm"

# def check_system_status():
#     """
#     Monitors the network status by pinging the device.
#     Returns:
#     str: System status ('ok', 'no_comm', 'alarm')
#     """

#     try:
#         response = subprocess.run(['ping', '-c', '1', DEVICE_IP], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         if response.returncode == 0:
#             return "ok"  # Device is reachable
#         else:
#             return "no_comm"  # No communication (ping failed)
#     except Exception as e:
#         print(f"Error checking network status: {e}")
#         return "no_comm"





# Alarm Detection Based on SNMP
# Uses the get_snmp_value function to query the device for the alarm OID.
# If the OID returns a value indicating an alarm (e.g., 1), it reports "alarm".
# If the SNMP request fails, it assumes there is "no_comm".

# def check_system_status():
#     """
#     Monitors the system alarm status by querying a specific OID.
#     Returns:
#     str: System status ('ok', 'alarm')
#     """

#     alarm_oid = '1.3.6.1.4.1.38783.3.7.0'  # Replace with actual Alarm OID
#     alarm_value = get_snmp_value(DEVICE_IP, COMMUNITY, alarm_oid)
    
#     if alarm_value is not None:
#         if alarm_value == 1:  # Assuming '1' indicates an alarm condition
#             return "alarm"
#         else:
#             return "ok"
#     else:
#         return "no_comm"  # If unable to fetch SNMP value, assume no communication






# Network Loss and Alarm Monitoring
# First checks the network connection with a ping command.
# If the device is reachable, it then queries the alarm status via SNMP.
# Returns one of three states:
# "ok": Device is reachable, no alarms.
# "no_comm": Device is unreachable.
# "alarm": Device reports an alarm condition.

# def check_system_status():
#     """
#     Checks both network status and alarm conditions.
#     Returns:
#     str: System status ('ok', 'no_comm', 'alarm')
#     """

#     # Step 1: Check network connectivity
#     try:
#         response = subprocess.run(['ping', '-c', '1', DEVICE_IP], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         if response.returncode != 0:
#             return "no_comm"  # No communication
#     except Exception as e:
#         print(f"Error checking network status: {e}")
#         return "no_comm"

#     # Step 2: Check alarm status via SNMP
#     alarm_oid = '1.3.6.1.4.1.38783.3.7.0'  # Replace with actual Alarm OID
#     alarm_value = get_snmp_value(DEVICE_IP, COMMUNITY, alarm_oid)
    
#     if alarm_value is not None and alarm_value == 1:
#         return "alarm"
    
#     return "ok"  # Everything is OK




# Polling Relay/Digital Input
# Queries the relay OID using SNMP.
# If the relay is ON (value 1), it reports "alarm".
# If the relay is OFF, it reports "ok".

# def check_system_status():
#     """
#     Polls the relay state to check for alarms.
#     Returns:
#     str: System status ('ok', 'alarm')
#     """

#     relay_oid = '1.3.6.1.4.1.38783.3.3.0'  # Replace with actual Relay OID
#     relay_value = get_snmp_value(DEVICE_IP, COMMUNITY, relay_oid)
    
#     if relay_value is not None and relay_value == 1:  # Assuming '1' means alarm
#         return "alarm"
#     return "ok"

