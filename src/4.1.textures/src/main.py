import glfw
import sys
import math

import numpy as np

from ctypes import *
from OpenGL.GL import *

from PIL import Image
from shader import Shader

# configurações
SCR_WIDTH = 800
SCR_HEIGHT = 600

def main():
    # glfw: inicializar e configurar
    # --------------------------------------------------
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    if (sys.platform == "darwin"):
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

    # criação da janela glfw
    # --------------------------------------------------
    window = glfw.create_window(SCR_WIDTH, SCR_HEIGHT, "Leran PyOpenGL", None, None)

    if (window == None):
        print("Falha ao criar a janela GLFW")
        glfw.terminate()
        return

    if (sys.platform == "win32"):
        # Obtém o tamanho da janela passado para glfwCreateWindow
        pWidth, pHeight = glfw.get_window_size(window)

        # Obtém a resolução do monitor principal
        vidMode = glfw.get_video_mode(glfw.get_primary_monitor())

        # Centralizar a janela
        glfw.set_window_pos(
            window,
            (vidMode.width - pWidth) // 2,
            (vidMode.height - pHeight) // 2
        )

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # Ativar v-sync
    glfw.swap_interval(1)

    # construir e compilar nosso programa de shader
    # --------------------------------------------------
    ourShader = Shader("res/shaders/texture.vs", "res/shaders/texture.fs")

    # configura dados de vértice (e buffer(s)) e configura atributos de vértice
    # --------------------------------------------------
    vertices = np.array([
        # positions         # colors         # texture coords
        -0.5, -0.5,  0.0,   1.0, 0.0, 0.0,   0.0, 0.0, # inferior esquerdo
         0.5, -0.5,  0.0,   0.0, 1.0, 0.0,   1.0, 0.0, # inferior direito
         0.5,  0.5,  0.0,   0.0, 0.0, 1.0,   1.0, 1.0, # superior direito
        -0.5,  0.5,  0.0,   1.0, 1.0, 0.0,   0.0, 1.0  # superior esquerdo
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2,
        0, 2, 3
    ], dtype=np.uint32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # color attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    glEnableVertexAttribArray(1)

    # texture coord attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(6 * sizeof(c_float)))
    glEnableVertexAttribArray(2)

    # carregar e criar uma textura
    # --------------------------------------------------
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture) # todas as operações GL_TEXTURE_2D subsequentes agora afetam este objeto de textura

    # define os parâmetros de repetição da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # define o modo de repetição da textura como GL_REPEAT (método padrão)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    #// definir parâmetros de filtragem de textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # carregar imagem, criar textura e gerar mipmaps
    img = Image.open("res/textures/container.jpg")
    img = img.convert("RGB")

    width, height = img.size
    data = np.array(img, dtype=np.uint8)

    if (data is not None):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        print("Falha ao carregar a textura")        

    # loop de renderização
    # --------------------------------------------------
    while (not glfw.window_should_close(window)):
        # input
        # --------------------------------------------------
        processInput(window)

        # render
        # --------------------------------------------------
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # vincular textura
        glBindTexture(GL_TEXTURE_2D, texture)

        # renderizar contêiner
        ourShader.use()
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, c_void_p(0))

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(1, VAO)
    glDeleteBuffers(1, VBO)
    glDeleteBuffers(1, EBO)

    # glfw: finaliza, limpando todos os recursos GLFW alocados anteriormente.
    # --------------------------------------------------
    glfw.terminate()
    return

# processar toda a entrada: consultar a GLFW para verificar se teclas relevantes foram pressionadas ou liberadas neste quadro e reagir de acordo
# --------------------------------------------------
def processInput(window):
    if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)

# glfw: sempre que o tamanho da janela é alterado (pelo SO ou por redimensionamento do usuário), esta função de callback é executada
# --------------------------------------------------
def framebuffer_size_callback(window, width, height):
    # certifique-se de que a viewport corresponda às novas dimensões da janela; observe que a largura e
    # a altura serão significativamente maiores do que as especificadas em telas Retina.
    glViewport(0, 0, width, height)    

if (__name__ == "__main__"):
    main()
