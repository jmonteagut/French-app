import streamlit as st
from openai import OpenAI
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="unmute.", page_icon="⚡", layout="mobile")

# --- 2. ESTILOS CSS (Diseño Kai Moderno) ---
st.markdown("""
<style>
    /* Estructura */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    
    /* Título */
    .gradient-text {
        background: linear-gradient(45deg, #FF5F6D, #FFC371);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 2.5rem; margin: 0;
    }
    
    /* Tarjetas */
    .vocab-card {
        background-color: #F8F9FA; border-left: 5px solid #FF5F6D;
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Chat */
    .stChatMessage { padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; }
    .stChatInput textarea { border: 2px solid #FFC371 !important; border-radius: 15px; }
    
    /* Ocultar interfaz extra */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN IA ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Error: No encuentro la API Key. Configúrala en .streamlit/secrets.toml")
    st.stop()

def consultar_kai(mensajes, temperatura=0.7):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=mensajes, temperature=temperatura
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 4. CEREBRO DE LA IA (PROMPTS) ---
def get_system_prompt(dia, fase, modo="practica", tipo_examen=None):
    # --- NIVEL DE AYUDA (PROGRESIÓN) ---
    if dia <= 7: 
        idioma_inst = "Eres bilingüe (Francés/Español). Usa el español entre paréntesis para explicar cosas difíciles. Estás enseñando a un principiante absoluto."
    elif dia <= 14: 
        idioma_inst = "Habla mayormente en Francés. Usa el español SOLO si el usuario comete un error grave o no entiende."
    else: 
        idioma_inst = "MODO INMERSIÓN: Habla SOLO en Francés. Si el usuario habla español, respóndele en francés."

    base = f"Eres Kai, un tutor de francés joven y motivador. El tema de hoy es: '{fase}'. {idioma_inst}."

    # --- MODOS ---
    if modo == "vocab":
        return f"{base} Genera 5 palabras/frases clave sobre el tema. Formato lista con emojis: '🇫🇷 Francés - 🇪🇸 Español'."

    elif modo == "practica":
        return f"{base} El usuario está practicando. Mantén una charla fluida. IMPORTANTE: Corrige CADA error gramatical que cometa el usuario de forma amable antes de seguir hablando."

    elif modo == "examen_generador":
        # Aquí la IA genera el contenido inicial del examen según el tipo que tocó en la ruleta
        if tipo_examen == "traduccion":
            return f"Genera 3 frases cortas en ESPAÑOL relacionadas con '{fase}'. El usuario deberá traducirlas al francés. Sepáralas con un guion medio (-). Ejemplo: Hola - Gracias - Adios"
        elif tipo_examen == "quiz":
            return f"Genera 3 preguntas cortas (tipo test o directas) en Francés sobre gramática o cultura relacionada con '{fase}'. Sepáralas con un guion medio (-)."
        elif tipo_examen == "roleplay":
            return f"Define un escenario corto de roleplay sobre '{fase}'. Eres un personaje (ej: camarero). Di SOLO tu primera frase para empezar la escena en Francés. No pongas guiones."

    elif modo == "examen_roleplay_activo":
        # En el roleplay de examen, Kai NO corrige, solo actúa
        return f"Estamos en un Roleplay de examen sobre '{fase}'. Eres el personaje. Responde al usuario siguiendo la corriente. NO CORRIJAS ERRORES AHORA. Sé breve."

    elif modo == "corrector_final":
        return f"Actúa como un examinador estricto. Revisa el desempeño del usuario. Dale una nota final (0/10) y lista sus errores corregidos. Sé constructivo."

# --- 5. GESTIÓN DE ESTADO (MEMORIA) ---
if 'dia_actual' not in st.session_state: st.session_state.dia_actual = 1
if 'mensajes' not in st.session_state: st.session_state.mensajes = []
if 'vocabulario_dia' not in st.session_state: st.session_state.vocabulario_dia = None
# Estados de la app: 'practica', 'examen_activo', 'examen_finalizado'
if 'modo_app' not in st.session_state: st.session_state.modo_app = "practica"
# Variables del examen
if 'examen_tipo' not in st.session_state: st.session_state.examen_tipo = None # traduccion, quiz, roleplay
if 'examen_data' not in st.session_state: st.session_state.examen_data = [] # Preguntas o contexto
if 'examen_respuestas' not in st.session_state: st.session_state.examen_respuestas = [] # Lo que responde el usuario
if 'examen_progreso' not in st.session_state: st.session_state.examen_progreso = 0

# --- 6. SIDEBAR (NAVEGACIÓN) ---
with st.sidebar:
    st.header("🗺️ Tu Mapa")
    dia = st.session_state.dia_actual
    
    # Definir Fase
    if dia <= 7: fase = "Supervivencia Básica"
    elif dia <= 14: fase = "Vida Social y Gustos"
    elif dia <= 21: fase = "Viajes y Ciudad"
    else: fase = "Opinión y Debates"
    
    st.progress(dia / 30)
    st.caption(f"Día {dia} - {fase}")

    if st.button("🔄 Reiniciar Día"):
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.session_state.examen_tipo = None
        st.session_state.examen_progreso = 0
        st.rerun()

# --- 7. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)

# A) GENERAR VOCABULARIO (Automático al inicio)
if not st.session_state.vocabulario_dia:
    with st.spinner("Kai está preparando la lección..."):
        prompt_sys = get_system_prompt(dia, fase, "vocab")
        vocab = consultar_kai([{"role": "system", "content": prompt_sys}, {"role": "user", "content": "Vocabulario"}])
        st.session_state.vocabulario_dia = vocab

# Mostrar tarjeta siempre arriba
with st.expander("📚 Vocabulario del Día (Revisar)", expanded=True):
    st.markdown(f'<div class="vocab-card">{st.session_state.vocabulario_dia}</div>', unsafe_allow_html=True)

st.divider()

# B) ZONA DE CHAT (HISTORIAL)
for msg in st.session_state.mensajes:
    avatar = "🧢" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# --- 8. LÓGICA DEL EXAMEN (LA RULETA) ---

if st.session_state.modo_app == "examen_activo":
    tipo = st.session_state.examen_tipo
    progreso = st.session_state.examen_progreso
    
    # Texto del input según el tipo de examen
    if tipo == "roleplay":
        label_input = f"🎭 ROLEPLAY ({progreso+1}/3): Tu turno..."
    else:
        label_input = f"📝 PREGUNTA ({progreso+1}/3): Tu respuesta..."

    # INPUT DEL EXAMEN
    if respuesta := st.chat_input(label_input):
        # 1. Guardar respuesta visualmente
        st.session_state.mensajes.append({"role": "user", "content": respuesta})
        st.session_state.examen_respuestas.append(respuesta) # Guardamos para corregir luego
        
        # 2. Lógica según tipo
        st.session_state.examen_progreso += 1
        
        # ¿Terminó el examen (3 turnos)?
        if st.session_state.examen_progreso >= 3:
            st.session_state.modo_app = "examen_finalizado"
            st.rerun()
        else:
            # Si NO ha terminado, preparamos el siguiente turno
            if tipo == "roleplay":
                # En roleplay, Kai debe responder para seguir la historia
                prompt_sys = get_system_prompt(dia, fase, "examen_roleplay_activo")
                # Contexto: últimas lineas
                contexto_rp = st.session_state.mensajes[-3:] 
                msg_kai = consultar_kai([{"role": "system", "content": prompt_sys}] + contexto_rp)
                st.session_state.mensajes.append({"role": "assistant", "content": msg_kai})
            else:
                # En Traducción o Quiz, lanzamos la siguiente pregunta pre-generada
                siguiente_p = st.session_state.examen_data[st.session_state.examen_progreso]
                st.session_state.mensajes.append({"role": "assistant", "content": f"➡️ **Siguiente:** {siguiente_p}"})
            
            st.rerun()

# --- 9. CORRECCIÓN DEL EXAMEN (FINAL) ---
elif st.session_state.modo_app == "examen_finalizado":
    if len(st.session_state.mensajes) > 0 and st.session_state.mensajes[-1]["role"] != "assistant" or "RESULTADO" not in st.session_state.mensajes[-1]["content"]:
        with st.spinner("Kai está corrigiendo tu examen..."):
            # Recopilar todo lo que pasó en el examen
            log_examen = f"Tipo de Examen: {st.session_state.examen_tipo}\n"
            for i, resp in enumerate(st.session_state.examen_respuestas):
                log_examen += f"Turno {i+1}: Usuario dijo '{resp}'\n"
            
            prompt_sys = get_system_prompt(dia, fase, "corrector_final")
            correccion = consultar_kai([
                {"role": "system", "content": prompt_sys},
                {"role": "user", "content": f"Corrige esto:\n{log_examen}"}
            ])
            
            st.session_state.mensajes.append({"role": "assistant", "content": f"🎓 **RESULTADO FINAL:**\n\n{correccion}"})
            st.balloons()
            st.rerun()
    
    # Botón para avanzar de día
    if st.button("🚀 ¡Día Superado! Ir al siguiente", type="primary"):
        st.session_state.dia_actual += 1
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.session_state.examen_tipo = None
        st.session_state.examen_progreso = 0
        st.rerun()

# --- 10. LÓGICA DE PRÁCTICA (CHAT NORMAL) ---
elif st.session_state.modo_app == "practica":
    # Input de Chat Normal
    if prompt := st.chat_input("Practica con Kai (te corregirá)..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        
        # Respuesta IA
        prompt_sys = get_system_prompt(dia, fase, "practica")
        historial = [{"role": "system", "content": prompt_sys}] + st.session_state.mensajes[-5:]
        
        with st.spinner("Escribiendo..."):
            resp = consultar_kai(historial)
        
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        st.rerun()

    # BOTÓN PARA INICIAR EXAMEN (Aparece tras 2 mensajes)
    if len(st.session_state.mensajes) >= 2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎲 ¡RULETA DE EXAMEN!", type="primary", use_container_width=True):
                # 1. Sortear tipo de examen
                opciones = ["traduccion", "quiz", "roleplay"]
                tipo_tocado = random.choice(opciones)
                st.session_state.examen_tipo = tipo_tocado
                
                # 2. Generar contenido inicial
                with st.spinner(f"Preparando examen de tipo: {tipo_tocado.upper()}..."):
                    prompt_sys = get_system_prompt(dia, fase, "examen_generador", tipo_tocado)
                    raw_content = consultar_kai([{"role": "system", "content": prompt_sys}, {"role": "user", "content": "Go"}])
                    
                    if tipo_tocado == "roleplay":
                        # En roleplay, el raw_content es la primera frase de Kai
                        msg_inicial = f"🎭 **EXAMEN DE ROLEPLAY**\nSitación: {raw_content}\n*(Sigue la corriente. No te corregiré hasta el final)*"
                        st.session_state.examen_data = "roleplay_context" # No necesitamos lista de preguntas
                    else:
                        # En Traduccion/Quiz es una lista de preguntas separadas por guiones
                        preguntas = [p.strip() for p in raw_content.split("-") if p.strip()]
                        # Fallback por si la IA falla el formato
                        if len(preguntas) < 3: preguntas = ["Pregunta 1", "Pregunta 2", "Pregunta 3"]
                        st.session_state.examen_data = preguntas
                        msg_inicial = f"📝 **EXAMEN DE {tipo_tocado.upper()}**\nContesta las 3 preguntas seguidas.\n\n**Pregunta 1:** {preguntas[0]}"

                    # 3. Cambiar estado
                    st.session_state.modo_app = "examen_activo"
                    st.session_state.examen_progreso = 0
                    st.session_state.examen_respuestas = []
                    
                    # 4. Anunciar inicio
                    st.session_state.mensajes.append({"role": "assistant", "content": msg_inicial})
                    st.rerun()


















