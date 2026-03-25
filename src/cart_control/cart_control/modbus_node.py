import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from pymodbus.client import ModbusSerialClient

class ControllinoModbus(Node):
    def __init__(self):
        super().__init__('controllino_modbus_node')
        
        # --- LINUX SERIAL CONFIGURATION ---
        self.port = '/dev/ttyUSB0'  # Check with 'ls /dev/tty*' (might be /dev/ttyACM0)
        self.baudrate = 115200
        self.slave_id = 1
        
        # Initialize Modbus Connection
        self.client = ModbusSerialClient(port=self.port, baudrate=self.baudrate)
        if not self.client.connect():
            self.get_logger().error(f"CRITICAL: Cannot connect to Controllino on {self.port}.")
        else:
            self.get_logger().info("SUCCESS: Connected to Controllino via Modbus RTU.")

        # Subscribe to the velocity commands
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        # Initialize safe default states (Brakes on, Neutral gear)
        gear = 1      # 1 = Neutral
        reverse = 0   # 0 = Off
        brake = 1     # 1 = Low Brake
        steering = 1  # 1 = Center (Assuming 0=Left, 1=Center, 2=Right for %QW14)
        
        # --- DRIVE LOGIC EVALUATION ---
        if linear_x > 0.05:
            # Moving Forward
            gear = 2
            reverse = 0
            brake = 0
            self.get_logger().info("Cmd: FORWARD -> Gear: High, Brakes: Released")
            
        elif linear_x < -0.05:
            # Moving Backward
            gear = 0      # Ensure your cart allows gear 0 for reverse
            reverse = 1
            brake = 0
            self.get_logger().info("Cmd: REVERSE -> Gear: Low, Reverse: ON, Brakes: Released")
            
        else:
            # Stopped (Deadband between -0.05 and 0.05 filters sensor noise)
            gear = 1
            reverse = 0
            brake = 1
            self.get_logger().info("Cmd: STOP -> Gear: Neutral, Brakes: Engaged")

        # --- STEERING LOGIC EVALUATION ---
        if angular_z > 0.1:
            steering = 2 # Turn Left
        elif angular_z < -0.1:
            steering = 0 # Turn Right
        else:
            steering = 1 # Center
        
        # --- SEND TO CONTROLLINO ---
        try:
            self.client.write_register(address=10, value=gear, slave=self.slave_id)
            self.client.write_register(address=11, value=reverse, slave=self.slave_id)
            self.client.write_register(address=12, value=brake, slave=self.slave_id)
            # Make sure you map %QW14 in OpenPLC before uncommenting the line below!
            # self.client.write_register(address=14, value=steering, slave=self.slave_id) 
            
        except Exception as e:
            self.get_logger().error(f"Modbus transmission error: {e}")

def main(args=None):
    rclpy.init(args=args)
    modbus_node = ControllinoModbus()
    
    try:
        rclpy.spin(modbus_node)
    except KeyboardInterrupt:
        modbus_node.get_logger().info("Node stopped manually.")
    finally:
        # Always release the serial port safely on shutdown
        modbus_node.client.close()
        modbus_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()