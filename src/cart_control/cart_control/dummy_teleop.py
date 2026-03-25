import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class DummyTeleop(Node):
    def __init__(self):
        super().__init__('dummy_teleop_node')
        # This node is a PUBLISHER. It broadcasts to /cmd_vel.
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Dummy Teleop Started. Ready to transmit.")

    def send_command(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published -> Linear: {linear}, Angular: {angular}")

def main(args=None):
    rclpy.init(args=args)
    teleop_node = DummyTeleop()

    print("\n" + "="*30)
    print("   AUTOBUS DUMMY TELEOP")
    print("="*30)
    print("  [ w ] : Forward (+0.5 m/s)")
    print("  [ s ] : Reverse (-0.5 m/s)")
    print("  [ x ] : Stop    ( 0.0 m/s)")
    print("  [ a ] : Left    (+0.5 rad/s)")
    print("  [ d ] : Right   (-0.5 rad/s)")
    print("  [ q ] : Quit")
    print("="*30)

    try:
        # We use a simple while loop to wait for your keyboard input
        while rclpy.ok():
            choice = input("\nEnter command: ").strip().lower()
            
            if choice == 'w':
                teleop_node.send_command(0.5, 0.0)
            elif choice == 's':
                teleop_node.send_command(-0.5, 0.0)
            elif choice == 'x':
                teleop_node.send_command(0.0, 0.0)
            elif choice == 'a':
                teleop_node.send_command(0.0, 0.5)
            elif choice == 'd':
                teleop_node.send_command(0.0, -0.5)
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