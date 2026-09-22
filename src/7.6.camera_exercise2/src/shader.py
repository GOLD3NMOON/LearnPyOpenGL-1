import glm

import numpy as np

from OpenGL.GL import *

class Shader:
    # o construtor gera o shader em tempo de execução
    # --------------------------------------------------
    def __init__(self, vertexPath, fragmentPath):
        # 1. recuperar o código-fonte do vértice/fragmento a partir de filePath
        try:
            with open(vertexPath, "r", encoding="utf8") as f:
                vertexCode = f.read()
            with open(fragmentPath, "r", encoding="utf8") as f:
                fragmentCode = f.read()
        except OSError as e:
            print("ERROR::SHADER::FILE_NOT_SUCCESSFULLY_READ: " + e)

        vShaderCode = vertexCode
        fShaderCode = fragmentCode

        # 2. compilar shaders

        # vertex shader
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, vShaderCode)
        glCompileShader(vertex)
        self.checkCompileErrors(vertex, "VERTEX")

        # fragment Shader
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, fShaderCode)
        glCompileShader(fragment)
        self.checkCompileErrors(fragment, "FRAGMENT")

        # shader Program
        self.ID = glCreateProgram()
        glAttachShader(self.ID, vertex)
        glAttachShader(self.ID, fragment)
        glLinkProgram(self.ID)
        self.checkCompileErrors(self.ID, "PROGRAM")

        # exclua os shaders, pois eles já estão vinculados ao nosso programa e não são mais necessários
        glDeleteShader(vertex)
        glDeleteShader(fragment)

    # ativa o shader
    # --------------------------------------------------
    def use(self):
        glUseProgram(self.ID)

    # funções utilitárias de uniformes
    # --------------------------------------------------
    def setBool(self, name, value):
        location = glGetUniformLocation(self.ID, name)
        glUniform1i(location, value)
    # --------------------------------------------------
    def setInt(self, name, value):
        location = glGetUniformLocation(self.ID, name)
        glUniform1i(location, value)
    # --------------------------------------------------
    def setFloat(self, name, value):
        location = glGetUniformLocation(self.ID, name)
        glUniform1f(location, value)
    # --------------------------------------------------
    def setVec2(self, name, *args):
        location = glGetUniformLocation(self.ID, name)

        if len(args) == 1:
            v = args[0]
            glUniform2fv(location, 1, np.array([v[0], v[1]], dtype=np.float32))
        else:
            glUniform2f(location, args[0], args[1])
    # --------------------------------------------------
    def setVec3(self, name, *args):
        location = glGetUniformLocation(self.ID, name)

        if len(args) == 1:
            v = args[0]
            glUniform3fv(location, 1, np.array([v[0], v[1], v[2]], dtype=np.float32))
        else:
            glUniform3f(location, args[0], args[1], args[2])
    # --------------------------------------------------
    def setVec4(self, name, *args):
        location = glGetUniformLocation(self.ID, name)

        if len(args) == 1:
            v = args[0]
            glUniform4fv(location, 1, np.array([v[0], v[1], v[2], v[3]], dtype=np.float32))
        else:
            glUniform4f(location, args[0], args[1], args[2], args[3])
    # --------------------------------------------------
    def setMat2(self, name, mat):
        location = glGetUniformLocation(self.ID, name)
        glUniformMatrix2fv(location, 1, GL_FALSE, glm.value_ptr(mat))
    # --------------------------------------------------
    def setMat3(self, name, mat):
        location = glGetUniformLocation(self.ID, name)
        glUniformMatrix3fv(location, 1, GL_FALSE, glm.value_ptr(mat))
    # --------------------------------------------------
    def setMat4(self, name, mat):
        location = glGetUniformLocation(self.ID, name)
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(mat))

    # função utilitária para verificar erros de compilação/vinculação de shaders.
    # --------------------------------------------------
    def checkCompileErrors(self, shader, type):
        if (type != "PROGRAM"):
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if (success == 0):
                infoLog = glGetShaderInfoLog(shader)
                print(
                    "ERROR::SHADER_COMPILATION_ERROR of type: " + type + "\n" +
                    infoLog + "\n" +
                    " -- -------------------------------------------------- -- "
                )
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if (success == 0):
                infoLog = glGetProgramInfoLog(shader)
                print(
                    "ERROR::PROGRAM_LINKING_ERROR of type: " + type + "\n" +
                    infoLog + "\n" +
                    " -- -------------------------------------------------- -- "
                )
