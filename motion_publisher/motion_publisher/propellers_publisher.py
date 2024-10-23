import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import threading
import readchar

class WamvTeleopPublisher(Node):

    def __init__(self):
        super().__init__('wamv_teleop_publisher')

        # Publicadores para los tópicos de posición
        self.left_pos_pub = self.create_publisher(Float64, '/wamv/thrusters/left/pos', 10)
        self.right_pos_pub = self.create_publisher(Float64, '/wamv/thrusters/right/pos', 10)

        # Publicadores para los tópicos de empuje
        self.left_thrust_pub = self.create_publisher(Float64, '/wamv/thrusters/left/thrust', 10)
        self.right_thrust_pub = self.create_publisher(Float64, '/wamv/thrusters/right/thrust', 10)

        timer_period = 0.1  # segundos
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Comando inicial
        self.command = 'stop'

        # Iniciar hilo para entrada de teclado
        self.input_thread = threading.Thread(target=self.keyboard_input_thread)
        self.input_thread.daemon = True
        self.input_thread.start()

    def keyboard_input_thread(self):
        self.get_logger().info('Control del WAM-V con el teclado:')
        self.get_logger().info('w: adelante, s: atrás, a: izquierda, d: derecha, espacio: detener, q: salir')

        while rclpy.ok():
            key = readchar.readkey()
            if key == 'w':
                self.command = 'adelante'
            elif key == 's':
                self.command = 'atrás'
            elif key == 'a':
                self.command = 'izquierda'
            elif key == 'd':
                self.command = 'derecha'
            elif key == ' ':
                self.command = 'stop'
            elif key == 'q':
                self.get_logger().info('Saliendo...')
                rclpy.shutdown()
                break
            else:
                self.command = 'stop'

    def timer_callback(self):
        # Publicar cero en los tópicos de posición
        pos_msg = Float64()
        pos_msg.data = 0.0
        self.left_pos_pub.publish(pos_msg)
        self.right_pos_pub.publish(pos_msg)

        # Configurar valores de empuje según el comando
        left_thrust_msg = Float64()
        right_thrust_msg = Float64()

        if self.command == 'adelante':
            left_thrust_msg.data = 10.0
            right_thrust_msg.data = 10.0
        elif self.command == 'atrás':
            left_thrust_msg.data = -10.0
            right_thrust_msg.data = -10.0
        elif self.command == 'izquierda':
            left_thrust_msg.data = -10.0
            right_thrust_msg.data = 10.0
        elif self.command == 'derecha':
            left_thrust_msg.data = 10.0
            right_thrust_msg.data = -10.0
        else:
            left_thrust_msg.data = 0.0
            right_thrust_msg.data = 0.0

        self.left_thrust_pub.publish(left_thrust_msg)
        self.right_thrust_pub.publish(right_thrust_msg)

        # Mostrar en el registro el comando y los valores de empuje
        self.get_logger().info(f'Comando: {self.command}, Empuje izquierda: {left_thrust_msg.data}, Empuje derecha: {right_thrust_msg.data}')

def main(args=None):
    rclpy.init(args=args)
    wamv_teleop_publisher = WamvTeleopPublisher()
    try:
        rclpy.spin(wamv_teleop_publisher)
    except KeyboardInterrupt:
        pass
    wamv_teleop_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
