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

fragmentShader1Source = """
    #version 330 core
    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
    }
"""

fragmentShader2Source = """
    #version 330 core
    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(1.0f, 1.0f, 0.0f, 1.0f);
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

    # desta vez, omitimos as verificações do log de compilação para facilitar a leitura (se você encontrar problemas, adicione as verificações de compilação; consulte os exemplos de código anteriores)
    vertexShader = glCreateShader(GL_VERTEX_SHADER)

    fragmentShaderOrange = glCreateShader(GL_FRAGMENT_SHADER) # o primeiro shader de fragmento que gera a cor laranja
    fragmentShaderYellow = glCreateShader(GL_FRAGMENT_SHADER) # o segundo shader de fragmento que gera a cor amarela

    shaderProgramOrange = glCreateProgram()
    shaderProgramYellow = glCreateProgram() # o segundo programa de shader

    glShaderSource(vertexShader, vertexShaderSource)
    glCompileShader(vertexShader)

    glShaderSource(fragmentShaderOrange, fragmentShader1Source)
    glCompileShader(fragmentShaderOrange)

    glShaderSource(fragmentShaderYellow, fragmentShader2Source)
    glCompileShader(fragmentShaderYellow)

    # vincular o primeiro objeto de programa
    glAttachShader(shaderProgramOrange, vertexShader)
    glAttachShader(shaderProgramOrange, fragmentShaderOrange)
    glLinkProgram(shaderProgramOrange)

    # em seguida, vincule o segundo objeto de programa usando um shader de fragmento diferente (mas o mesmo shader de vértice)
    # isso é perfeitamente permitido, uma vez que as entradas e saídas de ambos os shaders — de vértice e de fragmento — são compatíveis.
    glAttachShader(shaderProgramYellow, vertexShader)
    glAttachShader(shaderProgramYellow, fragmentShaderYellow)
    glLinkProgram(shaderProgramYellow)

    # configura dados de vértice (e buffer(s)) e configura atributos de vértice
    # --------------------------------------------------
    firstTriangle = np.array([
        -0.9,  -0.5,   0.0,
         0.0,  -0.5,   0.0,
        -0.45,  0.5,   0.0
    ], dtype=np.float32)

    secondTriangle = np.array([
         0.0,  -0.5,   0.0,
         0.9,  -0.5,   0.0,
         0.45,  0.5,   0.0
    ], dtype=np.float32)

    VAOs = glGenVertexArrays(2) # também podemos gerar múltiplos VAOs ou buffers ao mesmo tempo
    VBOs = glGenBuffers(2)

    # configuração do primeiro triângulo
    # --------------------------------------------------
    glBindVertexArray(VAOs[0])

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[0])
    glBufferData(GL_ARRAY_BUFFER, firstTriangle.nbytes, firstTriangle, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(c_float), c_void_p(0)) # Os atributos de vértice permanecem os mesmos
    glEnableVertexAttribArray(0)
    
    # glBindVertexArray(0) # não é necessário desfazer a vinculação, pois vinculamos diretamente um VAO diferente nas próximas linhas

    # configuração do segundo triângulo
    # --------------------------------------------------
    glBindVertexArray(VAOs[1]) # observe que agora vinculamos a um VAO diferente

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[1]) # e um VBO diferente
    glBufferData(GL_ARRAY_BUFFER, secondTriangle.nbytes, secondTriangle, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(c_float), c_void_p(0)) # como os dados dos vértices estão compactados, também podemos especificar 0 como o stride do atributo de vértice para deixar o OpenGL determiná-lo
    glEnableVertexAttribArray(0)
    
    # glBindVertexArray(0) # também não é estritamente necessário, mas cuidado com chamadas que possam afetar VAOs enquanto este estiver vinculado (como vincular *element buffer objects* ou habilitar/desabilitar atributos de vértice)

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

        # agora, ao desenhar o triângulo, usamos primeiro o shader de vértice e o shader de fragmento laranja do primeiro programa
        glUseProgram(shaderProgramOrange)

        # desenha o primeiro triângulo usando os dados do primeiro VAO
        glBindVertexArray(VAOs[0])
        glDrawArrays(GL_TRIANGLES, 0, 3) # esta chamada deve gerar um triângulo laranja

        # então, desenhamos o segundo triângulo usando os dados do segundo VAO
        # ao desenhar o segundo triângulo, queremos usar um programa de shader diferente; por isso, alternamos para o programa de shader que utiliza nosso shader de fragmento amarelo.
        glUseProgram(shaderProgramYellow)
        glBindVertexArray(VAOs[1])
        glDrawArrays(GL_TRIANGLES, 0, 3) # esta chamada deve gerar um triângulo amarelo

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(2, VAOs)
    glDeleteBuffers(2, VBOs)
    glDeleteProgram(shaderProgramOrange)
    glDeleteProgram(shaderProgramYellow)

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
