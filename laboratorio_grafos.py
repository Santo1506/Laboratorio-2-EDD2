
# Laboratorio de Estructuras de Datos - Grafos
# Funciones básicas para análisis de grafos

import csv
import math

# Función para leer el CSV y construir el grafo
def construir_grafo_desde_csv(ruta_csv):
    grafo = {}
    aeropuertos = {}  # Guardar coordenadas para calcular distancias
    
    with open(ruta_csv, 'r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        
        for fila in lector:
            origen = fila['Source Airport Code']
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
            if destino not in grafo:
                grafo[destino] = []
            
            # Revisar si ya existe la arista para no duplicar
            existe_origen_a_destino = any(v == destino for v, p in grafo[origen])
            existe_destino_a_origen = any(v == origen for v, p in grafo[destino])
            
            if not existe_origen_a_destino:
                grafo[origen].append((destino, distancia))
            if not existe_destino_a_origen:
                grafo[destino].append((origen, distancia))
    
    return grafo


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


# Función para calcular el peso del MST usando Prim
def calcular_mst(grafo):
    if not grafo:
        return 0
    
    # Encontrar todas las componentes conexas
    visitados_global = set()
    peso_total = 0
    
    for nodo_inicio in grafo:
        if nodo_inicio not in visitados_global:
            # Calcular MST de esta componente usando Prim
            peso_componente = prim_mst(grafo, nodo_inicio, visitados_global)
            peso_total += peso_componente
    
    return peso_total


# Función auxiliar Prim para calcular MST de una componente
def prim_mst(grafo, inicio, visitados_global):
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


# Menú principal
def menu_principal():
    # Cargar grafo desde CSV
    ruta_csv = "../flights_final.csv"
    print("Cargando datos del CSV...")
    grafo = construir_grafo_desde_csv(ruta_csv)
    print(f"✓ Grafo cargado: {len(grafo)} aeropuertos\n")
    
    print("=" * 40)
    print("  Laboratorio de Grafos")
    print("=" * 40)
    
    while True:
        print("\nOpciones:")
        print("1. Ver si el grafo es conexo")
        print("2. Ver si el grafo es bipartito")
        print("3. Calcular peso del MST")
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
            peso = calcular_mst(grafo)
            print(f"\nPeso total del MST: {peso}")
        
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        
        else:
            print("\nOpción no válida")


# Ejecutar el programa
if __name__ == "__main__":
    menu_principal()
