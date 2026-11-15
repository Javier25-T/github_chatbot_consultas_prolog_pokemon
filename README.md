# PokéChat: chatbot Python + LLM + Prolog

## Arquitectura
- Flask sirve la interfaz web y recibe las preguntas.
- Ollama ejecuta Qwen 2.5 localmente y convierte la pregunta en una consulta estructurada.
- PySwip conecta Python con SWI-Prolog.
- Prolog entrega los datos; el chatbot no inventa tipos ni ventajas que no estén en la base.

## Requisitos
1. Python 3.10 o superior.
2. SWI-Prolog instalado: https://www.swi-prolog.org/download/stable
3. Ollama instalado: https://ollama.com/download
4. Modelo descargado:

```bash
ollama pull qwen2.5:3b
```

Dejar Ollama ejecutándose. En Windows normalmente queda activo como servicio/aplicación.

## Instalación

Abrir una terminal dentro de esta carpeta y ejecuta:

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Instala dependencias:
```bash
pip install -r requirements.txt
```

Si PySwip no encuentra SWI-Prolog, verificar que SWI-Prolog esté instalado y que su carpeta `bin` esté en PATH. En Windows suele ser `C:\Program Files\swipl\bin`. Cierra y vuelve a abrir la terminal después de modificar PATH.

## Ejecutar

```bash
python app.py
```

Abre en el navegador:
http://127.0.0.1:5000

## Preguntas de prueba
- ¿Qué tipo es Pikachu?
- ¿Qué tipos tiene Gyarados?
- ¿Qué tipo es Bulbasaur?
- ¿pikachu le gana a gyarados?
- ¿pierde pikachu contra onix?

## Cómo funciona una pregunta
1. El usuario pregunta en español.
2. Qwen identifica la intención y devuelve JSON (por ejemplo, `tipos_pokemon` para Pikachu).
3. Python valida los nombres y ejecuta una consulta Prolog.
4. La respuesta se construye con los resultados reales de Prolog y se muestra en la web.

El LLM interpreta la pregunta, pero Prolog es la fuente de verdad.
