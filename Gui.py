"""
Gui.py - Interfaz gráfica para el Laboratorio de Grafos (EDD2)
Usa Tkinter (incluido en Python estándar).
Requiere que laboratorio_grafos.py y flights_final.csv estén en la misma carpeta.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import laboratorio_grafos as lg


#  COLORES Y FUENTES 
BG_DARK    = "#0d1117"   # fondo principal
BG_PANEL   = "#161b22"   # fondo paneles
BG_CARD    = "#21262d"   # fondo tarjetas/botones
ACCENT     = "#58a6ff"   # azul accent
ACCENT2    = "#3fb950"   # verde éxito
WARN       = "#f85149"   # rojo error
TEXT_MAIN  = "#e6edf3"   # texto principal
TEXT_DIM   = "#8b949e"   # texto secundario
BORDER     = "#30363d"   # bordes

FONT_TITLE = ("Consolas", 16, "bold")
FONT_SUB   = ("Consolas", 10, "bold")
FONT_BODY  = ("Consolas", 10)
FONT_SMALL = ("Consolas", 9)


class AppGrafos(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("Laboratorio de Grafos – EDD2")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)

        # Estado compartido
        self.grafo = None
        self.info_aeropuertos = None
        self.aeropuerto_origen = None   # se guarda al ejecutar la opción 4

        self._construir_ui()
        self._cargar_datos()

    # ──────────────────────────────────────────
    #  CONSTRUCCIÓN DE LA UI
    # ──────────────────────────────────────────

    def _construir_ui(self):
        """Construye todos los widgets."""

        # ── Encabezado ──
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", padx=16, pady=(14, 0))

        tk.Label(
            header, text="✈  ANALIZADOR DE RUTAS AÉREAS",
            font=FONT_TITLE, fg=ACCENT, bg=BG_DARK
        ).pack(side="left")

        self.lbl_estado = tk.Label(
            header, text="⏳ Cargando datos...",
            font=FONT_SMALL, fg=TEXT_DIM, bg=BG_DARK
        )
        self.lbl_estado.pack(side="right", padx=8)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=8)

        # ── Cuerpo principal ──
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Panel izquierdo (controles)
        self.panel_izq = tk.Frame(body, bg=BG_PANEL, bd=0, relief="flat", width=280)
        self.panel_izq.pack(side="left", fill="y", padx=(0, 10))
        self.panel_izq.pack_propagate(False)

        # Panel derecho (resultados)
        panel_der = tk.Frame(body, bg=BG_PANEL, bd=0)
        panel_der.pack(side="left", fill="both", expand=True)

        self._construir_panel_controles()
        self._construir_panel_resultados(panel_der)

    def _construir_panel_controles(self):
        """Panel izquierdo: título + 5 botones de acción."""
        p = self.panel_izq

        tk.Label(
            p, text="ACCIONES", font=FONT_SUB,
            fg=TEXT_DIM, bg=BG_PANEL
        ).pack(anchor="w", padx=14, pady=(14, 6))

        # Definición de cada botón: (etiqueta, comando)
        botones = [
            ("1.  ¿Es conexo?",             self._accion_conexo),
            ("2.  ¿Es bipartito?",           self._accion_bipartito),
            ("3.  Peso del MST",             self._accion_mst),
            ("4.  Seleccionar Aeropuerto",  self._accion_mas_lejanos),
            ("5.  Ruta mínima en mapa",      self._accion_ruta_minima),
        ]

        self.btns = []
        for texto, cmd in botones:
            btn = tk.Button(
                p, text=texto, command=cmd,
                font=FONT_BODY,
                fg=TEXT_MAIN, bg=BG_CARD,
                activeforeground=ACCENT, activebackground=BG_DARK,
                relief="flat", bd=0, cursor="hand2",
                anchor="w", padx=12, pady=10,
                state="disabled"          # se habilitan al cargar datos
            )
            btn.pack(fill="x", padx=10, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2d333b"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_CARD))
            self.btns.append(btn)

        # Separador y botón limpiar
        ttk.Separator(p, orient="horizontal").pack(fill="x", padx=10, pady=10)

        tk.Button(
            p, text="🗑  Limpiar resultados",
            command=self._limpiar_resultados,
            font=FONT_SMALL, fg=TEXT_DIM, bg=BG_PANEL,
            activeforeground=WARN, activebackground=BG_PANEL,
            relief="flat", bd=0, cursor="hand2", pady=6
        ).pack(fill="x", padx=10)

    def _construir_panel_resultados(self, parent):
        """Panel derecho: área de texto con scroll."""
        tk.Label(
            parent, text="RESULTADOS", font=FONT_SUB,
            fg=TEXT_DIM, bg=BG_PANEL
        ).pack(anchor="w", padx=14, pady=(14, 4))

        self.txt_resultado = scrolledtext.ScrolledText(
            parent,
            font=FONT_BODY,
            fg=TEXT_MAIN, bg=BG_DARK,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            wrap="word",
            state="disabled"
        )
        self.txt_resultado.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tags de color para resaltar texto
        self.txt_resultado.tag_config("titulo",   foreground=ACCENT,  font=("Consolas", 11, "bold"))
        self.txt_resultado.tag_config("ok",        foreground=ACCENT2)
        self.txt_resultado.tag_config("error",     foreground=WARN)
        self.txt_resultado.tag_config("dim",       foreground=TEXT_DIM)
        self.txt_resultado.tag_config("normal",    foreground=TEXT_MAIN)

    # ──────────────────────────────────────────
    #  CARGA DE DATOS (en hilo separado para no
    #  congelar la ventana)
    # ──────────────────────────────────────────

    def _cargar_datos(self):
        """Carga el CSV en un hilo secundario."""
        def _tarea():
            try:
                self.grafo, self.info_aeropuertos = lg.construir_grafo_desde_csv("flights_final.csv")
                self.after(0, self._datos_listos)
            except FileNotFoundError:
                self.after(0, lambda: self._datos_error(
                    "No se encontró flights_final.csv.\n"
                    "Asegúrate de que esté en la misma carpeta que Gui.py."
                ))
            except Exception as e:
                self.after(0, lambda: self._datos_error(str(e)))

        threading.Thread(target=_tarea, daemon=True).start()

    def _datos_listos(self):
        """Callback cuando los datos cargaron bien."""
        n = len(self.grafo)
        self.lbl_estado.config(
            text=f"✓ {n:,} aeropuertos cargados", fg=ACCENT2
        )
        for btn in self.btns:
            btn.config(state="normal")
        self._escribir(f"Grafo cargado correctamente: {n:,} aeropuertos.\n", "ok")
        self._escribir("Selecciona una acción en el panel izquierdo.\n", "dim")

    def _datos_error(self, msg):
        """Callback cuando falla la carga."""
        self.lbl_estado.config(text="✗ Error al cargar", fg=WARN)
        messagebox.showerror("Error de carga", msg)

    # ──────────────────────────────────────────
    #  UTILIDADES DE ESCRITURA
    # ──────────────────────────────────────────

    def _escribir(self, texto, tag="normal"):
        """Agrega texto al área de resultados."""
        self.txt_resultado.config(state="normal")
        self.txt_resultado.insert("end", texto, tag)
        self.txt_resultado.see("end")
        self.txt_resultado.config(state="disabled")

    def _limpiar_resultados(self):
        self.txt_resultado.config(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.config(state="disabled")

    def _separador(self):
        self._escribir("─" * 60 + "\n", "dim")

    # ──────────────────────────────────────────
    #  ACCIONES (por ahora son stubs)
    # ──────────────────────────────────────────

    def _accion_conexo(self):
        self._separador()
        self._escribir("▶ Verificando conexidad...\n", "titulo")
        
        def _tarea():
            es_con, num_comp, tamaños = lg.es_conexo(self.grafo)
            self.after(0, lambda: self._mostrar_conexo(es_con, num_comp, tamaños))

        threading.Thread(target=_tarea, daemon=True).start()

    def _mostrar_conexo(self, es_con, num_comp, tamaños):
            if es_con:
                self._escribir("✓ El grafo ES conexo.\n", "ok")
            else:
                self._escribir(f"✗ El grafo NO es conexo.\n", "error")
                self._escribir(f"  Número de componentes: {num_comp}\n", "normal")
                # Mostrar las 10 componentes más grandes para no llenar la pantalla
                tamaños_ord = sorted(tamaños, reverse=True)
                self._escribir(f"  Vértices por componente\n", "dim")
                for i, t in enumerate(tamaños_ord[:10], 1):
                    self._escribir(f"    {i}. {t:,} aeropuertos\n", "normal")
                if len(tamaños) > 10:
                    self._escribir(f"    ... y {len(tamaños)-10} componentes más pequeñas\n", "dim")

    def _accion_bipartito(self):
        self._separador()
        self._escribir("▶ Verificando si el grafo es bipartito...\n", "titulo")
        self._escribir("  (Se analiza la componente más grande)\n", "dim")

        def _tarea():
            resultado = lg.es_bipartito(self.grafo)
            self.after(0, lambda: self._mostrar_bipartito(resultado))

        threading.Thread(target=_tarea, daemon=True).start()

    def _mostrar_bipartito(self, resultado):
        if resultado:
            self._escribir("✓ La componente más grande ES bipartita.\n", "ok")
        else:
            self._escribir("✗ La componente más grande NO es bipartita.\n", "error")
            self._escribir(
                "  Esto es esperado en grafos de vuelos: existen rutas\n"
                "  circulares que crean ciclos de longitud impar.\n", "dim"
            )
            
    def _accion_mst(self):
        self._separador()
        self._escribir("▶ Calculando árbol de expansión mínima...\n", "titulo")
        self._escribir("  Esto puede tardar unos segundos ⏳\n", "dim")

        def _tarea():
            pesos, aristas_componentes = lg.calcular_aem(self.grafo)
            self.after(0, lambda: self._mostrar_mst(pesos, aristas_componentes))

        threading.Thread(target=_tarea, daemon=True).start()

    def _mostrar_mst(self, pesos, aristas_componentes):
        # Emparejamos peso con sus aristas y ordenamos de mayor a menor
        componentes = sorted(zip(pesos, aristas_componentes),
                            key=lambda x: x[0], reverse=True)

        total = sum(pesos)
        num = len(pesos)

        self._escribir(f"  Componentes encontradas: {num}\n", "normal")
        self._escribir(f"  Peso total (suma de todos los MST): {total:,.2f} km\n\n", "ok")

        self._escribir("  Detalle por componente:\n", "titulo")
        self._escribir(f"  {'#':<4} {'Aristas MST':<14} {'Peso (km)'}\n", "dim")
        self._escribir("  " + "─" * 38 + "\n", "dim")

        for i, (peso, aristas) in enumerate(componentes, 1):
            self._escribir(
                f"  {i:<4} {len(aristas):<14} {peso:>14,.2f} km\n", "normal"
            )

        self._escribir("\n  Abriendo mapa del MST en el navegador...\n", "dim")

        aristas_ordenadas = [a for _, a in componentes]

        def _abrir_mapa():
            lg.dibujar_mst(aristas_ordenadas, self.info_aeropuertos)

        threading.Thread(target=_abrir_mapa, daemon=True).start()

# En Gui.py
    def _accion_mas_lejanos(self):
        from tkinter import simpledialog
        self._separador()
        self._escribir("▶ Consultar aeropuerto y 10 más lejanos\n", "titulo")
        
        # 1. Solicitar el código del nodo (aeropuerto)
        codigo = simpledialog.askstring("Seleccionar Nodo", "Ingresa el código IATA (ej: BOG):", parent=self)
        
        if not codigo:
            self._escribir("  Operación cancelada.\n", "dim")
            return
            
        codigo = codigo.strip().upper()
        
        # 2. Validar si existe en el grafo
        if codigo not in self.grafo:
            self._escribir(f"  ✗ El aeropuerto '{codigo}' no existe en el sistema.\n", "error")
            return

        # 3. Cálculo en segundo plano para no congelar la GUI
        def _tarea():
            try:
                # Calcular distancias desde el origen usando Dijkstra
                distancias, predecesores = lg.dijkstra(self.grafo, codigo)
                # Obtener el top 10 de los más lejanos
                lejanos = lg.Diez_aeropuertos_mas_lejanos(self.grafo, distancias, self.info_aeropuertos)
                
                # Mostrar información del nodo y lista en la interfaz
                self.after(0, lambda: self._mostrar_resultados_lejanos(codigo, lejanos))
                
                # Generar y abrir el mapa
                lg.dibujar_caminos_lejanos(codigo, lejanos, predecesores, self.info_aeropuertos)
                
            except Exception as e:
                self.after(0, lambda: self._escribir(f" Error: {str(e)}\n", "error"))

        threading.Thread(target=_tarea, daemon=True).start()

    def _mostrar_resultados_lejanos(self, origen, lejanos):
        info_o = self.info_aeropuertos[origen]
        
        # Mostrar la info del aeropuerto consultado
        self._escribir(f"\n  [INFO NODO SELECCIONADO]\n", "ok")
        self._escribir(f"  Código: {origen}\n", "normal")
        self._escribir(f"  Aeropuerto: {info_o['name']}\n", "normal")
        self._escribir(f"  Ubicación: {info_o['city']}, {info_o['country']}\n\n", "normal")
        self._escribir(f"  Latitud:    {info_o['latitude']}\n", "normal")
        self._escribir(f"  Longitud:   {info_o['longitude']}\n\n", "normal")
        
        # Mostrar la tabla de resultados
        self._escribir("  LOS 10 MÁS LEJANOS (Camino Mínimo):\n", "titulo")
        self._escribir(f"  {'#':<4} {'Cód':<5} {'Ciudad':<20} {'Distancia'}\n", "dim")
        self._escribir("  " + "─" * 45 + "\n", "dim")
        
        for i, (cod_dest, dist) in enumerate(lejanos, 1):
            info_d = self.info_aeropuertos[cod_dest]
            self._escribir(f"  {i:<4} {cod_dest:<5} {info_d['city'][:18]:<20} {dist:>10,.2f} km\n", "normal")
        
        self._escribir("\n✓ Mapa generado y abierto en el navegador.\n", "ok")
    def _accion_ruta_minima(self):
        self._separador()
        self._escribir("▶ Calculando ruta mínima...\n", "titulo")
        self._escribir("(próximamente)\n", "dim")


# ──────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app = AppGrafos()
    app.mainloop()
