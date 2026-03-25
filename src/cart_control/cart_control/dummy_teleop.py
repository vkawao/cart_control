import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class DummyTeleop(Node):
    def __init__(self):
        super().__init__('dummy_teleop_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Dummy Teleop Started. Ready to transmit drive commands.")

    def send_command(self, linear):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = 0.0  # Zeroed out since steering is handled elsewhere
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published -> Linear: {linear}")

def main(args=None):
    rclpy.init(args=args)
    teleop_node = DummyTeleop()

    print("\n" + "="*30)
    print("   AUTOBUS DUMMY TELEOP (DRIVE ONLY)")
    print("="*30)
    print("  [ w ] : Forward (+0.5 m/s)")
    print("  [ s ] : Reverse (-0.5 m/s)")
    print("  [ x ] : Stop    ( 0.0 m/s)")
    print("  [ q ] : Quit")
    print("="*30)

    try:
        while rclpy.ok():
            choice = input("\nEnter command: ").strip().lower()
            
            if choice == 'w':
                teleop_node.send_command(0.5)
            elif choice == 's':
                teleop_node.send_command(-0.5)
            elif choice == 'x':
                teleop_node.send_command(0.0)
            elif choice == 'q':
                print("Shutting down teleop...")
                break
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        pass
    finally:
        teleop_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()