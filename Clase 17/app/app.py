# app.py
# Archivo principal de la aplicación Tkinter.
# Contiene la interfaz de usuario y la lógica de eventos.

import tkinter as tk
from tkinter import ttk, messagebox

# Importar componentes desde los otros archivos
from config import DB_CONFIG
from database import DatabaseManager

class App:
    """
    Capa de presentación de la aplicación. Gestiona la interfaz gráfica (GUI)
    y los eventos del usuario, delegando las operaciones de datos a DatabaseManager.

    Arquitectura:
        App (presentación - Tkinter)
            ↓
        DatabaseManager (acceso a datos - MySQL)

    Layout de la ventana (grid):
        row=0  │ Treeview con tabla de clientes (columnspan=2)
        row=1  │ Frame inputs  │  Frame botones
    """
    def __init__(self, root):
        """
        Inicializa la aplicación: configura la ventana, conecta la base de datos,
        construye los widgets y carga los datos iniciales.

        Args:
            root (tk.Tk): Ventana principal de Tkinter.
        """
        self.root = root
        self.root.title("Gestor de Clientes con MySQL")
        self.root.geometry("900x650")

        # Crear instancia del gestor de base de datos
        self.db_manager = DatabaseManager(DB_CONFIG)

        # Crear los widgets de la interfaz
        self.crear_widgets()
        
        # Cargar datos iniciales solo si la conexión fue exitosa
        # (si MySQL no estaba disponible, connection será None)
        if self.db_manager.connection:
            self.cargar_datos()
        
        # Intercepta el botón X de cerrar ventana para cerrar la BD antes de salir
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def crear_widgets(self):
        """
        Construye y posiciona todos los widgets de la interfaz gráfica.
        Se estructura en tres secciones usando el gestor de layout 'grid':
          - Treeview (tabla): fila 0, ocupa las 2 columnas.
          - Frame de inputs: fila 1, columna 0.
          - Frame de botones: fila 1, columna 1.
        """
        # --- Frame para la tabla ---
        frame_tabla = ttk.Frame(self.root, padding="10")
        frame_tabla.grid(row=0, column=0, columnspan=2, sticky="nsew")
        # weight=1 permite que la fila/columna se expanda al redimensionar la ventana
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview: widget de tabla con filas y columnas, vinculado al scrollbar
        self.tabla = ttk.Treeview(frame_tabla, yscrollcommand=scrollbar.set)
        self.tabla.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tabla.yview)

        # Definir columnas (coinciden con los campos de la tabla MySQL)
        self.tabla['columns'] = ('ID', 'Nombre', 'Email', 'Teléfono')
        self.tabla.column('#0', width=0, stretch=tk.NO)  # Columna fantasma oculta (requerida por Treeview)
        self.tabla.column('ID', anchor=tk.CENTER, width=50)
        self.tabla.column('Nombre', anchor=tk.W, width=200)
        self.tabla.column('Email', anchor=tk.W, width=200)
        self.tabla.column('Teléfono', anchor=tk.W, width=120)

        self.tabla.heading('#0', text='')
        self.tabla.heading('ID', text='ID', anchor=tk.CENTER)
        self.tabla.heading('Nombre', text='Nombre', anchor=tk.CENTER)
        self.tabla.heading('Email', text='Email', anchor=tk.CENTER)
        self.tabla.heading('Teléfono', text='Teléfono', anchor=tk.CENTER)
        
        # Evento: al seleccionar una fila, rellenar los campos del formulario
        self.tabla.bind('<<TreeviewSelect>>', self.seleccionar_cliente)
        
        # --- Frame para los campos de entrada ---
        frame_inputs = ttk.LabelFrame(self.root, text="Datos del Cliente", padding="10")
        frame_inputs.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(frame_inputs, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nombre = ttk.Entry(frame_inputs, width=40)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_inputs, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_email = ttk.Entry(frame_inputs, width=40)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_inputs, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_telefono = ttk.Entry(frame_inputs, width=40)
        self.entry_telefono.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Permite que la columna de inputs se expanda horizontalmente
        frame_inputs.grid_columnconfigure(1, weight=1)

        # --- Frame para los botones ---
        frame_botones = ttk.Frame(self.root, padding="10")
        frame_botones.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        btn_agregar = ttk.Button(frame_botones, text="Agregar", command=self.agregar_cliente)
        btn_agregar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        btn_actualizar = ttk.Button(frame_botones, text="Actualizar", command=self.actualizar_cliente)
        btn_actualizar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_eliminar = ttk.Button(frame_botones, text="Eliminar", command=self.eliminar_cliente)
        btn_eliminar.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        btn_limpiar = ttk.Button(frame_botones, text="Limpiar Campos", command=self.limpiar_campos)
        btn_limpiar.grid(row=3, column=0, padx=5, pady=15, sticky="ew")

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
        clientes = self.db_manager.fetch_all_clientes()
        for cliente in clientes:
            self.tabla.insert('', tk.END, values=cliente)

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
            self.cargar_datos()  # Refresca la tabla para mostrar el nuevo registro

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
            self.cargar_datos()

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
                self.cargar_datos()

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