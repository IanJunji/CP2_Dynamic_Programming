import math
from datetime import datetime, timedelta
import folium
import webbrowser
import os

# --- Constantes do Desafio ---
VELOCIDADE_TREM_KMH = 35.0
PENALIDADE_TROCA_LINHA_MIN = 3.0


class RoteadorMetroLondres:
    """
    Classe principal que modela a rede de metrô, calcula e visualiza rotas.
    Aplica Programação Dinâmica com recursão e memoization para encontrar
    o caminho ótimo (mais curto ou mais longo) entre duas estações.
    """

    def __init__(self, stations_data, edges_data):
        self.stations = stations_data
        self.graph = self._build_graph(edges_data)
        self.memo = {}  # Cache para a memoization

    def _get_coords(self, estacao):
        # Retorna (lat, lon) para uma estação, aceitando value como dict ou lista.
        val = self.stations[estacao]
        return val[0], val[1]

    def _build_graph(self, data):
        """
        Constrói o grafo (lista de adjacência) a partir dos dados de arestas.

        Suporta dois formatos:
        - string multilinha com linhas no formato 'origem - destino - linha'
        - dict {nome_linha: [(origem,destino), ...], ...}
        """
        graph = {name: [] for name in self.stations}

        if isinstance(data, dict):
            for nome_linha, conexoes in data.items():
                for par in conexoes:
                    if not par or len(par) < 2:
                        continue
                    origem, destino = par[0].strip(), par[1].strip()
                    if origem not in graph or destino not in graph:
                        continue
                    graph[origem].append({"vizinho": destino, "linha": nome_linha})
                    graph[destino].append({"vizinho": origem, "linha": nome_linha})
        else:
            for line in data.strip().split("\n"):
                origem, destino, nome_linha = [
                    item.strip() for item in line.split(" - ")
                ]
                # Adiciona a conexão nos dois sentidos (grafo não-direcionado)
                graph[origem].append({"vizinho": destino, "linha": nome_linha})
                graph[destino].append({"vizinho": origem, "linha": nome_linha})

        return graph

    def _haversine(self, estacao1, estacao2):
        """Calcula a distância em km entre duas estações usando a fórmula de Haversine."""
        R = 6371  # Raio da Terra em km
        lat1, lon1 = self._get_coords(estacao1)
        lat2, lon2 = self._get_coords(estacao2)

        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _get_tempo_deslocamento(self, estacao1, estacao2):
        """Calcula o tempo de viagem em minutos entre duas estações."""
        distancia_km = self._haversine(estacao1, estacao2)
        return (distancia_km / VELOCIDADE_TREM_KMH) * 60

    def _get_tempo_espera(self, hora_atual):
        """Calcula o tempo de espera na estação com base na hora do dia."""
        if hora_atual.hour < 11:
            return 1.5
        elif hora_atual.hour >= 18:
            return 2.0
        else:
            return 1.0

    def _encontrar_caminhos_recursivo(
        self, atual, destino, visitados, hora_atual, linha_anterior
    ):
        """
        Função recursiva principal que explora todos os caminhos simples (sem ciclos).
        Esta é a implementação da Programação Dinâmica com Memoization.
        """
        # 1. CONDIÇÃO DE PARADA (CASO BASE)
        if atual == destino:
            return [{"caminho": [destino], "tempo": 0, "linhas": [], "trocas": 0}]

        # 2. MEMOIZATION: Verifica se já calculamos este subproblema
        # A chave do cache contém o estado essencial: (estação atual, nós já visitados)
        estado = (atual, frozenset(visitados))
        if estado in self.memo:
            return self.memo[estado]

        # 3. PASSO RECURSIVO
        caminhos_encontrados = []
        novos_visitados = visitados | {atual}

        for conexao in self.graph[atual]:
            vizinho = conexao["vizinho"]
            linha_atual = conexao["linha"]

            if vizinho not in visitados:
                # Calcula os custos para este trecho
                tempo_espera = self._get_tempo_espera(hora_atual)
                tempo_deslocamento = self._get_tempo_deslocamento(atual, vizinho)

                troca_de_linha = (
                    linha_anterior is not None and linha_anterior != linha_atual
                )
                penalidade = PENALIDADE_TROCA_LINHA_MIN if troca_de_linha else 0

                tempo_trecho = tempo_espera + tempo_deslocamento + penalidade

                # Chama a recursão para o próximo estado
                proxima_hora = hora_atual + timedelta(minutes=tempo_trecho)
                sub_caminhos = self._encontrar_caminhos_recursivo(
                    vizinho, destino, novos_visitados, proxima_hora, linha_atual
                )

                # Constrói o caminho completo a partir dos resultados dos subproblemas
                for sub_caminho in sub_caminhos:
                    caminho_completo = {
                        "caminho": [atual] + sub_caminho["caminho"],
                        "tempo": tempo_trecho + sub_caminho["tempo"],
                        "linhas": [linha_atual] + sub_caminho["linhas"],
                        "trocas": (1 if troca_de_linha else 0) + sub_caminho["trocas"],
                    }
                    caminhos_encontrados.append(caminho_completo)

        # 4. ARMAZENA NO CACHE E RETORNA
        self.memo[estado] = caminhos_encontrados
        return caminhos_encontrados

    def _visualizar_caminho(self, resultado):
        """Cria um mapa interativo com o trajeto usando a biblioteca Folium."""
        caminho = resultado["caminho"]
        linhas = resultado["linhas"]

        # Cores para as linhas do metrô (pode adicionar mais)
        cores_linhas = {
            "Victoria": "lightblue",
            "Northern": "black",
            "Bakerloo": "brown",
            "Jubilee": "gray",
            "Circle": "yellow",
        }

        # Centraliza o mapa na estação de partida
        lat_inicial, lon_inicial = self._get_coords(caminho[0])
        mapa = folium.Map(location=[lat_inicial, lon_inicial], zoom_start=14)

        # Adiciona marcadores para cada estação no caminho
        for i, nome_estacao in enumerate(caminho):
            lat, lon = self._get_coords(nome_estacao)
            coords = [lat, lon]
            cor_marcador = (
                "green" if i == 0 else "red" if i == len(caminho) - 1 else "blue"
            )
            icone = "play" if i == 0 else "stop" if i == len(caminho) - 1 else "info"

            folium.Marker(
                location=coords,
                popup=f"<b>{nome_estacao}</b>",
                icon=folium.Icon(color=cor_marcador, icon=icone, prefix="fa"),
            ).add_to(mapa)

        # Desenha as linhas do trajeto
        for i in range(len(caminho) - 1):
            ponto_a = list(self._get_coords(caminho[i]))
            ponto_b = list(self._get_coords(caminho[i + 1]))
            cor = cores_linhas.get(linhas[i], "purple")  # Roxo como cor padrão

            folium.PolyLine(
                locations=[ponto_a, ponto_b],
                color=cor,
                weight=5,
                opacity=0.8,
                tooltip=f"Linha: {linhas[i]}",
            ).add_to(mapa)

        # Salva e abre o mapa
        filepath = os.path.abspath("trajeto_metro_londes.html")
        mapa.save(filepath)
        print(f"\n  Mapa gerado e salvo em: {filepath}")
        webbrowser.open(f"file://{filepath}")

    def encontrar_caminho(self, origem, destino, hora_inicio_str, modo="menor"):
        """
        Função principal que orquestra a busca pelo caminho.
        É a interface pública para o usuário.
        """
        print("-" * 50)
        print(f"Buscando rota de '{origem}' para '{destino}'")
        print(f"Hora de início: {hora_inicio_str} | Modo: {modo}")
        print("-" * 50)

        # Validações de entrada
        if origem not in self.stations or destino not in self.stations:
            print("Erro: Uma ou ambas as estações não existem nos dados fornecidos.")
            return

        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M")

        todos_caminhos = self._encontrar_caminhos_recursivo(
            origem, destino, set(), hora_inicio, None
        )

        if not todos_caminhos:
            print("Nenhum caminho encontrado entre as estações.")
            return

        # Seleciona o caminho com base no modo ('menor', 'medio' ou 'maior')
        if modo == "menor":
            resultado_final = min(todos_caminhos, key=lambda x: x["tempo"])
        elif modo == "maior":
            resultado_final = max(todos_caminhos, key=lambda x: x["tempo"])
        elif modo == "medio":
            # Caminho mediano: ordena todos os caminhos por tempo e pega o do meio.
            # Se houver um número par de caminhos, escolhemos o elemento (n-1)//2
            # (mediana inferior) para retornar um caminho existente.
            caminhos_ordenados = sorted(todos_caminhos, key=lambda x: x["tempo"])
            idx = (len(caminhos_ordenados) - 1) // 2
            resultado_final = caminhos_ordenados[idx]
        else:
            print(f" Modo '{modo}' inválido. Use 'menor', 'medio' ou 'maior'.")
            return

        # Apresenta o resultado
        print("Rota encontrada com sucesso!\n")
        print(f"Tempo total: {resultado_final['tempo']:.2f} minutos")
        print(f"Caminho: {' → '.join(resultado_final['caminho'])}")
        print(f"Linhas: {' → '.join(resultado_final['linhas'])}")
        print(f"Trocas de linha: {resultado_final['trocas']}")

        # Gera o mapa
        self._visualizar_caminho(resultado_final)


# --- DADOS FORNECIDOS ---


stations_coordinates_data = {
    "King's Cross": [51.5308, -0.1238],
    "Oxford Circus": [51.5154, -0.1410],
    "Green Park": [51.5067, -0.1428],
    "Victoria Station": [51.4965, -0.1447],
    "Euston": [51.5281, -0.1337],
    "Baker Street": [51.5231, -0.1569],
    "Paddington": [51.5150, -0.1750],
    "Bond Street": [51.5145, -0.1494],
}

metro_dict = {
    "Victoria": [
        ("King's Cross", "Oxford Circus"),
        ("Oxford Circus", "Green Park"),
        ("Green Park", "Victoria Station"),
    ],
    "Northern": [("King's Cross", "Euston"), ("Euston", "Victoria Station")],
    "Bakerloo": [("Baker Street", "Oxford Circus"), ("Paddington", "Baker Street")],
    "Jubilee": [("Bond Street", "Green Park"), ("Oxford Circus", "Bond Street")],
    "Circle": [("Bond Street", "Paddington")],
}


# --- EXECUÇÃO DO DESAFIO ---
if __name__ == "__main__":

    # 1. Instancia o roteador com os dados
    roteador = RoteadorMetroLondres(stations_coordinates_data, metro_dict)

    # 2. Executa a busca pelo caminho mais RÁPIDO
    # Exemplo 1: Trajeto simples na mesma linha
    roteador.encontrar_caminho(
        origem="King's Cross",
        destino="Victoria Station",
        hora_inicio_str="10:00",
        modo="menor",
    )

    # 2.1 Exemplo: caminho mediano em tempo total
    roteador.encontrar_caminho(
        origem="King's Cross",
        destino="Victoria Station",
        hora_inicio_str="12:00",
        modo="medio",
    )

    # 3. Executa a busca pelo caminho mais LONGO (turístico)
    # Exemplo 2: Trajeto que força mais trocas e distância
    roteador.encontrar_caminho(
        origem="Paddington", destino="Euston", hora_inicio_str="14:00", modo="maior"
    )
