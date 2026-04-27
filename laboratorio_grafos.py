
# Laboratorio de Estructuras de Datos - Grafos
# Funciones básicas para análisis de grafos

import csv
import math
import heapq
import folium
import webbrowser

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
def prim_aem(grafo, inicio, visitados_global):
    visitados = set()
    visitados.add(inicio)
    visitados_global.add(inicio)
    
    temp_visitados = set()
    componente_nodos = bfs_componente(grafo, inicio, temp_visitados)
    tamaño_componente = len(componente_nodos)
    
    # heapq mantiene el orden automáticamente, sin .sort()
    heap = []
    for vecino, peso in grafo[inicio]:
        heapq.heappush(heap, (peso, inicio, vecino))
    
    peso_mst = 0
    aristas_mst = []
    
    while heap and len(visitados) < tamaño_componente:
        peso, origen, destino = heapq.heappop(heap)  # saca el mínimo directo
        
        if destino not in visitados:
            visitados.add(destino)
            visitados_global.add(destino)
            peso_mst += peso
            aristas_mst.append((origen, destino))
            
            for nuevo_vecino, nuevo_peso in grafo[destino]:
                if nuevo_vecino not in visitados:
                    heapq.heappush(heap, (nuevo_peso, destino, nuevo_vecino))
    
    return peso_mst, aristas_mst


def calcular_aem(grafo):
    if not grafo:
        return [], []
    
    visitados_global = set()
    pesos_componentes = []
    aristas_componentes = []
    
    for nodo_inicio in grafo:
        if nodo_inicio not in visitados_global:
            peso, aristas = prim_aem(grafo, nodo_inicio, visitados_global)
            pesos_componentes.append(peso)
            aristas_componentes.append(aristas)
    
    return pesos_componentes, aristas_componentes

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

def dibujar_mapa(ruta, info_aeropuertos):
    
    # 1. Crear el mapa centrado en el origen
    origen = ruta[0]
    lat_org = info_aeropuertos[origen]['latitude']
    lon_org = info_aeropuertos[origen]['longitude']
    
    mapa = folium.Map(location=[lat_org, lon_org], zoom_start=3, tiles="CartoDB positron")
    
    # 2. Lista para guardar las coordenadas de la línea
    puntos_linea = []
    
    # 3. Añadir marcadores para cada escala
    for codigo in ruta:
        info = info_aeropuertos[codigo]
        coords = [info['latitude'], info['longitude']]
        puntos_linea.append(coords)
        
        folium.Marker(
            location=coords,
            popup=f"{info['name']} ({codigo})\n{info['city']}, {info['country']}",
            tooltip=codigo,
            icon=folium.Icon(color='blue', icon='plane')
        ).add_to(mapa)
    
    # 4. Dibujar la línea que une los aeropuertos
    folium.PolyLine(puntos_linea, color="red", weight=3, opacity=0.8).add_to(mapa)
    
    # 5. Guardar y abrir
    nombre_archivo = "ruta_vuelo.html"
    mapa.save(nombre_archivo)
    print(f"\n✓ Mapa generado: {nombre_archivo}")
    webbrowser.open(nombre_archivo)


def dibujar_mst(aristas_componentes, info_aeropuertos):
    """Dibuja todas las aristas del MST en un mapa folium."""
    mapa = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
    
    colores = ["red", "blue", "green", "purple", "orange",
               "darkred", "cadetblue", "darkgreen", "black", "gray"]
    
    for idx, aristas in enumerate(aristas_componentes):
        color = colores[idx % len(colores)]
        
        for origen, destino in aristas:
            if origen in info_aeropuertos and destino in info_aeropuertos:
                lat1 = info_aeropuertos[origen]['latitude']
                lon1 = info_aeropuertos[origen]['longitude']
                lat2 = info_aeropuertos[destino]['latitude']
                lon2 = info_aeropuertos[destino]['longitude']
                
                folium.PolyLine(
                    [[lat1, lon1], [lat2, lon2]],
                    color=color, weight=1, opacity=0.5
                ).add_to(mapa)
    
    # Marcadores pequeños solo para nodos que aparecen en el MST
    nodos_en_mst = set()
    for aristas in aristas_componentes:
        for origen, destino in aristas:
            nodos_en_mst.add(origen)
            nodos_en_mst.add(destino)
    
    for cod in nodos_en_mst:
        if cod in info_aeropuertos:
            info = info_aeropuertos[cod]
            folium.CircleMarker(
                location=[info['latitude'], info['longitude']],
                radius=2,
                color="red",
                fill=True,
                fill_opacity=0.7,
                popup=f"{info['name']} ({cod})"
            ).add_to(mapa)
    
    nombre_archivo = "mst_vuelos.html"
    mapa.save(nombre_archivo)
    print(f"✓ Mapa MST generado: {nombre_archivo}")
    webbrowser.open(nombre_archivo)

def dibujar_10_lejanos(origen, lejanos, info_aeropuertos):
    info_org = info_aeropuertos[origen]
    mapa = folium.Map(location=[info_org['latitude'], info_org['longitude']], 
                      zoom_start=2, tiles="CartoDB positron")
    
    # Marcador especial para el origen
    folium.Marker(
        [info_org['latitude'], info_org['longitude']],
        popup=f"ORIGEN: {info_org['name']}",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(mapa)
    
    # Marcadores para los 10 lejanos y líneas de conexión
    for cod_dest, dist in lejanos:
        info_dest = info_aeropuertos[cod_dest]
        loc_dest = [info_dest['latitude'], info_dest['longitude']]
        
        folium.Marker(
            loc_dest,
            popup=f"{info_dest['name']} ({cod_dest})\nDistancia: {dist:.2f} km",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
        
        # Línea punteada que muestra la distancia radial
        folium.PolyLine(
            [[info_org['latitude'], info_org['longitude']], loc_dest],
            color="blue", weight=2, opacity=0.4, dash_array='5, 5'
        ).add_to(mapa)
        
    nombre_archivo = f"lejanos_{origen}.html"
    mapa.save(nombre_archivo)
    webbrowser.open(nombre_archivo)

def dibujar_caminos_lejanos(origen, lejanos, predecesores, info_aeropuertos):
    """Dibuja en el mapa las rutas completas calculadas por Dijkstra."""
    info_org = info_aeropuertos[origen]
    mapa = folium.Map(location=[info_org['latitude'], info_org['longitude']], 
                      zoom_start=2, tiles="CartoDB positron")
    
    # Lista de colores para que cada ruta sea distinguible
    colores = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkgreen', 'darkpurple', 'pink']
    
    # Dibujar el ORIGEN con un marcador especial
    folium.Marker(
        [info_org['latitude'], info_org['longitude']],
        popup=f"ORIGEN: {info_org['name']} ({origen})",
        icon=folium.Icon(color='black', icon='star')
    ).add_to(mapa)

    for i, (cod_dest, dist) in enumerate(lejanos):
        # 1. Reconstruir el camino usando tu función existente
        ruta = reconstruir_camino(predecesores, cod_dest)
        
        # 2. Convertir los códigos de aeropuerto en coordenadas [lat, lon]
        puntos_camino = []
        for nodo in ruta:
            info = info_aeropuertos[nodo]
            puntos_camino.append([info['latitude'], info['longitude']])
        
        color_ruta = colores[i % len(colores)]
        
        # 3. Dibujar la polilínea que sigue el camino real del grafo
        folium.PolyLine(
            puntos_camino,
            color=color_ruta,
            weight=3,
            opacity=0.7,
            popup=f"Ruta #{i+1} a {cod_dest} ({dist:.2f} km)"
        ).add_to(mapa)
        
        # 4. Marcador en el destino final
        folium.Marker(
            puntos_camino[-1],
            popup=f"Destino #{i+1}: {info_aeropuertos[cod_dest]['name']}\nDistancia: {dist:.2f} km",
            icon=folium.Icon(color=color_ruta, icon='plane')
        ).add_to(mapa)

    nombre_mapa = f"rutas_lejanas_{origen}.html"
    mapa.save(nombre_mapa)
    webbrowser.open(nombre_mapa)

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
        print("5. Encontrar ruta más corta entre dos aeropuertos")
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

        elif opcion == "5":
            orig = input("\nCódigo del aeropuerto de Origen: ").strip().upper()
            dest = input("Código del aeropuerto de Destino: ").strip().upper()
            
            if orig in grafo and dest in grafo:
                distancias, predecesores = dijkstra(grafo, orig)
                
                if distancias[dest] == float('inf'):
                    print(f"✗ No existe una ruta entre {orig} y {dest}")
                else:
                    ruta = reconstruir_camino(predecesores, dest)
                    print(f"\n✓ Ruta encontrada ({distancias[dest]:.2f} km):")
                    print(" -> ".join(ruta))
                    
                    # Llamamos a la función del mapa
                    dibujar_mapa(ruta, info_aeropuertos)
            else:
                print("✗ Uno o ambos códigos de aeropuerto no existen.")
            
        
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        
        else:
            print("\nOpción no válida")


# Ejecutar el programa
if __name__ == "__main__":
    menu_principal()
