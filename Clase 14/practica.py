# Crear un archivo con frases favoritas. Leerlo al azar.
import random
frases = [
    "La vida es un sueño, y los sueños, sueños son.",
    "En un lugar de la Mancha, de cuyo nombre no quiero acordarme.",
    "El amor en tiempos del cólera.",
    "Cien años de soledad.",
]

# Crear el archivo y escribir las frases
with open('frases_favoritas.txt', 'w') as archivo:
    for frase in frases:
        archivo.write(frase + "\n")

# Leer una frase al azar
with open('frases_favoritas.txt', 'r') as archivo:
    lineas = archivo.readlines()
    frase_aleatoria = random.choice(lineas).strip()
    print(f"Frase aleatoria: {frase_aleatoria}")