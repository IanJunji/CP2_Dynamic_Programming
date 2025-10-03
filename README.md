# Roteador do Metrô de Londres com Programação Dinâmica

## Visão Geral

Este projeto é uma implementação de um sistema de roteamento para o metrô de Londres, desenvolvido como parte do Check Point 2 da matéria de Dynamic Programming no curso de Engenharia de Software da FIAP. A aplicação utiliza programação dinâmica, com recursão e memoization, para calcular a rota ótima (mais rápida, mais longa ou de tempo mediano) entre duas estações da rede.

O algoritmo considera diversas variáveis para otimizar o trajeto, como:
* A distância geográfica entre as estações (calculada pela fórmula de Haversine).
* O tempo de deslocamento com base na velocidade média do trem.
* O tempo de espera variável, que muda conforme o horário de pico.
* Penalidades por trocas de linha.

Ao final, o sistema gera um mapa interativo com a rota traçada, utilizando a biblioteca Folium, e o abre automaticamente no navegador.

## Membros do Grupo

* Cilas Pinto Macedo - RM560745
* Ian Junji Maluvayshi Matsushita RM560588
* Pedro Arão Baquini - RM559580

## Bibliotecas Utilizadas e Documentação

O projeto foi construído em Python e utiliza as seguintes bibliotecas:

* **`math`**: Utilizada para realizar os cálculos da fórmula de Haversine, que determina a distância em linha reta entre dois pontos em uma esfera (a Terra).
    * [Documentação Oficial do math](https://docs.python.org/3/library/math.html)
* **`datetime`**: Usada para manipular o tempo, calcular a hora de chegada em cada estação e determinar os tempos de espera com base no horário.
    * [Documentação Oficial do datetime](https://docs.python.org/3/library/datetime.html)
* **`folium`**: Biblioteca principal para a visualização de dados. Ela gera um mapa interativo em HTML, onde a rota, as estações e as linhas são plotadas.
    * [Documentação Oficial do folium](https://python-visualization.github.io/folium/)
* **`webbrowser`**: Módulo que permite abrir o arquivo HTML gerado pelo Folium diretamente no navegador padrão do usuário, facilitando a visualização do resultado.
    * [Documentação Oficial do webbrowser](https://docs.python.org/3/library/webbrowser.html)
* **`os`**: Utilizado para interagir com o sistema operacional, especificamente para obter o caminho absoluto do arquivo do mapa, garantindo que ele possa ser aberto corretamente pelo navegador.
    * [Documentação Oficial do os](https://docs.python.org/3/library/os.html)

