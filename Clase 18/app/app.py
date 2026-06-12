# =============================================================================
# app.py - DEMO EDUCATIVA: Aplicación CRUD con Tkinter + MySQL
# =============================================================================
#
# OBJETIVO PEDAGÓGICO:
#   Este archivo demuestra cómo construir una aplicación de escritorio
#   profesional usando Tkinter/TTK con arquitectura en capas.
#
# CONCEPTOS CLAVE PARA ESTUDIANTES:
#   - Separación de responsabilidades: UI (App) vs Datos (DatabaseManager)
#   - Layout con grid() para organizar widgets
#   - Eventos y callbacks en Tkinter
#   - Estilos TTK personalizados (delegados a styles.py)
#   - Patrón CRUD completo (Create, Read, Update, Delete)
#
# FLUJO DE DATOS:
#   Usuario → GUI (Tkinter) → App → DatabaseManager → MySQL
#
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# Importar componentes modularizados (patrón de separación de responsabilidades)
from config import DB_CONFIG           # Configuración centralizada
from database import DatabaseManager   # Capa de acceso a datos
from styles import StyleManager        # Configuración visual centralizada


class App:
    """
    Capa de PRESENTACIÓN de la aplicación (MVC - Modelo/Vista/Controlador).
    
    Responsabilidad ÚNICA: Gestionar la interfaz gráfica (GUI) y eventos.
    NO realiza operaciones de base de datos directamente - delega a DatabaseManager.
    
    Arquitectura en Capas:
    ┌─────────────────────────────────────────────────┐
    │  App (Presentación - Tkinter)                   │  ← Este archivo
    │  - Maneja clicks, inputs, ventanas              │
    └───────────────────┬─────────────────────────────┘
                        │ Delega operaciones CRUD
    ┌───────────────────▼─────────────────────────────┐
    │  DatabaseManager (Acceso a Datos)               │  ← database.py
    │  - Conexiones, queries SQL                      │
    └───────────────────┬─────────────────────────────┘
                        │
    ┌───────────────────▼─────────────────────────────┐
    │  MySQL Server (Base de Datos)                   │
    └─────────────────────────────────────────────────┘
    
    Layout de la ventana (sistema grid):
        row=0: Tabla Treeview (ocupa máximo espacio vertical)
        row=1: Formulario + botones CRUD
        row=2: Botones de utilidad (Recargar, Importar)
        row=3: Barra de estado
    """
    def __init__(self, root):
        """
        Inicializa la aplicación: configura la ventana, conecta la base de datos,
        construye los widgets y carga los datos iniciales.

        Args:
            root (tk.Tk): Ventana principal de Tkinter.
        """
        # -------------------------------------------------------------------------
        # CONFIGURACIÓN DE LA VENTANA PRINCIPAL
        # -------------------------------------------------------------------------
        self.root = root
        self.root.title("Gestor de Clientes con MySQL")
        self.root.geometry("900x700")  # Tamaño inicial de la ventana (ancho x alto)
        
        # Estado de ordenamiento: diccionario que guarda la columna actual y dirección
        # Esto permite mantener el estado entre operaciones (patrón de estado)
        self.orden_actual = {'columna': 'nombre', 'direccion': 'ASC'}

        # Configurar icono de la ventana (try/except para que funcione sin icono)
        try:
            self.root.iconbitmap('icono.ico')
        except tk.TclError:
            pass  # Graceful degradation: si no hay icono, la app funciona igual

        # -------------------------------------------------------------------------
        # INICIALIZACIÓN DE COMPONENTES (en orden de dependencia)
        # -------------------------------------------------------------------------
        # 1. Capa de datos: establece conexión con MySQL y crea tablas si no existen
        self.db_manager = DatabaseManager(DB_CONFIG)

        # 2. Capa de presentación: configura colores, fuentes y estilos visuales
        StyleManager.configurar_estilos()

        # 3. Construcción de la interfaz: crea todos los widgets
        self.crear_widgets()
        
        # 4. Barra de estado: muestra conexión y cantidad de registros
        self.crear_barra_estado()
        
        # 5. Carga inicial de datos (solo si la conexión fue exitosa)
        # Nota: DatabaseManager establece self.connection = None si falla la conexión
        if self.db_manager.connection:
            self.cargar_datos()
        
        # 6. Protocolo de cierre: intercepta el botón X para cerrar la BD correctamente
        # Esto evita dejar conexiones abiertas al servidor MySQL
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def crear_widgets(self):
        """
        Construye y posiciona todos los widgets de la interfaz gráfica.
        
        Layout con grid (más espacio para la tabla):
          - row=0: Treeview (tabla) - ocupa 2 columnas, más altura
          - row=1: Frame "Datos del Cliente" con inputs y botones CRUD
          - row=2: Botones de utilidad (Recargar, Importar JSON)
          - row=3: Barra de estado
        """
        # -------------------------------------------------------------------------
        # SECCIÓN 1: TABLA DE CLIENTES (Treeview)
        # -------------------------------------------------------------------------
        # NOTA PARA ESTUDIANTES: El sistema grid() organiza widgets en una cuadrícula.
        # - sticky="nsew" (North-South-East-West) = expande en todas direcciones
        # - columnspan=2 = ocupa 2 columnas de ancho
        frame_tabla = ttk.Frame(self.root, padding="10")
        frame_tabla.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        # CONFIGURACIÓN DE PESOS (weight): Determina cómo se distribuye el espacio extra
        # cuando la ventana se redimensiona. Mayor peso = recibe más espacio.
        self.root.grid_rowconfigure(0, weight=3)    # Tabla: 3 partes del espacio extra
        self.root.grid_rowconfigure(1, weight=0)    # Formulario: tamaño fijo (0 = no expande)
        self.root.grid_rowconfigure(2, weight=0)    # Botones utilidad: tamaño fijo
        self.root.grid_rowconfigure(3, weight=0)    # Barra estado: tamaño fijo
        
        # Columnas con peso igual (1) para que se expandan uniformemente
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(frame_tabla, style='Modern.Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview: widget de tabla con filas y columnas, vinculado al scrollbar
        self.tabla = ttk.Treeview(frame_tabla, yscrollcommand=scrollbar.set, style='Modern.Treeview')
        self.tabla.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tabla.yview)
        
        # -------------------------------------------------------------------------
        # CONFIGURACIÓN DE LA TABLA (Treeview)
        # -------------------------------------------------------------------------
        # NOTA: Treeview es el widget de tabla de Tkinter.
        # - 'tag_configure' define estilos aplicables a filas individuales
        # - 'zebra striping' = filas intercaladas para mejor legibilidad
        self.tabla.tag_configure('evenrow', background='white')
        self.tabla.tag_configure('oddrow', background='#F5F5F5')

        # DEFINICIÓN DE COLUMNAS: Lista de tuplas con los identificadores
        # NOTA: Treeview siempre tiene una columna '#0' fantasma (árbol jerárquico).
        # La ocultamos con width=0 porque usamos columnas planas tipo Excel.
        self.tabla['columns'] = ('ID', 'Nombre', 'Email', 'Teléfono')
        self.tabla.column('#0', width=0, stretch=tk.NO)  # Ocultar columna fantasma
        self.tabla.column('ID', anchor=tk.CENTER, width=50)
        self.tabla.column('Nombre', anchor=tk.W, width=200)   # W = alineación izquierda (West)
        self.tabla.column('Email', anchor=tk.W, width=200)
        self.tabla.column('Teléfono', anchor=tk.W, width=120)

        # -------------------------------------------------------------------------
        # ENCABEZADOS ORDENABLES (TÉCNICA AVANZADA)
        # -------------------------------------------------------------------------
        # NOTA: El parámetro 'command' en heading() convierte
        # los encabezados en botones clickeables. Usamos lambda para pasar
        # el nombre de la columna al método ordenar_por().
        # Los símbolos ↕ ↑ ↓ indican visualmente el estado de ordenamiento.
        self.tabla.heading('#0', text='')
        self.tabla.heading('ID', text='ID ↕', anchor=tk.CENTER, command=lambda: self.ordenar_por('id'))
        self.tabla.heading('Nombre', text='Nombre ↑', anchor=tk.CENTER, command=lambda: self.ordenar_por('nombre'))
        self.tabla.heading('Email', text='Email ↕', anchor=tk.CENTER, command=lambda: self.ordenar_por('email'))
        self.tabla.heading('Teléfono', text='Teléfono ↕', anchor=tk.CENTER, command=lambda: self.ordenar_por('telefono'))
        
        # EVENTO: <<TreeviewSelect>> se dispara al hacer clic en una fila
        # Es un 'event binding' que conecta la acción del usuario con nuestro método
        self.tabla.bind('<<TreeviewSelect>>', self.seleccionar_cliente)
        
        # --- Frame para los campos de entrada y botones de registro ---
        frame_datos = ttk.LabelFrame(self.root, text="Datos del Cliente", padding="15", style='Card.TLabelframe')
        frame_datos.grid(row=1, column=0, columnspan=2, padx=15, pady=(5, 10), sticky="ew")
        
        # Campos de entrada
        ttk.Label(frame_datos, text="Nombre:", style='Modern.TLabel').grid(row=0, column=0, padx=8, pady=5, sticky="w")
        self.entry_nombre = ttk.Entry(frame_datos, width=35, style='Modern.TEntry')
        self.entry_nombre.grid(row=0, column=1, padx=8, pady=5, sticky="ew")

        ttk.Label(frame_datos, text="Email:", style='Modern.TLabel').grid(row=0, column=2, padx=8, pady=5, sticky="w")
        self.entry_email = ttk.Entry(frame_datos, width=30, style='Modern.TEntry')
        self.entry_email.grid(row=0, column=3, padx=8, pady=5, sticky="ew")

        ttk.Label(frame_datos, text="Teléfono:", style='Modern.TLabel').grid(row=0, column=4, padx=8, pady=5, sticky="w")
        self.entry_telefono = ttk.Entry(frame_datos, width=20, style='Modern.TEntry')
        self.entry_telefono.grid(row=0, column=5, padx=8, pady=5, sticky="ew")
        
        # Botones de operación de registro (fila 1 del frame_datos)
        frame_botones_registro = ttk.Frame(frame_datos)
        frame_botones_registro.grid(row=1, column=0, columnspan=6, pady=(15, 5), sticky="ew")
        frame_botones_registro.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        btn_agregar = ttk.Button(frame_botones_registro, text="➕ Agregar", command=self.agregar_cliente, style='Success.TButton')
        btn_agregar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        btn_actualizar = ttk.Button(frame_botones_registro, text="📝 Actualizar", command=self.actualizar_cliente, style='Primary.TButton')
        btn_actualizar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_eliminar = ttk.Button(frame_botones_registro, text="🗑️ Eliminar", command=self.eliminar_cliente, style='Danger.TButton')
        btn_eliminar.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        btn_limpiar = ttk.Button(frame_botones_registro, text="🧹 Limpiar", command=self.limpiar_campos, style='Neutral.TButton')
        btn_limpiar.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Permitir expansión de columnas de inputs
        for i in range(6):
            frame_datos.grid_columnconfigure(i, weight=1 if i % 2 == 1 else 0)
        
        # --- Frame para botones de utilidad ---
        frame_utilidad = ttk.Frame(self.root)
        frame_utilidad.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 5), sticky="e")
        
        btn_recargar = ttk.Button(frame_utilidad, text="🔄 Recargar Datos", command=self.recargar_datos, style='Neutral.TButton')
        btn_recargar.pack(side=tk.LEFT, padx=5)
        
        btn_importar = ttk.Button(frame_utilidad, text="📥 Importar JSON", command=self.importar_json, style='Primary.TButton')
        btn_importar.pack(side=tk.LEFT, padx=5)

    def recargar_datos(self):
        """
        Recarga los datos de la tabla desde la base de datos.
        Resetea el ordenamiento al valor por defecto (nombre ascendente).
        Útil para refrescar la vista manualmente si hubo cambios externos.
        """
        if self.db_manager.connection and self.db_manager.connection.is_connected():
            # Resetear ordenamiento al valor por defecto
            self.orden_actual = {'columna': 'nombre', 'direccion': 'ASC'}
            
            # Resetear textos de encabezados
            self.tabla.heading('ID', text='ID ↕')
            self.tabla.heading('Nombre', text='Nombre ↑')  # Por defecto ordenado por nombre ASC
            self.tabla.heading('Email', text='Email ↕')
            self.tabla.heading('Teléfono', text='Teléfono ↕')
            
            self.cargar_datos()
            messagebox.showinfo("Actualizado", "Datos recargados correctamente (orden por nombre).")
        else:
            messagebox.showwarning("Sin conexión", "No hay conexión a la base de datos.")

    def ordenar_por(self, columna):
        """
        Ordena la tabla por la columna seleccionada.
        Alterna entre ascendente (ASC) y descendente (DESC) en cada clic.
        
        PATRÓN: Mantenimiento de estado (self.orden_actual) + Feedback visual
        
        Args:
            columna: Nombre de la columna ('id', 'nombre', 'email', 'telefono')
        """
        # -------------------------------------------------------------------------
        # LÓGICA DE ESTADO: Mantenemos la columna y dirección en self.orden_actual
        # -------------------------------------------------------------------------
        # Caso 1: Clic en la MISMA columna → alternar dirección (ASC ↔ DESC)
        if self.orden_actual['columna'] == columna:
            self.orden_actual['direccion'] = 'DESC' if self.orden_actual['direccion'] == 'ASC' else 'ASC'
        else:
            # Caso 2: Clic en columna DIFERENTE → ordenar ascendente por defecto
            self.orden_actual['columna'] = columna
            self.orden_actual['direccion'] = 'ASC'
        
        # -------------------------------------------------------------------------
        # FEEDBACK VISUAL: Actualizamos los textos de los encabezados
        # -------------------------------------------------------------------------
        # Los iconos ↑ ↓ ↕ indican al usuario el estado actual del ordenamiento
        direccion_icono = '↑' if self.orden_actual['direccion'] == 'ASC' else '↓'
        columnas_texto = {
            'id': f'ID {direccion_icono}',
            'nombre': f'Nombre {direccion_icono}',
            'email': f'Email {direccion_icono}',
            'telefono': f'Teléfono {direccion_icono}'
        }
        
        # Resetear todos los encabezados al estado neutro (↕ = ordenable)
        self.tabla.heading('ID', text='ID ↕')
        self.tabla.heading('Nombre', text='Nombre ↕')
        self.tabla.heading('Email', text='Email ↕')
        self.tabla.heading('Teléfono', text='Teléfono ↕')
        
        # Destacar visualmente la columna activa con su icono de dirección
        columna_mapping = {
            'id': 'ID',
            'nombre': 'Nombre',
            'email': 'Email',
            'telefono': 'Teléfono'
        }
        self.tabla.heading(columna_mapping[columna], text=columnas_texto[columna])
        
        # -------------------------------------------------------------------------
        # EJECUCIÓN: Delegar a DatabaseManager que ejecuta el SQL con ORDER BY
        # -------------------------------------------------------------------------
        self.cargar_datos()

    def crear_barra_estado(self):
        """
        Crea una barra de estado en la parte inferior de la ventana
        que muestra el estado de conexión a MySQL.
        """
        frame_estado = ttk.Frame(self.root, relief='solid', borderwidth=1)
        frame_estado.grid(row=3, column=0, columnspan=2, sticky='ew', padx=15, pady=(0, 10))
        
        # Label de estado de conexión
        self.lbl_estado = ttk.Label(frame_estado, text="", font=('Segoe UI', 9))
        self.lbl_estado.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Separador
        ttk.Separator(frame_estado, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5, pady=5)
        
        # Label de cantidad de registros
        self.lbl_registros = ttk.Label(frame_estado, text="", font=('Segoe UI', 9))
        self.lbl_registros.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Actualizar estado inicial
        self.actualizar_barra_estado()
    
    def actualizar_barra_estado(self):
        """
        Actualiza los labels de la barra de estado según el estado
        de la conexión y la cantidad de registros cargados.
        """
        if self.db_manager.connection and self.db_manager.connection.is_connected():
            self.lbl_estado.config(text="🟢 Conectado a MySQL", foreground='#4CAF50')
        else:
            self.lbl_estado.config(text="🔴 Desconectado", foreground='#F44336')
        
        # Contar registros en la tabla
        cantidad = len(self.tabla.get_children())
        self.lbl_registros.config(text=f"📋 {cantidad} cliente{'s' if cantidad != 1 else ''}")

    def cargar_datos(self):
        """
        Recarga la tabla visual con los datos actuales de la base de datos.
        Primero limpia todas las filas existentes del Treeview para evitar duplicados,
        luego inserta cada registro obtenido desde DatabaseManager.
        Se llama al iniciar la app y después de cada operación de escritura.
        """
        # Limpiar todas las filas actuales del Treeview
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Insertar cada cliente como una nueva fila al final del Treeview
        clientes = self.db_manager.fetch_all_clientes(
            ordenar_por=self.orden_actual['columna'],
            direccion=self.orden_actual['direccion']
        )
        for i, cliente in enumerate(clientes):
            # Aplicar tag para fila intercalada (odd/even)
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tabla.insert('', tk.END, values=cliente, tags=(tag,))
        
        # Actualizar barra de estado
        self.actualizar_barra_estado()

    def agregar_cliente(self):
        """
        Lee los campos del formulario, valida que el nombre no esté vacío
        e inserta el nuevo cliente en la base de datos. Recarga la tabla al finalizar.
        """
        nombre = self.entry_nombre.get()
        email = self.entry_email.get()
        telefono = self.entry_telefono.get()
        
        # Validación: el nombre es el único campo obligatorio
        if not nombre:
            messagebox.showwarning("Campo Vacío", "El nombre es obligatorio.")
            return
            
        if self.db_manager.insert_cliente(nombre, email, telefono):
            messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
            self.limpiar_campos()
            self.cargar_datos()  # Refresca la tabla y la barra de estado

    def actualizar_cliente(self):
        """
        Actualiza los datos del cliente seleccionado en la tabla.
        Requiere que haya una fila seleccionada en el Treeview.
        El id del cliente se obtiene del primer valor de la fila seleccionada (columna ID).
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin Selección", "Por favor, selecciona un cliente para actualizar.")
            return
        
        # Obtiene el id de la fila seleccionada (primer valor, columna 'ID')
        client_id = self.tabla.item(seleccion[0])['values'][0]
        nombre = self.entry_nombre.get()
        email = self.entry_email.get()
        telefono = self.entry_telefono.get()
        
        if not nombre:
            messagebox.showwarning("Campo Vacío", "El nombre es obligatorio.")
            return

        if self.db_manager.update_cliente(client_id, nombre, email, telefono):
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            self.limpiar_campos()
            self.cargar_datos()  # Refresca tabla y barra de estado

    def eliminar_cliente(self):
        """
        Elimina el cliente seleccionado en la tabla, previa confirmación del usuario.
        Usa messagebox.askyesno() para mostrar un diálogo de confirmación antes de
        ejecutar la operación destructiva, evitando eliminaciones accidentales.
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin Selección", "Por favor, selecciona un cliente para eliminar.")
            return
        
        # Obtiene id y nombre del cliente desde los valores de la fila seleccionada
        cliente_info = self.tabla.item(seleccion[0])['values']
        client_id, nombre_cliente = cliente_info[0], cliente_info[1]
        
        # Diálogo de confirmación: retorna True si el usuario presiona 'Sí'
        respuesta = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar a {nombre_cliente}?")
        
        if respuesta:
            if self.db_manager.delete_cliente(client_id):
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.limpiar_campos()
                self.cargar_datos()  # Refresca tabla y barra de estado

    def importar_json(self):
        """
        Abre un diálogo para seleccionar un archivo JSON con clientes
        y los importa a la base de datos.
        
        El JSON debe tener el formato:
        [
            {"nombre": "Juan", "email": "juan@mail.com", "telefono": "1234"},
            {"nombre": "Ana", "email": "ana@mail.com", "telefono": "5678"}
        ]
        """
        if not self.db_manager.connection:
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return
        
        # Abrir diálogo de selección de archivo
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            defaultextension=".json"
        )
        
        if not archivo:
            return  # Usuario canceló
        
        try:
            # Leer el archivo JSON
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Validar que sea una lista
            if not isinstance(datos, list):
                messagebox.showerror("Error", "El archivo JSON debe contener una lista de clientes.")
                return
            
            # Contadores
            importados = 0
            errores = 0
            
            # Procesar cada cliente
            for cliente in datos:
                if not isinstance(cliente, dict):
                    errores += 1
                    continue
                
                nombre = cliente.get('nombre', '').strip()
                email = cliente.get('email', '').strip()
                telefono = cliente.get('telefono', '').strip()
                
                # Validar nombre obligatorio
                if not nombre:
                    errores += 1
                    continue
                
                # Insertar en la base de datos
                if self.db_manager.insert_cliente(nombre, email, telefono):
                    importados += 1
                else:
                    errores += 1
            
            # Mostrar resultado
            mensaje = f"Importación completada:\n\n"
            mensaje += f"✅ Importados: {importados}\n"
            mensaje += f"❌ Errores: {errores}"
            
            if importados > 0:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_datos()  # Refrescar tabla y barra de estado
            else:
                messagebox.showwarning("Advertencia", mensaje)
                
        except json.JSONDecodeError as e:
            messagebox.showerror("Error de JSON", f"El archivo no es un JSON válido:\n{e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se pudo encontrar el archivo seleccionado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")

    def seleccionar_cliente(self, event=None):
        """
        Evento disparado al hacer clic en una fila del Treeview (<<TreeviewSelect>>).
        Rellena automáticamente los campos del formulario con los datos del cliente
        seleccionado, facilitando la edición sin tener que escribir nuevamente.

        Args:
            event: Evento de Tkinter (se recibe automáticamente, no se usa directamente).
        """
        seleccion = self.tabla.selection()
        if not seleccion: return
        
        # valores[0]=id, valores[1]=nombre, valores[2]=email, valores[3]=telefono
        valores = self.tabla.item(seleccion[0])['values']
        
        # Limpia los campos sin deseleccionar la fila (deseleccionar=False)
        self.limpiar_campos(deseleccionar=False)
        self.entry_nombre.insert(0, valores[1])
        self.entry_email.insert(0, valores[2])
        self.entry_telefono.insert(0, valores[3])

    def limpiar_campos(self, deseleccionar=True):
        """
        Vacía los tres campos de entrada del formulario.

        Args:
            deseleccionar (bool): Si es True (por defecto), también quita la selección
                                   de la tabla. Se pasa False desde seleccionar_cliente()
                                   para no crear un bucle de eventos.
        """
        self.entry_nombre.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        
        if deseleccionar and self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection()[0])

    def on_closing(self):
        """
        Maneja el evento de cierre de la ventana (botón X).
        Cierra la conexión a MySQL antes de destruir la ventana para liberar
        los recursos del servidor correctamente.
        Se registra con root.protocol('WM_DELETE_WINDOW', ...) en __init__.
        """
        self.db_manager.close()
        self.root.destroy()


if __name__ == "__main__":
    # Crear la ventana principal
    ventana_principal = tk.Tk()
    # Iniciar la aplicación
    app = App(ventana_principal)
    # Iniciar el loop principal
    ventana_principal.mainloop()