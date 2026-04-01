import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty

class IncrementalTeleop(Node):
    def __init__(self):
        super().__init__('incremental_teleop_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.current_speed = 0.0
        self.speed_step = 0.1

    def update_and_publish(self, speed_change):
        if speed_change == 0:
            self.current_speed = 0.0
        else:
            self.current_speed = round(self.current_speed + speed_change, 2)
            
        msg = Twist()
        msg.linear.x = self.current_speed
        msg.angular.z = 0.0
        
        self.publisher_.publish(msg)
        print(f"\rPublished Speed: {self.current_speed} m/s    ", end='')

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    import select
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    rclpy.init(args=args)
    teleop_node = IncrementalTeleop()
    settings = termios.tcgetattr(sys.stdin)

    print("\n" + "="*35)
    print(" AUTOBUS INCREMENTAL TELEOP")
    print("="*35)
    print("  [ w ] : Increase speed (+0.1)")
    print("  [ s ] : Decrease speed (-0.1)")
    print("  [ x ] : Force Stop     (0.0)")
    print("  [ q ] : Quit")
    print("="*35)

    try:
        while rclpy.ok():
            key = get_key(settings)
            
            if key == 'w':
                teleop_node.update_and_publish(teleop_node.speed_step)
            elif key == 's':
                teleop_node.update_and_publish(-teleop_node.speed_step)
            elif key == 'x':
                teleop_node.update_and_publish(0.0)
            elif key == 'q' or key == '\x03': # \x03 is Ctrl+C
                break
                
    except Exception as e:
        print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        teleop_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()