import glm
import math

from OpenGL.GL import *

# Define várias opções possíveis para o movimento da câmera. Utilizado como uma abstração para evitar a dependência de métodos de entrada específicos do sistema de janelas.
class Camera_Movement:
    FORWARD  = 0
    BACKWARD = 1
    LEFT     = 2
    RIGHT    = 3

# Valores padrão da câmera
YAW         = -90.0
PITCH       =   0.0
SPEED       =   2.5
SENSITIVITY =   0.1
ZOOM        =  45.0

# Uma classe de câmera abstrata que processa a entrada e calcula os ângulos de Euler, vetores e matrizes correspondentes para uso no OpenGL
class Camera:
    # construtor com vetores
    def __init__(self, position = glm.vec3(0.0, 0.0, 0.0), up = glm.vec3(0.0, 1.0, 0.0), yaw = YAW, pitch = PITCH):
        self.Front = glm.vec3(0.0, 0.0, -1.0)
        self.MovementSpeed = SPEED
        self.MouseSensitivity = SENSITIVITY
        self.Zoom = ZOOM

        self.Position = position
        self.Up = glm.vec3(0.0, 0.0, 0.0)
        self.Right = glm.vec3(0.0, 0.0, 0.0)
        self.WorldUp = up

        self.Yaw = yaw
        self.Pitch = pitch

        self.updateCameraVectors()

    # construtor com valores escalares
    def from_scalars(cls, posX, posY, posZ, upX, upY, upZ, yaw, pitch):
        return cls(
            position = glm.vec3(posX, posY, posZ),
            up = glm.vec3(upX, upY, upZ),
            yaw = yaw,
            pitch = pitch
        )

    # retorna a matriz de visualização calculada usando ângulos de Euler e a matriz LookAt
    def GetViewMatrix(self):
        return glm.lookAt(
            self.Position,
            self.Position + self.Front,
            self.Up
        )

    # Esta função encontra-se na classe de câmera. Basicamente, mantemos o valor da posição Y em 0.0f para forçar
    # o usuário a permanecer no chão.

    # processa a entrada recebida de qualquer sistema de entrada do tipo teclado. Aceita um parâmetro de entrada na forma de um ENUM definido pela câmera (para abstraí-lo de sistemas de janelas)
    def ProcessKeyboard(self, direction, deltaTime):
        velocity = self.MovementSpeed * deltaTime

        if (direction == Camera_Movement.FORWARD):
            self.Position += velocity * self.Front
        if (direction == Camera_Movement.BACKWARD):
            self.Position -= velocity * self.Front
        if (direction == Camera_Movement.LEFT):
            self.Position -= velocity * self.Right
        if (direction == Camera_Movement.RIGHT):
            self.Position += velocity * self.Right

        # garanta que o usuário permaneça no nível do solo
        self.Position.y = 0.0 # <-- esta linha única mantém o usuário no nível do solo (plano xz)

    # processa a entrada recebida de um sistema de entrada de mouse. Espera o valor de deslocamento nas direções x e y.
    def ProcessMouseMovement(self, xoffset, yoffset, constrainPitch = True):
        xoffset *= self.MouseSensitivity
        yoffset *= self.MouseSensitivity

        self.Yaw   += xoffset
        self.Pitch += yoffset

        # certifique-se de que a tela não seja invertida quando o pitch estiver fora dos limites
        if (constrainPitch):
            if (self.Pitch > 89.0):
                self.Pitch = 89.0
            if (self.Pitch < -89.0):
                self.Pitch = -89.0

        # atualiza os vetores Front, Right e Up usando os ângulos de Euler atualizados
        self.updateCameraVectors()

    # processa a entrada recebida de um evento de roda de rolagem do mouse. Requer entrada apenas no eixo vertical da roda.
    def ProcessMouseScroll(self, yoffset):
        self.Zoom -= yoffset

        if (self.Zoom < 1.0):
            self.Zoom = 1.0
        if (self.Zoom > 45.0):
            self.Zoom = 45.0

    # calcula o vetor frontal a partir dos ângulos de Euler (atualizados) da câmera
    def updateCameraVectors(self):
        # calcula o novo vetor Front
        front = glm.vec3(0.0, 0.0, 0.0)
        front.x = math.cos(glm.radians(self.Pitch)) * math.cos(glm.radians(self.Yaw))
        front.y = math.sin(glm.radians(self.Pitch))
        front.z = math.cos(glm.radians(self.Pitch)) * math.sin(glm.radians(self.Yaw))

        self.Front = glm.normalize(front)

        # também recalcule os vetores Direita e Cima
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp)) # Normaliza os vetores, pois o comprimento deles se aproxima de zero quanto mais você olha para cima ou para baixo, o que resulta em um movimento mais lento.
        self.Up = glm.normalize(glm.cross(self.Right, self.Front))
