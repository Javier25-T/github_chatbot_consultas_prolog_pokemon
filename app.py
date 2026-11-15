import json
import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from pyswip import Prolog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROLOG_FILE = os.path.join(BASE_DIR, "pokemon.pl")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

app = Flask(__name__, static_folder='.', static_url_path='')

# Carga la base de conocimiento una sola vez al iniciar el servidor.
prolog = Prolog()
prolog.consult(PROLOG_FILE)

TIPOS_VALIDOS = {
    "agua", "bicho", "dragon", "electrico", "fantasma", "fuego",
    "hada", "hielo", "lucha", "metal", "normal", "planta",
    "psiquico", "roca", "tierra", "veneno", "volador"
}

def consultar_llm(pregunta):
    """El LLM interpreta la pregunta y devuelve una consulta estructurada."""
    prompt = f"""
Eres un analizador de preguntas para una base de conocimiento Pokémon.
No respondas con conocimientos propios. Solo identifica qué consulta debe
realizar Python sobre Prolog.

Devuelve unicamente un objeto JSON con uno de estos formatos:
{{"accion":"tipos_pokemon","pokemon":"pikachu"}}
{{"accion":"pokemons_tipo","tipo":"agua"}}
{{"accion":"ventajas_tipo","tipo":"agua"}}
{{"accion":"combate_pokemon","pokemon1":"charizard","pokemon2":"blastoize"}}
{{"accion":"ganan_pokemon","pokemon":"pikachu"}}
{{"accion":"pokemons_combinacion_tipo","tipo1":"planta","tipo2":"veneno"}}
{{"accion":"desconocida"}}

Reglas:
- Usa nombres de Pokémon y tipos en minúsculas, sin tildes.
- Los tipos permitidos son: {", ".join(sorted(TIPOS_VALIDOS))}.
- "¿Qué tipo es Pikachu?" => tipos_pokemon.
- "¿charizard le gana a blastoise?" => combate_pokemon.
- Para combate_pokemon siempre debes devolver los campos pokemon1 y pokemon2.
- pokemon1 es el primer Pokémon mencionado.
- pokemon2 es el segundo Pokémon mencionado.
- Nunca utilices el campo "pokemon" para esta acción.
- No confundas los nombres de los Pokémon.
- "¿Contra qué tipos es fuerte el agua?" => ventajas_tipo.
- "¿Qué pokemons son de tipo agua?" => pokemons_tipo.
- "¿Qué pokemons le ganan a charizard?" => ganan_pokemon.
- "¿Qué pokemons son de la combinacion planta veneno?" => pokemons_combinacion_tipo.
- Si la pregunta no corresponde a esas consultas, usa desconocida.
- No inventes datos ni agregues explicaciones fuera del JSON.
"""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": pregunta}
                ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0}
        },
        timeout=200
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]
    return json.loads(content)

def normalizar_atom(valor):
    """Acepta únicamente átomos simples para evitar inyectar código Prolog."""
    valor_str = str(valor or "").strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", valor_str):
        raise ValueError(f"Nombre no válido detectado: '{valor_str}'")
    return valor_str

def ejecutar_consulta(datos):
    accion = datos.get("accion")

    if accion == "tipos_pokemon":
        pokemon = normalizar_atom(datos.get("pokemon"))
        resultados = list(prolog.query(f"tipo({pokemon}, Tipo)"))
        tipos = sorted({str(x["Tipo"]) for x in resultados})
        if tipos:
            return f"{pokemon.capitalize()} pertenece a los siguientes tipos: {', '.join(tipos)}."
        return f"No encontré a {pokemon.capitalize()} en la base de conocimiento."

    if accion == "ventajas_tipo":
        tipo = normalizar_atom(datos.get("tipo"))
        if tipo not in TIPOS_VALIDOS:
            return "Ese tipo no está registrado en la base de conocimiento."
        resultados = list(prolog.query(f"tipo_gana({tipo}, Objetivo)"))
        objetivos = sorted({str(x["Objetivo"]) for x in resultados})
        if objetivos:
            return f"Según la base Prolog, el tipo {tipo} tiene ventaja contra: {', '.join(objetivos)}."
        return f"No hay reglas de ventaja registradas para el tipo {tipo}."

    if accion == "combate_pokemon":
        pokemon1 = normalizar_atom(datos.get("pokemon1"))
        pokemon2 = normalizar_atom(datos.get("pokemon2"))
        # Comprobar que ambos Pokémon existan en Prolog
        existe1 = bool(list(prolog.query(f"tipo({pokemon1}, _)")))
        existe2 = bool(list(prolog.query(f"tipo({pokemon2}, _)")))
        if not existe1:
            return f"No encontré a {pokemon1} en la base de conocimiento."
        if not existe2:
            return f"No encontré a {pokemon2} en la base de conocimiento."
        if pokemon1 == pokemon2:
            return f"La base no registra una ventaja para pokemones de la misma especie"
        gana_pokemon1 = bool(list(prolog.query(f"gana({pokemon1}, {pokemon2})")))
        gana_pokemon2 = bool(list(prolog.query(f"gana({pokemon2}, {pokemon1})")))
        empate_pokemon = bool(list(prolog.query(f"empata({pokemon1}, {pokemon2})")))
        if gana_pokemon1 and gana_pokemon2:
            return f"Segun las reglas {pokemon1} y {pokemon2} tienen ventajas mutuas"
        elif gana_pokemon1:
            return f"Segun la base prolog, gana {pokemon1} a {pokemon2}"
        elif gana_pokemon2:
            return f"Segun la base prolog, pierde {pokemon1} contra {pokemon2}"
        elif empate_pokemon:
            return f"Segun la base prolog, {pokemon1} y {pokemon2} empatan, ninguno tiene ventaja sobre el otro." 
        return f"La base prolog no registra esa informacíon"

    if accion == "pokemons_tipo":
        tipo = normalizar_atom(datos.get("tipo"))
        if tipo not in TIPOS_VALIDOS:
            return "Ese tipo no está registrado en la base de conocimiento."
        resultados = list(prolog.query(f"tipo(Pokemons, {tipo})"))
        pokemons = sorted({str(x["Pokemons"]) for x in resultados })
        if pokemons:
            return f"Segun la base prolog, los pokemons de tipo {tipo} son: {', '.join(pokemons)}"
        return f"no hay pokemons de ese tipo"
    
    if accion == "pokemons_combinacion_tipo":
        tipo1 = normalizar_atom(datos.get("tipo1"))
        tipo2 = normalizar_atom(datos.get("tipo2"))
        if tipo1 and tipo2 not in TIPOS_VALIDOS:
            return "hay un(os) tipo(s) que no está registrado en la base de conocimiento."
        resultados = list(prolog.query(f"tipo(Pokemons, {tipo1}),tipo(Pokemons, {tipo2})"))
        pokemons = sorted({str(x["Pokemons"]) for x in resultados })
        if pokemons:
            return f"Segun la base prolog, los pokemons de la combinación de tipos {tipo1} y {tipo2} son: {', '.join(pokemons)}"    
        return f"No hay pokemons de la combinación de tipos {tipo1} y {tipo2}"

    if accion == "ganan_pokemon":
        pokemon = normalizar_atom(datos.get("pokemon"))
        existe = bool(list(prolog.query(f"tipo({pokemon}, _)")))
        if not existe:
            return f"no se encontro {pokemon} en la base prolog"
        resultados = list(prolog.query(f"gana(Pokemons, {pokemon})"))
        pokemons = sorted({str(x["Pokemons"]) for x in resultados })
        if pokemons:
            return f"Segun la base prolog, los pokemons que ganan a {pokemon} son: {', '.join(pokemons)}"
        return f"no hay pokemons que le ganen a {pokemon}"
    return ("Puedo responder preguntas sobre los tipos de un Pokémon, "
            "las ventajas de un tipo y los enfrentamientos entre dos pokemones. "
            "Prueba: «¿Qué tipo es Pikachu?»")


# conexion con el html
@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    datos_recibidos = request.get_json()
    mensaje_usuario = datos_recibidos.get('mensaje', '')
    
    if not mensaje_usuario:
        return jsonify({'respuesta': 'Mensaje vacío recibido.'}), 400

    try:
        # llama al llm y el prolog
        datos_json_llm = consultar_llm(mensaje_usuario)
        print("JSON generado por Ollama:", datos_json_llm)
        respuesta_bot = ejecutar_consulta(datos_json_llm)
    except Exception as e:
        respuesta_bot = f"Error procesando la consulta: {str(e)}"
        
    return jsonify({'respuesta': respuesta_bot})

if __name__ == '__main__':
    print("Iniciando servidor web y Prolog:")
    # Ollama debe estar corriendo en segundo plano para que funcione
    app.run(debug=True, port=5000)