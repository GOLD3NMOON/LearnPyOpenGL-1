import glfw
import sys
from OpenGL.GL import *

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

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

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
