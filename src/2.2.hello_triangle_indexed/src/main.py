import glfw
import sys
import numpy as np
from ctypes import *
from OpenGL.GL import *

# configurações
SCR_WIDTH = 800
SCR_HEIGHT = 600

vertexShaderSource = """
    #version 330 core
    layout (location = 0) in vec3 aPos;

    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
    }
"""

fragmentShaderSource = """
    #version 330 core
    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
    }
"""

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

    # vertex shader
    vertexShader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShader, vertexShaderSource)
    glCompileShader(vertexShader)

    # verificar erros de compilação de shader
    success = glGetShaderiv(vertexShader, GL_COMPILE_STATUS)
    if (success == 0):
        infoLog = glGetShaderInfoLog(vertexShader)
        print(
            "ERROR::SHADER::VERTEX::COMPILATION_FAILED" + "\n" +
            infoLog
        )

    # fragment shader
    fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragmentShader, fragmentShaderSource)
    glCompileShader(fragmentShader)

    # verificar erros de compilação de shader
    success = glGetShaderiv(fragmentShader, GL_COMPILE_STATUS)
    if (success == 0):
        infoLog = glGetShaderInfoLog(fragmentShader)
        print(
            "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED" + "\n" +
            infoLog
        )

    # link shaders
    shaderProgram = glCreateProgram()
    glAttachShader(shaderProgram, vertexShader)
    glAttachShader(shaderProgram, fragmentShader)
    glLinkProgram(shaderProgram)

    # verificar erros de vinculação
    success = glGetProgramiv(shaderProgram, GL_LINK_STATUS)
    if (success == 0):
        infoLog = glGetProgramInfoLog(shaderProgram)
        print(
            "ERROR::SHADER::PROGRAM::LINKING_FAILED" + "\n" +
            infoLog
        )

    glDeleteShader(vertexShader)
    glDeleteShader(fragmentShader)

    # configura dados de vértice (e buffer(s)) e configura atributos de vértice
    # --------------------------------------------------
    vertices = np.array([
        -0.5, -0.5,  0.0, # inferior esquerdo
         0.5, -0.5,  0.0, # inferior direito
         0.5,  0.5,  0.0, # superior direito
        -0.5,  0.5,  0.0  # superior esquerdo
    ], dtype=np.float32)

    indices = np.array([ # observe que começamos do 0!
        0, 1, 2, # primeiro triângulo
        0, 2, 3  # segundo triângulo
    ], dtype=np.uint32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    # primeiro vincule o Vertex Array Object, depois vincule e configure o(s) buffer(s) de vértices e, em seguida, configure o(s) atributo(s) de vértice.
    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # observe que isso é permitido; a chamada para glVertexAttribPointer registrou o VBO como o objeto de buffer de vértices vinculado ao atributo de vértice, portanto, podemos desvinculá-lo com segurança logo em seguida
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # lembre-se: NÃO desvincule o EBO enquanto um VAO estiver ativo, pois o objeto de buffer de elementos vinculado ESTÁ armazenado no VAO; mantenha o EBO vinculado.
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    # Você pode desvincular o VAO posteriormente para que outras chamadas de VAO não modifiquem acidentalmente este VAO, mas isso raramente acontece. Modificar outros
    # VAOs exige uma chamada para glBindVertexArray de qualquer forma, então geralmente não desvinculamos VAOs (nem VBOs) quando não é diretamente necessário.
    glBindVertexArray(0)

    # descomente esta chamada para desenhar polígonos em wireframe.
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

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

        # desenhar nosso primeiro triângulo
        glUseProgram(shaderProgram) # como temos apenas um único VAO, não há necessidade de vinculá-lo todas as vezes, mas faremos isso para manter as coisas um pouco mais organizadas
        glBindVertexArray(VAO)
        # glDrawArrays(GL_TRIANGLES, 0, 3)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, c_void_p(0))
        # glUseProgram(0) # não é necessário desvinculá-lo toda vez

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(1, VAO)
    glDeleteBuffers(1, VBO)
    glDeleteBuffers(1, EBO)
    glDeleteProgram(shaderProgram)

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
