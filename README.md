## 1.Research Copilot: Análisis de Dinámicas Agrarias y Desarrollo Rural

Este proyecto es un asistente de investigación inteligente diseñado para procesar, indexar y consultar una biblioteca especializada de 20 artículos académicos sobre desarrollo rural, sociología agraria y economía agrícola. Utilizando una arquitectura RAG (Retrieval-Augmented Generation), el sistema permite realizar consultas semánticas precisas sobre textos complejos, garantizando la integridad de los metadatos (autores, años y páginas) mediante una sincronización estricta entre una base de datos de vectores y un catálogo maestro en formato JSON.

**Link Web:** https://research-copilot-7qhf9a2prvftcnfpipyrrh.streamlit.app/

## 1.1 📑 Campo de Estudio y Temáticas

Los artículos integrados en este repositorio se centran en el estudio de las transformaciones rurales contemporáneas, con especial énfasis en:

**Sujetos Agrarios:** Dinámicas de la juventud rural, sucesión generacional y el papel de la mujer en la agricultura.

**Economía y Productividad:** Análisis de la Productividad Total de Factores (PTF) en países como Perú y México.

**Nuevas Ruralidades:** Críticas al modelo neoliberal, la multilocalidad familiar y la integración de pequeños productores al mercado interno.

**Sustentabilidad y Estrategias de Vida:** Marcos teóricos sobre medios de vida sostenibles y enfoques territoriales del desarrollo.

## 🚀 2. Características

El sistema es capaz de:

- 📄 **Comprender y extraer información de documentos PDF**, procesando contenido académico de manera estructurada.

- 🔎 **Responder preguntas complejas**, recuperando pasajes relevantes mediante un sistema de búsqueda semántica.

- 📚 **Proporcionar citas precisas en formato APA**, garantizando la integridad de autores, año y páginas.

- 💬 **Mantener el contexto de la conversación** a lo largo de múltiples intercambios, permitiendo consultas encadenadas.

- 🌐 **Presentar la información a través de una interfaz web intuitiva y rica en funciones**, diseñada para facilitar la exploración del corpus académico.

## 3. Arquitectura
<img width="487" height="578" alt="image" src="https://github.com/user-attachments/assets/e1770f8f-5ef9-4935-adaa-5029dcedaf6a" />

## 4. Instalacion 

**Instalar dependencias**
pip install -r requirements.txt

**Configurar API Key (crear archivo .env)**
echo "OPENAI_API_KEY=tu_api_key_aqui" > .env

**Ejecutar la aplicación**
streamlit run app.py

## 5. Detalles tecnicos 

<img width="747" height="208" alt="image" src="https://github.com/user-attachments/assets/89cdbd5d-2606-4682-80e0-69f0db78bb15" />

<img width="839" height="281" alt="image" src="https://github.com/user-attachments/assets/f8b4fa83-4374-4a1a-abe5-59f509a84b34" />

## 6. Limitaciones

Se debe mejorar la sintesis de varios autores a la vez

Las citas a veces fallan

## 7. Datos de Autor

Autores: Imilla Córdova Chambi

Curso: Prompt Engineering - Qlab

Fecha: 3/03/2026

