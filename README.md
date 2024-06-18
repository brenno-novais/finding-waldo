# finding-waldo
EP de processamento para disciplina de Computação Gráfica. O objetivo é encontrar o Waldo em imagens Where's Waldo utilizando apenas técnicas de processamento.

# Montagem do Setup

1. Instalar o [Python (3.10.0)](https://www.python.org/downloads/release/python-3100/)
2. Clonar este repositório
3. Criar um virtual environment
   Digite, no prompt de comando, na pasta onde você clonou o repositório: <code>pipenv install</code>
4. Instale o Jupyter Labe digitando no prompt:  <code>pip install jupyterlab</code>
5. Após isso, ative o venv, digitando: <code>pipenv shell</code>
   Necessário toda vez que for usar o setup
6. Digite no prompt <code>jupyter-lab</code> para iniciar

# Lógica do processamento

- Aumentar o tamanho da imagem para melhor detectar os elementos dela;
- Transformar em escala de cinza;
- Aplicar blur para suavizar imagem;
- Aplicar Transformada de Hough para círculos na tentativa de encontrar os óculos do Waldo;
- Filtrar círculos que formam pares e estão alinhados horizontalmente;
- Criar versão preto e branco da imagem;
- Verificar que acima do par de círculos há pixels pretos na imagem preto e branco (seria a testa do Waldo);
- Verificar que acima da suposta testa há pixels brancos na imagem preto e branco (seria o cabelo do Waldo);
- Par de círculos que tiver a maior proporção de pixels pretos e brancos na área definida é o Waldo.
- Torna a imagem mais escura ao redor de tudo que não identificamos como o Waldo.
