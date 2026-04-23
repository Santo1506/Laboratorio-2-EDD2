
# Laboratorio de Estructuras de Datos - Grafos
# Funciones básicas para análisis de grafos

import csv
import math
import heapq

# Función para leer el CSV y construir el grafo
def construir_grafo_desde_csv(ruta_csv):
    grafo = {}
    info_aeropuertos = {}  # Guardar información de aeropuertos completa
    aeropuertos = {}  # Guardar coordenadas para calcular distancias
    
    with open(ruta_csv, 'r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        
        for fila in lector:
            origen = fila['Source Airport Code']
            nombre = fila['Source Airport Name']
            ciudad = fila['Source Airport City']
            pais = fila['Source Airport Country']
            destino = fila['Destination Airport Code']
            lat_origen = float(fila['Source Airport Latitude'])
            lon_origen = float(fila['Source Airport Longitude'])
            lat_destino = float(fila['Destination Airport Latitude'])
            lon_destino = float(fila['Destination Airport Longitude'])
            
            # Calcular distancia (peso de la arista)
            distancia = calcular_distancia(lat_origen, lon_origen, lat_destino, lon_destino)
            
            # Agregar al grafo (no dirigido)
            if origen not in grafo:
                grafo[origen] = []
                info_aeropuertos[origen] = {
                    'latitude': lat_origen,
                    'longitude': lon_origen,
                    'name': nombre,
                    'city': ciudad,
                    'country': pais
                }
            if destino not in grafo:
                grafo[destino] = []
                info_aeropuertos[destino] = {
                    'latitude': lat_destino,
                    'longitude': lon_destino,
                    'name': fila['Destination Airport Name'],
                    'city': fila['Destination Airport City'],
                    'country': fila['Destination Airport Country']
                }

            # Revisar si ya existe la arista para no duplicar
            existe_origen_a_destino = any(v == destino for v, p in grafo[origen])
            existe_destino_a_origen = any(v == origen for v, p in grafo[destino])
            
            if not existe_origen_a_destino:
                grafo[origen].append((destino, distancia))
            if not existe_destino_a_origen:
                grafo[destino].append((origen, distancia))
    
    return grafo, info_aeropuertos


# Calcular distancia entre dos puntos geográficos usando la fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    # Radio de la Tierra (R)
    R = 6371.0
    
    # Convertir todo a radianes
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    #calculo de a
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    
    # calculo de c
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    #ditancia final
    return R * c


# Función para verificar si el grafo es conexo usando BFS
def es_conexo(grafo):
    if not grafo:
        return True, 0, []
    
    # Encontrar todas las componentes conexas
    visitados = set()
    componentes = []
    
    for nodo in grafo:
        if nodo not in visitados:
            componente = bfs_componente(grafo, nodo, visitados)
            componentes.append(componente)
    
    # Si hay solo una componente, es conexo
    if len(componentes) == 1:
        return True, 1, [len(componentes[0])]
    else:
        tamaños = [len(c) for c in componentes]
        return False, len(componentes), tamaños


# Función BFS para encontrar una componente
def bfs_componente(grafo, inicio, visitados):
    cola = [inicio]
    visitados.add(inicio)
    componente = [inicio]
    
    while cola:
        nodo = cola.pop(0)
        
        # Recorrer vecinos
        for vecino, peso in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)
                componente.append(vecino)
    
    return componente


# Función para determinar si el grafo es bipartito
def es_bipartito(grafo):
    if not grafo:
        return True
    
    # Encontrar la componente más grande
    visitados = set()
    componentes = []
    
    for nodo in grafo:
        if nodo not in visitados:
            componente = bfs_componente(grafo, nodo, visitados)
            componentes.append(componente)
    
    # Obtener la componente más grande
    componente_grande = max(componentes, key=len)
    
    # Intentar colorear con 2 colores usando BFS
    colores = {}
    cola = [componente_grande[0]]
    colores[componente_grande[0]] = 0
    
    while cola:
        nodo = cola.pop(0)
        color_actual = colores[nodo]
        color_siguiente = 1 - color_actual
        
        # Recorrer vecinos
        for vecino, peso in grafo[nodo]:
            if vecino not in colores:
                colores[vecino] = color_siguiente
                cola.append(vecino)
            elif colores[vecino] != color_siguiente:
                return False
    
    return True


# Función para calcular el peso del AEM () usando Prim
def calcular_aem(grafo):
    if not grafo:
        return 0
    
    # Encontrar todas las componentes conexas
    visitados_global = set()
    pesos_componentes = []
    
    for nodo_inicio in grafo:
        if nodo_inicio not in visitados_global:
            # Calcular AEM de esta componente usando Prim
            peso_componente = prim_aem(grafo, nodo_inicio, visitados_global)
            pesos_componentes.append(peso_componente)
    
    return pesos_componentes


# Función auxiliar Prim para calcular AEM de una componente
def prim_aem(grafo, inicio, visitados_global):
    visitados = set()
    visitados.add(inicio)
    visitados_global.add(inicio)
    
    # Encontrar todos los nodos en esta componente
    temp_visitados = set()
    componente_nodos = bfs_componente(grafo, inicio, temp_visitados)
    tamaño_componente = len(componente_nodos)
    
    # Lista de aristas: (peso, nodo_origen, nodo_destino)
    aristas = []
    
    # Agregar todas las aristas del nodo inicial
    for vecino, peso in grafo[inicio]:
        aristas.append((peso, inicio, vecino))
    
    peso_mst = 0
    
    # Procesar aristas hasta conectar todos los nodos de la componente
    while aristas and len(visitados) < tamaño_componente:
        # Ordenar aristas por peso y tomar la mínima
        aristas.sort()
        peso, origen, destino = aristas.pop(0)
        
        if destino not in visitados:
            visitados.add(destino)
            visitados_global.add(destino)
            peso_mst += peso
            
            # Agregar nuevas aristas del nodo recién agregado
            for nuevo_vecino, nuevo_peso in grafo[destino]:
                if nuevo_vecino not in visitados:
                    aristas.append((nuevo_peso, destino, nuevo_vecino))
    
    return peso_mst

def dijkstra(grafo, inicio):
    # Inicializamos distancias en infinito y predecesores en None
    distancias = {nodo: float('inf') for nodo in grafo}
    predecesores = {nodo: None for nodo in grafo}
    distancias[inicio] = 0
    
    # Cola de prioridad: (distancia, nodo)
    cola = [(0, inicio)]
    
    while cola:
        distancia_actual, nodo_actual = heapq.heappop(cola)
        
        if distancia_actual > distancias[nodo_actual]:
            continue
            
        for vecino, peso in grafo[nodo_actual]:
            distancia = distancia_actual + peso
            if distancia < distancias[vecino]:
                distancias[vecino] = distancia
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola, (distancia, vecino))
                
    return distancias, predecesores

def reconstruir_camino(predecesores, destino):
    camino = []
    nodo = destino
    
    while nodo is not None:
        camino.append(nodo)
        nodo = predecesores[nodo]
    
    camino.reverse()
    return camino

def Diez_aeropuertos_mas_lejanos(grafo, distancias, info_aeropuertos):
    # 1. Filtramos los inalcanzables y el origen
    alcanzables = []
    for cod, dist in distancias.items():
        if dist != float('inf') and dist > 0:
            alcanzables.append((cod, dist))

    # 2. Ordenamos por distancia (la posición [1] de la tupla) de mayor a menor
    # Usamos reverse=True para que los más largos salgan primero
    lejanos = sorted(alcanzables, key=lambda x: x[1], reverse=True)[:10]

    return lejanos

# Menú principal
def menu_principal():
    # Cargar grafo desde CSV
    ruta_csv = "flights_final.csv"
    print("Cargando datos del CSV...")
    grafo, info_aeropuertos = construir_grafo_desde_csv(ruta_csv)
    print(f"✓ Grafo cargado: {len(grafo)} aeropuertos\n")
    
    print("=" * 40)
    print("  Laboratorio de Grafos")
    print("=" * 40)
    
    while True:
        print("\nOpciones:")
        print("1. Ver si el grafo es conexo")
        print("2. Ver si el grafo es bipartito")
        print("3. Calcular peso del MST")
        print("4. Calcular distancias maximas desde un aeropuerto (Dijkstra)")
        print("0. Salir")
        
        opcion = input("\nElige una opción: ").strip()
        
        if opcion == "1":
            es_con, num_comp, tamaños = es_conexo(grafo)
            if es_con:
                print("\n✓ El grafo ES conexo")
            else:
                print(f"\n✗ El grafo NO es conexo")
                print(f"  Componentes: {num_comp}")
                print(f"  Tamaños: {tamaños}")
        
        elif opcion == "2":
            resultado = es_bipartito(grafo)
            if resultado:
                print("\n✓ El grafo ES bipartito")
            else:
                print("\n✗ El grafo NO es bipartito")
        
        elif opcion == "3":
            pesos_componentes = calcular_aem(grafo)
            print(f"\nPesos de las componentes del AEM: {pesos_componentes}")

        elif opcion == "4":
            aeropuerto_inicio = input("\nIngresa el código del aeropuerto de inicio: ").strip()
            if aeropuerto_inicio not in grafo:
                print("✗ Aeropuerto no encontrado en el grafo.")
                continue

            distancias, predecesores = dijkstra(grafo, aeropuerto_inicio)
            lejanos = Diez_aeropuertos_mas_lejanos(grafo, distancias, info_aeropuertos)

            # 3. Mostramos los resultados
            print("\nLos 10 aeropuertos con el camino mínimo más largo:")
            print("-" * 60)
            for i, (cod_dest, dist_total) in enumerate(lejanos, 1):
                info = info_aeropuertos[cod_dest]
                print(f"{i}. {cod_dest} - {info['name']} ({info['city']}, {info['country']})")
                print(f"   Distancia del camino: {dist_total:.2f} km")
            
        
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        
        else:
            print("\nOpción no válida")


# Ejecutar el programa
if __name__ == "__main__":
    menu_principal()
