import os
from dotenv import load_dotenv
from groq import Groq

# Cargar las variables de entorno (la API key)
load_dotenv()

# Configurar el cliente de Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def resumir_texto(texto_largo):
    print("[IA] Enviando texto a la IA para resumir...")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente experto en resumir textos en 3 puntos clave."
            },
            {
                "role": "user",
                "content": f"Por favor, resume el siguiente texto: '{texto_largo}'",
            }
        ],
        model="llama-3.1-8b-instant", # Modelo rápido y potente
    )
    resumen = chat_completion.choices[0].message.content
    return resumen

# Ejemplo de uso
articulo = """La inteligencia artificial (IA) está transformando el mundo a una velocidad vertiginosa, marcando un antes y
un después en la forma en que trabajamos, nos comunicamos y vivimos. Lo que hasta hace pocos años parecía ciencia ficción 
hoy es una realidad palpable: desde la automatización de tareas repetitivas en fábricas y oficinas hasta la creación de arte,
música y literatura mediante algoritmos avanzados, las aplicaciones de la IA parecen no tener límites.

Empresas de todos los sectores, desde la salud hasta la banca, pasando por la educación, la industria energética y 
el entretenimiento, están invirtiendo miles de millones de dólares en desarrollar sus propias capacidades de IA. El objetivo 
no es solo optimizar procesos internos o reducir costos, sino también mejorar la precisión en la toma de decisiones 
estratégicas, anticipar tendencias del mercado y, sobre todo, crear productos y servicios innovadores que antes resultaban 
impensables. La IA se ha convertido en un factor diferencial clave para la competitividad global.

En el campo de la medicina, por ejemplo, la IA está revolucionando el diagnóstico temprano y el descubrimiento de fármacos. 
Algoritmos de aprendizaje profundo analizan imágenes médicas con una precisión sobresaliente, permitiendo detectar 
enfermedades graves en etapas iniciales. Asimismo, los modelos predictivos ayudan a diseñar moléculas de medicamentos 
en una fracción del tiempo que solía tomar el proceso de investigación tradicional en el pasado.

Por otro lado, el sector educativo está experimentando una transición hacia el aprendizaje adaptativo. Las plataformas 
basadas en IA pueden evaluar en tiempo real las dificultades de cada estudiante, adaptando el contenido y las actividades 
a sus necesidades individuales. Esto no solo democratiza el acceso a una tutoría de alta calidad, sino que también redefine 
el rol del docente, quien pasa a ser un facilitador del desarrollo integral del alumno.

A su vez, el auge de estas tecnologías plantea importantes desafíos en el ámbito de la ciberseguridad. Por una parte, 
las herramientas inteligentes permiten identificar y neutralizar amenazas cibernéticas antes de que causen daños mayores. 
Por la otra, estas mismas tecnologías son empleadas por actores malintencionados para generar ataques más sofisticados, 
como la suplantación de identidad mediante imágenes o voces clonadas (deepfakes).

Sin embargo, este rápido avance también trae consigo una serie de desafíos éticos, sociales y legales que deben ser abordados
con seriedad. Surgen preguntas fundamentales: ¿cómo garantizar que los algoritmos sean justos y no reproduzcan sesgos? 
¿Qué impacto tendrá la automatización en los empleos tradicionales? ¿Cómo se deben regular el uso de los datos y la privacidad 
de los ciudadanos? ¿Qué responsabilidades deben asumir las empresas y los gobiernos ante posibles consecuencias negativas 
de estas tecnologías?

La respuesta a estas cuestiones exige un esfuerzo conjunto de científicos, legisladores, empresas 
y la sociedad en general. Solo a través de un marco ético sólido y políticas claras será posible aprovechar el enorme 
potencial de la inteligencia artificial sin dejar de lado la protección de los derechos humanos y la equidad social. 
En definitiva, la IA representa una herramienta poderosa que, bien utilizada, puede impulsar el progreso y el bienestar global,
pero cuyo desarrollo requiere responsabilidad, transparencia y un debate inclusivo.
"""

resumen_generado = resumir_texto(articulo)
print("\n[OK] Resumen generado:")
print(resumen_generado)