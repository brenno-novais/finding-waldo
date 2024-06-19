import argparse

import cv2
import matplotlib.pyplot as plt
import numpy as np


# Função para exibir a imagem
def exibe_imagem(imagem):
    plt.imshow(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

# Função para encontrar o quadrado que contenha os dois círculos
def encontrar_quadrado(circulo1, circulo2):
    x_min = min(abs(circulo1[0] - circulo1[2]), abs(circulo2[0] - circulo2[2]))
    x_max = max(abs(circulo1[0] + circulo1[2]), abs(circulo2[0] + circulo2[2]))
    y_min = min(abs(circulo1[1] - circulo1[2]), abs(circulo2[1] - circulo2[2]))
    y_max = max(abs(circulo1[1] + circulo1[2]), abs(circulo2[1] + circulo2[2]))
    return (x_min, y_min, x_max, y_max)

# Função para contar a proporção de pixels brancos dentro de um quadrado em uma imagem preto e branco
def contar_proporcao_pixels_brancos(imagem_bw, x_min, y_min, x_max, y_max):
    roi = imagem_bw[y_min:y_max, x_min:x_max]
    pixels_brancos = cv2.countNonZero(roi)
    total_pixels = roi.size
    proporcao_brancos = (
        pixels_brancos / total_pixels) if total_pixels > 0 else 0
    return proporcao_brancos

# Função para calcular a distância euclidiana entre dois centros de círculos
def calcular_distancia(centro1, centro2):
    centro1 = np.array(centro1, dtype=np.float64)
    centro2 = np.array(centro2, dtype=np.float64)
    return np.linalg.norm(centro1 - centro2)

# Função para detectar Waldo em uma imagem
def encontrar_waldo(imagem):

    # Aumenta a dimensão da imagem
    escala = 8
    imagem_grande = cv2.resize(
        imagem, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    print('Imagem original com dimensão aumentada')
    exibe_imagem(imagem_grande)

    # Converter para escala de cinza
    imagem_cinza = cv2.cvtColor(imagem_grande, cv2.COLOR_BGR2GRAY)
    print('Imagem em escala de cinza')
    cv2.imwrite(
        'resultados/processamentos_realizados/imagem_cinza.jpg', imagem_cinza)
    exibe_imagem(imagem_cinza)

    # Aplicar suavização GaussianBlur
    imagem_suavizada = cv2.GaussianBlur(imagem_cinza, (9, 9), 2)
    print('Imagem em escala de cinza suavizada')
    cv2.imwrite(
        'resultados/processamentos_realizados/imagem_suavizada.jpg', imagem_suavizada)
    exibe_imagem(imagem_suavizada)

    # Converter para preto e branco
    kernel = np.ones((5, 5), np.uint8)
    imagem_preto_e_branco = cv2.threshold(
        imagem_cinza, 45, 255, cv2.THRESH_BINARY_INV)[1]
    imagem_preto_e_branco = cv2.morphologyEx(
        imagem_preto_e_branco, cv2.MORPH_CLOSE, kernel)
    print('Imagem que manteve somente pixels pretos')
    cv2.imwrite(
        'resultados/processamentos_realizados/imagem_preto_e_branco.jpg', imagem_preto_e_branco)
    exibe_imagem(imagem_preto_e_branco)

    # Detectr bordas usando Canny
    # Propósito é simular como a transformada de Hough verá as bordas do objeto. Só possui utilidade para debug.
    imagem_bordas = cv2.Canny(imagem_preto_e_branco, 100, 200)
    print('Imagem com bordas do objeto')
    cv2.imwrite(
        'resultados/processamentos_realizados/imagem_bordas.jpg', imagem_bordas)
    exibe_imagem(imagem_bordas)

    # Utilizar a transformada de Hough para encontrar círculos
    print('Encontrando círculos na imagem...')
    circulos = cv2.HoughCircles(imagem_suavizada, cv2.HOUGH_GRADIENT, dp=1.3, minDist=5,
                                param1=200, param2=20, minRadius=15, maxRadius=25)
    print('Círculos encontrados.')

    # Filtragem dos círculos detectados
    if circulos is not None:
        circulos = np.uint16(np.around(circulos))
        pares_de_oculos = []
        melhor_par = None
        max_pixels_brancos = 0
        melhor_quadrado = None

        # Encontrar pares de círculos próximos, com o intuito de achar as lentes dos óculos de Waldo
        print('Filtrando círculos com potencial para serem as lentes do óculos de Waldo...')
        for i in range(len(circulos[0])):
            for j in range(i + 1, len(circulos[0])):
                centro1 = (circulos[0][i][0], circulos[0][i][1])
                centro2 = (circulos[0][j][0], circulos[0][j][1])

                dist = calcular_distancia(centro1, centro2)

                # Limite para considerar círculos alinhados horizontalmente (ajustar conforme necessário)
                limite_alinhamento_horizontal = 10

                # Distância mínima e máxima entre as lentes dos óculos e verificação de alinhamento horizontal
                if 30 < dist < 60 and abs(centro2[1] - centro1[1]) <= limite_alinhamento_horizontal:
                    pares_de_oculos.append((circulos[0][i], circulos[0][j]))

        print('Círculos com potencial para serem as lentes encontrados.')

        # Verificar cada par de círculos
        print('Verificando qual par de círculos melhor representa os óculos de Waldo...')
        for par in pares_de_oculos:
            # Encontrar o quadrado que contenha ambos os círculos
            x_min, y_min, x_max, y_max = encontrar_quadrado(par[0], par[1])

            # Conta pixels brancos na região de interesse (quadrado)
            # A região de interesse é acima da lente dos óculos, objetivo é achar o cabelo do Waldo, que mantem uma grande concentração de pixels brancos na imagem preto e branco.
            total_pixels_brancos = contar_proporcao_pixels_brancos(
                imagem_preto_e_branco, x_min + 30, y_min - 70, x_max, y_max - 70)

            # Verifica se este par tem mais pixels brancos
            if total_pixels_brancos > max_pixels_brancos:
                max_pixels_brancos = total_pixels_brancos
                melhor_par = par
                melhor_quadrado = (x_min - 150, y_min - 150,
                                   x_max + 150, y_max + 150)

        # Desenha o melhor par de círculos na imagem original
        print('Waldo potencialmente encontrado.')
        print('Isolando Waldo na imagem...')
        if melhor_par:
            # Desenha o quadrado de destaque
            x_min, y_min, x_max, y_max = melhor_quadrado
            cv2.rectangle(imagem_grande, (x_min, y_min),
                          (x_max, y_max), (0, 255, 0), 20)

            # Cria uma máscara para escurecer a imagem fora do quadrado de destaque
            mask = np.zeros(imagem_grande.shape, dtype=np.uint8)
            mask[y_min:y_max, x_min:x_max] = imagem_grande[y_min:y_max, x_min:x_max]

            # Escurece a imagem
            imagem_escurecida = cv2.addWeighted(
                imagem_grande, 0.3, mask, 0.7, 0)

    try:
        return cv2.resize(imagem_escurecida, None, fx=1/8, fy=1/8, interpolation=cv2.INTER_CUBIC)
    except Exception:
        print('Não foi possível encontrar o Waldo.')
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Encontrar Waldo em uma imagem.')
    parser.add_argument('path_da_imagem', nargs='?',
                        default='wheres-waldo/waldo-7.jpg', help='Caminho da imagem do Waldo')
    args = parser.parse_args()

    # Carrega a imagem de entrada
    imagem = cv2.imread(args.path_da_imagem)

    if imagem is None:
        print(
            f"Não foi possível carregar a imagem no caminho: {args.path_da_imagem}")
        return

    print('Imagem a detectar Waldo')
    exibe_imagem(imagem)

    imagem_com_waldo = encontrar_waldo(imagem)

    # Mostra a imagem com a detecção
    if imagem_com_waldo is not None:
        cv2.imwrite('resultados/waldo_detectado.jpg', imagem_com_waldo)
        print('\n\nImagem com Waldo detectado')
        exibe_imagem(imagem_com_waldo)


if __name__ == "__main__":
    main()
