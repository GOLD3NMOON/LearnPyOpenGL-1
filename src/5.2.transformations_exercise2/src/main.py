import glfw
import sys
import math
import glm

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
    ourShader = Shader("res/shaders/transform.vs", "res/shaders/transform.fs")

    # configura dados de vértice (e buffer(s)) e configura atributos de vértice
    # --------------------------------------------------
    vertices = np.array([
        # positions         # texture coords
        -0.5, -0.5,  0.0,   0.0, 0.0, # inferior esquerdo
         0.5, -0.5,  0.0,   1.0, 0.0, # inferior direito
         0.5,  0.5,  0.0,   1.0, 1.0, # superior direito
        -0.5,  0.5,  0.0,   0.0, 1.0  # superior esquerdo
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
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # texture coord attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    glEnableVertexAttribArray(1)

    # carregar e criar uma textura
    # --------------------------------------------------

    # texture 1
    # --------------------------------------------------
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1)

    # define os parâmetros de repetição da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # define o modo de repetição da textura como GL_REPEAT (método padrão)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    #// definir parâmetros de filtragem de textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # carregar imagem, criar textura e gerar mipmaps
    img = Image.open("res/textures/container.jpg")
    img = img.transpose(Image.FLIP_TOP_BOTTOM) # Instrua o stb_image.h a inverter as texturas carregadas no eixo Y.
    img = img.convert("RGB")

    width, height = img.size
    data = np.array(img, dtype=np.uint8)

    if (data is not None):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        print("Falha ao carregar a textura")        

    # texture 2
    # --------------------------------------------------
    texture2 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture2)

    # define os parâmetros de repetição da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # define o modo de repetição da textura como GL_REPEAT (método padrão)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    #// definir parâmetros de filtragem de textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # carregar imagem, criar textura e gerar mipmaps
    img = Image.open("res/textures/awesomeface.png")
    img = img.transpose(Image.FLIP_TOP_BOTTOM) # Instrua o stb_image.h a inverter as texturas carregadas no eixo Y.
    img = img.convert("RGBA")

    width, height = img.size
    data = np.array(img, dtype=np.uint8)

    if (data is not None):
        # observe que o awesomeface.png possui transparência e, portanto, um canal alfa; certifique-se de informar ao OpenGL que o tipo de dado é GL_RGBA
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        print("Falha ao carregar a textura") 

    # informar ao OpenGL, para cada sampler, a qual unidade de textura ele pertence (isso só precisa ser feito uma vez)
    # --------------------------------------------------
    ourShader.use()
    ourShader.setInt("texture1", 0)
    ourShader.setInt("texture2", 1)

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

        # vincular texturas às unidades de textura correspondentes
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, texture2)

        transform = glm.mat4(1.0) # certifique-se de inicializar a matriz como a matriz identidade primeiro

        # primeiro contêiner
        # --------------------------------------------------
        transform = glm.translate(transform, glm.vec3(0.5, -0.5, 0.0))
        transform = glm.rotate(transform, glfw.get_time(), glm.vec3(0.0, 0.0, 1.0))

        # obtém a localização do uniform e define a matriz (usando glm::value_ptr)
        ourShader.use()
        transformLoc = glGetUniformLocation(ourShader.ID, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(transform))

        # com a matriz uniforme definida, desenhe o primeiro contêiner
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, c_void_p(0))

        # segunda transformação
        # --------------------------------------------------
        transform = glm.mat4(1.0) # redefini-la para a matriz identidade
        transform = glm.translate(transform, glm.vec3(-0.5, 0.5, 0.0))
        scaleAmount = math.sin(glfw.get_time())
        transform = glm.scale(transform, glm.vec3(scaleAmount, scaleAmount, scaleAmount))
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(transform)) # desta vez, utilize o primeiro elemento do array de valores da matriz como o valor do seu ponteiro de memória

        # agora, com a matriz uniform sendo substituída por novas transformações, desenhe-o novamente.
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
