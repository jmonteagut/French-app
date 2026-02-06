import streamlit as st
from openai import OpenAI

# 1. Configuración de la página
st.set_page_config(page_title="FrenchAgile AI", page_icon="🇫🇷", layout="centered")

# 2. Conexión con la IA (Busca la clave en los secretos de Streamlit)
# Si da error, muestra un mensaje amigable
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("No se ha encontrado la API Key. Configura .streamlit/secrets.toml")
    st.stop()

# 3. Función maestra para llamar a la IA
def consultar_ia(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Modelo rápido y barato
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# 4. Lógica de la Metodología (Tus Prompts Originales)
def obtener_prompt_sistema(tipo, fase):
    base = "Eres un tutor de francés experto que sigue la metodología 'Outcome-First Language Plan'."
    if tipo == "vocab":
        return f"{base} Genera vocabulario 'Frequency-Core' para la {fase}. Incluye: Palabra, Pronunciación aproximada, Significado y 1 ejemplo natural. Formato tabla Markdown."
    elif tipo == "drill":
        return f"{base} Haz una pregunta corta en francés basada en el contexto de {fase}. Espera la respuesta del usuario. Luego corrige ligeramente y mejora su frase ('Upgrade phrasing')."
    elif tipo == "roleplay":
        return f"{base} Inicia un 'Real Conversation Simulator' para un escenario de {fase}. Tú empiezas. Sé breve y espera la réplica del usuario."
    return base

# --- INTERFAZ DE USUARIO (UI) ---

st.title("🇫🇷 FrenchAgile AI")
st.markdown("*Tu entrenador personal de francés basado en resultados.*")

# Sidebar: Configuración
dia = st.sidebar.slider("Día del Plan (1-30)", 1, 30, 1)

# Determinar Fase automáticamente
if dia <= 7:
    fase = "Fase 1: Supervivencia (Cafés, Saludos, Taxis)"
elif dia <= 14:
    fase = "Fase 2: El Conector (Gustos, Social básica)"
elif dia <= 21:
    fase = "Fase 3: El Navegador (Resolver problemas, Wifi)"
else:
    fase = "Fase 4: El Sintetizador (Opiniones, Pasado)"

st.sidebar.info(f"📅 **{fase}**")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📚 Vocabulario", "⚡ Drills Rápidos", "🎭 Roleplay"])

# --- PESTAÑA 1: VOCABULARIO ---
with tab1:
    st.header("Vocabulario Core del Día")
    if st.button("Generar Lección de Hoy"):
        with st.spinner("Preparando tu material..."):
            sys_p = obtener_prompt_sistema("vocab", fase)
            resultado = consultar_ia(sys_p, f"Genera el material para el día {dia}.")
            st.markdown(resultado)

# --- PESTAÑA 2: DRILLS (CHAT) ---
with tab2:
    st.header("Speak-From-Day-One")
    st.caption("Responde a la pregunta. La IA corregirá tu gramática solo si es necesario.")
    
    # Historial del chat para Drills
    if "mensajes_drill" not in st.session_state:
        st.session_state.mensajes_drill = []

    # Botón de inicio
    if st.button("Iniciar Nuevo Drill"):
        sys_p = obtener_prompt_sistema("drill", fase)
        pregunta_inicial = consultar_ia(sys_p, "Empieza el ejercicio.")
        st.session_state.mensajes_drill = [{"role": "assistant", "content": pregunta_inicial}]

    # Mostrar historial
    for msg in st.session_state.mensajes_drill:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("Escribe tu respuesta en francés...", key="drill_input"):
        st.session_state.mensajes_drill.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Respuesta IA
        with st.spinner("Analizando..."):
            sys_p = obtener_prompt_sistema("drill", fase)
            # Pasamos el contexto previo para que entienda la conversación
            contexto = str(st.session_state.mensajes_drill[-3:]) 
            resp = consultar_ia(sys_p, f"El usuario respondió: '{prompt}'. Contexto previo: {contexto}. Corrige y sigue.")
            
            st.session_state.mensajes_drill.append({"role": "assistant", "content": resp})
            st.chat_message("assistant").write(resp)

# --- PESTAÑA 3: ROLEPLAY ---
with tab3:
    st.header("Simulador Real")
    escenario = st.selectbox("Elige situación:", ["Pedir en cafetería", "Comprar billete tren", "Check-in Hotel", "Presentarse a un grupo"])
    
    if st.button("🎬 ¡Acción!"):
        with st.spinner("Preparando escenario..."):
            sys_p = obtener_prompt_sistema("roleplay", f"{fase} - Escenario: {escenario}")
            intro = consultar_ia(sys_p, "Empieza el roleplay.")
            st.info(intro)
            st.text_area("Tu respuesta (simulación mental o escrita):", height=100)