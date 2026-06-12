# =============================================================================
# styles.py - Sistema de Estilos TTK (Theme Toolkit)
# =============================================================================
#
# OBJETIVO PEDAGÓGICO:
#   Demostrar cómo centralizar la configuración visual de una aplicación
#   Tkinter usando el sistema de estilos ttk.Style().
#
# CONCEPTOS CLAVE PARA ESTUDIANTES:
#   - TTK (Themed Tk) vs Tkinter clásico: widgets modernos y nativos del SO
#   - style.configure(): define apariencia base de un tipo de widget
#   - style.map(): define apariencia en diferentes estados (hover, pressed)
#   - Temas (clam, alt, classic, vista, aqua): base visual predefinida
#   - Custom styles: crear estilos propios heredando de los estándar
#
# ARQUITECTURA DE ESTILOS:
#   'Nombre.Tipo' → Hereda del tipo base TTK
#   Ejemplo: 'Success.TButton' hereda de 'TButton' y modifica colores
#
# PALETA MATERIAL DESIGN:
#   Usamos colores estándar de Material Design para consistencia visual
#   - Primary: #2196F3 (azul)
#   - Success: #4CAF50 (verde)
#   - Danger: #F44336 (rojo)
#
# =============================================================================

from tkinter import ttk


class StyleManager:
    """
    Gestiona todos los estilos TTK de la aplicación.
    Centraliza la configuración visual para mantener consistencia.
    """
    
    # Paleta de colores Material Design
    PRIMARY = '#2196F3'      # Azul
    SUCCESS = '#4CAF50'      # Verde
    DANGER = '#F44336'       # Rojo
    NEUTRAL = '#757575'      # Gris
    BG = '#FAFAFA'           # Fondo gris claro
    
    @classmethod
    def configurar_estilos(cls, root=None):
        """
        Configura todos los estilos TTK personalizados.
        
        Args:
            root: Ventana raíz (opcional, para forzar actualización)
        """
        style = ttk.Style()
        # Forzar el tema clam para mejor compatibilidad
        style.theme_use('clam')
        
        # Frame de datos (tarjeta)
        style.configure('Card.TLabelframe',
            background=cls.BG,
            borderwidth=1,
            relief='solid')
        
        style.configure('Card.TLabelframe.Label',
            font=('Segoe UI', 11, 'bold'),
            foreground=cls.PRIMARY,
            background=cls.BG)
        
        # Botones de acción
        style.configure('Success.TButton',
            font=('Segoe UI', 10),
            background=cls.SUCCESS,
            foreground='white',
            padding=8)
        style.map('Success.TButton',
            background=[('active', '#388E3C'), ('pressed', '#2E7D32')])
        
        style.configure('Primary.TButton',
            font=('Segoe UI', 10),
            background=cls.PRIMARY,
            foreground='white',
            padding=8)
        style.map('Primary.TButton',
            background=[('active', '#1976D2'), ('pressed', '#1565C0')])
        
        style.configure('Danger.TButton',
            font=('Segoe UI', 10),
            background=cls.DANGER,
            foreground='white',
            padding=8)
        style.map('Danger.TButton',
            background=[('active', '#D32F2F'), ('pressed', '#C62828')])
        
        style.configure('Neutral.TButton',
            font=('Segoe UI', 10),
            background=cls.NEUTRAL,
            foreground='white',
            padding=8)
        style.map('Neutral.TButton',
            background=[('active', '#616161'), ('pressed', '#424242')])
        
        # Treeview moderno
        style.configure('Modern.Treeview',
            font=('Segoe UI', 10),
            rowheight=28,
            background='white',
            fieldbackground='white',
            borderwidth=0)
        
        style.configure('Modern.Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background=cls.PRIMARY,
            foreground='white',
            padding=8)
        
        # Nota: Los colores para filas intercaladas (zebra striping)
        # se configuran en el widget Treeview mediante tag_configure()
        # en app.py, ya que ttk.Style no soporta tags de Treeview.
        
        # Scrollbar moderno
        style.configure('Modern.Vertical.TScrollbar',
            background=cls.PRIMARY,
            troughcolor=cls.BG,
            borderwidth=0)
        
        # Etiquetas
        style.configure('Modern.TLabel',
            font=('Segoe UI', 10),
            background=cls.BG)
        
        # Inputs
        style.configure('Modern.TEntry',
            font=('Segoe UI', 10),
            padding=5)
    
    @classmethod
    def obtener_color(cls, nombre_color):
        """
        Retorna el valor hexadecimal de un color de la paleta.
        
        Args:
            nombre_color: 'PRIMARY', 'SUCCESS', 'DANGER', 'NEUTRAL', 'BG'
            
        Returns:
            str: Código hexadecimal del color
        """
        colores = {
            'PRIMARY': cls.PRIMARY,
            'SUCCESS': cls.SUCCESS,
            'DANGER': cls.DANGER,
            'NEUTRAL': cls.NEUTRAL,
            'BG': cls.BG
        }
        return colores.get(nombre_color, cls.NEUTRAL)
