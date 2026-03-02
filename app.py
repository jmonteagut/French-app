import streamlit as st
from openai import OpenAI
import random
import time
import re
import json 
import os   

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="unmute.", page_icon="🌊", layout="wide")

# --- 2. ESTILOS VISUALES PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC; /* Un tono aún más limpio y premium */
        color: #1E293B; 
    }
    
    p, h1, h2, h3, h4, h5, h6, input, button, textarea, div.markdown-text-container {
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.2px;
    }

    span[class*="material-symbols"], [data-testid="stIconMaterial"], svg {
        font-family: 'Material Symbols Rounded' !important;
        letter-spacing: normal !important;
    }

    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    
    /* Tipografía de títulos */
    .gradient-text {
        background: linear-gradient(135deg, #0284C7, #0EA5E9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 2.8rem; margin-bottom: 0; line-height: 1.2;
    }
    .subtitle { color: #64748B; font-size: 1.1rem; font-weight: 500; margin-bottom: 1.5rem; }
    
    /* Tarjetas y contenedores */
    .vocab-card {
        background: #FFFFFF; 
        border-left: 4px solid #0EA5E9;
        padding: 18px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        color: #334155 !important;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    /* Burbujas de chat rediseñadas */
    .stChatMessage { padding: 1rem; margin-bottom: 1rem; border: none !important; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) { background-color: #F0F9FF; border-radius: 16px 16px 16px 4px; }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) { background-color: #FFFFFF; border-radius: 16px 16px 4px 16px; border: 1px solid #E2E8F0 !important; }
    
    /* Botones Premium */
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0284C7, #0EA5E9) !important;
        border: none !important; border-radius: 8px !important; color: white !important; font-weight: 600 !important;
        box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.2); transition: all 0.2s;
    }
    button[data-testid="baseButton-primary"]:hover { transform: translateY(-1px); box-shadow: 0 6px 8px -1px rgba(2, 132, 199, 0.3); }
    
    button[data-testid="baseButton-secondary"] {
         border: 1px solid #0EA5E9 !important; color: #0EA5E9 !important; background: transparent !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    
    /* Inputs */
    .stChatInput textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] { 
        border: 1px solid #CBD5E1 !important; border-radius: 12px !important; background: #FFFFFF !important; color: #1E293B !important; 
    }
    .stChatInput textarea:focus, .stTextInput input:focus { border-color: #0EA5E9 !important; box-shadow: 0 0 0 1px #0EA5E9 !important; }
    
    /* Tarjeta de Onboarding (Bienvenida) */
    .onboarding-card {
        background: #FFFFFF;
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
        text-align: center;
        max-width: 600px;
        margin: 0 auto;
    }
    
    #MainMenu, footer, [data-testid="stToolbar"] {visibility: hidden;}
    header {background-color: transparent !important;}
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN IA ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Error: Configura tu API Key en los secrets.")
    st.stop()

def consultar_kai(mensajes, temperatura=0.7):
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=mensajes, temperature=temperatura)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 4. CEREBRO DE KAI (AHORA ADAPTATIVO AL NIVEL) ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    nombre = st.session_state.get('nombre_usuario', "Alumno")
    hobbies = st.session_state.get('intereses_usuario', "")
    nivel = st.session_state.get('nivel_usuario', "Principiante absoluto")
    
    perfil = f"Se llama {nombre}. Nivel de francés: {nivel}."
    if hobbies: perfil += f" Le gusta: {hobbies}."
        
    instruccion_nivel = f"IMPORTANTE: Adapta tu vocabulario, velocidad y complejidad al nivel del alumno ({nivel}). Si es principiante, usa frases muy cortas y acompáñalas siempre de traducción. Si es intermedio o avanzado, exígele más."
    
    base = f"Eres Kai, un profesor nativo y actor de roleplay en la app 'unmute'. SITUACIÓN ACTUAL: '{fase}'. INFO DEL ALUMNO: {perfil}. {instruccion_nivel}"

    if modo == "vocab":
        return f"{base} Genera una lista de 5 frases clave en FRANCÉS para esta situación adaptadas a su nivel. FORMATO ESTRICTO: Cada frase en una línea nueva. Usa este formato: \n- Emoji **Palabra en francés** (Pronunciación figurada) - Traducción en español."
    elif modo == "inicio_activo":
        return f"{base} 1. CONTEXTO (En Español): Explica la situación en 1 línea. 2. ACCIÓN (En Francés): Cambia de línea, entra en tu rol de actor para esta situación y lanza tu primera pregunta para que el alumno responda."
    elif modo == "practica": 
        return f"{base} TU ROL: Eres un ACTOR en la situación actual. 1. NO REPITAS lo que dice el usuario. 2. Responde natural como si fuera la vida real. 3. CORRECCIÓN INVISIBLE: Si comete un error gramatical, usa la forma correcta en tu respuesta sutilmente sin detener la conversación."
    elif modo == "pista": 
        return f"{base} El usuario se ha quedado en blanco. Sal de tu personaje un momento. Sé su tutor empático en español. Dale 2 opciones breves y útiles de qué podría decir a continuación en francés."
    elif modo == "examen_generador":
        sep = "Separa con '|||'. NO uses guiones."
        if contexto_extra == "traduccion": return f"3 frases en ESPAÑOL sobre '{fase}' adaptadas a su nivel para que las traduzca. {sep}"
        elif contexto_extra == "quiz": return f"3 preguntas test en FRANCÉS sobre '{fase}' (con traducción si es principiante). {sep}"
        elif contexto_extra == "roleplay": return f"Inicia un roleplay de examen sobre '{fase}'. Haz tu primera pregunta."
    elif modo == "examen_roleplay_activo": 
        return f"Roleplay examen. Actúa y responde evaluando en silencio. No ayudes ni des pistas."
    elif modo == "corrector_final": 
        return f"Evalúa su rendimiento. Formato estricto: NOTA: [0-10]/10. FEEDBACK: [Resumen constructivo en español]. TIPS: [2 Consejos prácticos]."

# --- 5. SISTEMA DE GUARDADO ---
ARCHIVO_PROGRESO = "progreso_kai.json"

def guardar_progreso():
    datos = {
        "onboarding_completado": st.session_state.onboarding_completado,
        "dia_actual": st.session_state.dia_actual, 
        "mensajes": st.session_state.mensajes, 
        "vocabulario_dia": st.session_state.vocabulario_dia,
        "modo_app": st.session_state.modo_app, 
        "examen_tipo": st.session_state.examen_tipo, 
        "examen_data": st.session_state.examen_data,
        "examen_respuestas": st.session_state.examen_respuestas, 
        "examen_progreso": st.session_state.examen_progreso, 
        "nota_final": st.session_state.nota_final,
        "nombre_usuario": st.session_state.get('nombre_usuario', ""), 
        "intereses_usuario": st.session_state.get('intereses_usuario', ""), 
        "nivel_usuario": st.session_state.get('nivel_usuario', "Principiante absoluto"),
        "pistas_usadas": st.session_state.get('pistas_usadas', 0)
    }
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f: json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_progreso():
    if os.path.exists(ARCHIVO_PROGRESO):
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f: return json.load(f)
    return None

# --- 6. GESTIÓN DE ESTADO ---
if 'iniciado' not in st.session_state:
    datos_guardados = cargar_progreso()
    if datos_guardados:
        for key, value in datos_guardados.items(): st.session_state[key] = value
        # Parches de seguridad para partidas antiguas
        if 'onboarding_completado' not in st.session_state: st.session_state.onboarding_completado = False
        if 'nivel_usuario' not in st.session_state: st.session_state.nivel_usuario = "Principiante absoluto"
    else:
        st.session_state.update({
            "onboarding_completado": False,
            "dia_actual": 1, "mensajes": [], "vocabulario_dia": None, "modo_app": "practica", "examen_tipo": None,
            "examen_data": [], "examen_respuestas": [], "examen_progreso": 0, "nota_final": None, 
            "nombre_usuario": "", "intereses_usuario": "", "nivel_usuario": "Principiante absoluto", "pistas_usadas": 0
        })
    st.session_state.iniciado = True

# --- 7. PANTALLA DE ONBOARDING (BIENVENIDA) ---
if not st.session_state.onboarding_completado:
    # Ocultamos la barra lateral forzosamente usando CSS
    st.markdown("<style>[data-testid='stSidebar'] {display: none !important;}</style>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("") # Espaciado
        st.write("")
        st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
        
        # Placeholder de la imagen de Kai (Se cambiará por la real luego)
        st.markdown('<div style="font-size: 80px; text-align: center; margin-bottom: 10px;">🧑‍🏫</div>', unsafe_allow_html=True)
        
        st.markdown('<h1 class="gradient-text" style="font-size: 2.5rem;">Bienvenido a unmute.</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <p style="color: #64748B; font-size: 1.1rem; margin-top: 15px; margin-bottom: 25px;">
        ¡Hola! Soy <b>Kai</b>, tu compañero de francés. <br><br>
        Aprender un idioma no va de memorizar listas interminables de gramática, va de <b>perder el miedo a hablar</b>. 
        En este programa de 30 días, te pondré en situaciones cotidianas reales (como pedir un café o coger el metro) 
        y practicaremos juntos mediante <i>Roleplay activo</i>. Yo actúo, tú respondes.
        <br><br>Para adaptar las clases perfectamente a ti, cuéntame un poco:
        </p>
        """, unsafe_allow_html=True)
        
        # Formulario de datos
        temp_name = st.text_input("¿Cómo te llamas?", placeholder="Ej: Carlos")
        temp_level = st.selectbox("¿Cuál es tu nivel actual de francés?", [
            "Principiante absoluto (No sé nada)", 
            "Básico (Conozco algunas palabras y saludos)", 
            "Intermedio (Puedo mantener una conversación sencilla)",
            "Avanzado (Quiero perfeccionar fluidez)"
        ])
        temp_hobbies = st.text_input("¿Cuáles son tus hobbies? (Opcional)", placeholder="Ej: Cine, deportes, viajar...")
        
        st.write("")
        if st.button("🚀 Empezar mi Viaje de 30 Días", type="primary", use_container_width=True):
            if temp_name.strip() == "":
                st.error("Por favor, dime cómo te llamas para poder empezar.")
            else:
                st.session_state.nombre_usuario = temp_name
                st.session_state.nivel_usuario = temp_level
                st.session_state.intereses_usuario = temp_hobbies
                st.session_state.onboarding_completado = True
                guardar_progreso()
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

# --- 8. LA APP PRINCIPAL (DASHBOARD) ---
else:
    # MENÚ LATERAL
    with st.sidebar:
        st.header("🗺️ Ruta 30 Días")
        dia = st.session_state.dia_actual
        
        fases_map = {1: "Cafetería: Pedir", 2: "Transporte: Metro", 3: "Supermercado", 4: "Restaurante: Alergias", 5: "Calle: Direcciones", 6: "Farmacia: Dolor", 7: "Hotel: Check-in"}
        fase = fases_map.get(dia, "Social: Conocer gente" if dia <= 14 else "Vida Profesional")
        
        st.progress(dia / 30)
        st.caption(f"Día {dia}: {fase}")
        st.divider()

        st.markdown("### 👤 Tu Perfil")
        st.text_input("Tu nombre:", key="nombre_usuario", on_change=guardar_progreso)
        st.selectbox("Nivel:", ["Principiante absoluto", "Básico", "Intermedio", "Avanzado"], index=["Principiante absoluto", "Básico", "Intermedio", "Avanzado"].index(st.session_state.nivel_usuario.split(" (")[0]) if "(" in st.session_state.nivel_usuario else 0, key="nivel_usuario", on_change=guardar_progreso)
        
        st.divider()
        if st.button("🔄 Borrar Partida y Reiniciar App"):
            if os.path.exists(ARCHIVO_PROGRESO): os.remove(ARCHIVO_PROGRESO)
            for k in ["mensajes", "vocabulario_dia", "examen_tipo", "examen_data", "examen_respuestas", "nota_final"]: st.session_state[k] = None if k in ["vocabulario_dia", "examen_tipo", "nota_final"] else []
            st.session_state.update({"dia_actual": 1, "modo_app": "practica", "examen_progreso": 0, "pistas_usadas": 0, "onboarding_completado": False})
            st.rerun()

    # GENERACIÓN INICIAL DEL DÍA
    if not st.session_state.vocabulario_dia:
        with st.spinner(f"Kai está preparando la Misión: {fase}..."):
            prompt_v = get_system_prompt(dia, fase, "vocab")
            st.session_state.vocabulario_dia = consultar_kai([{"role": "system", "content": prompt_v}, {"role": "user", "content": "Generar"}])
            if len(st.session_state.mensajes) == 0:
                prompt_i = get_system_prompt(dia, fase, "inicio_activo")
                inicio = consultar_kai([{"role": "system", "content": prompt_i}, {"role": "user", "content": f"Empieza la lección."}]) 
                st.session_state.mensajes.append({"role": "assistant", "content": inicio})
                guardar_progreso() 

    col_panel, espacio, col_chat = st.columns([1.2, 0.1, 2.5])

    # COLUMNA IZQUIERDA: CHULETA Y ACCIONES
    with col_panel:
        st.markdown('<div class="gradient-text">unmute.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="subtitle">Día {dia} | {fase}</div>', unsafe_allow_html=True)
        
        st.markdown("### 📚 Tu Chuleta")
        vocab_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', st.session_state.vocabulario_dia)
        vocab_html = vocab_html.replace('\n', '<br>')
        st.markdown(f'<div class="vocab-card">{vocab_html}</div>', unsafe_allow_html=True)
        
        st.markdown("### ⚡ Acciones")
        
        if st.session_state.modo_app == "practica":
            pistas_restantes = 2 - st.session_state.get('pistas_usadas', 0)
            if pistas_restantes > 0:
                if st.button(f"💡 Pedir Pista ({pistas_restantes})", use_container_width=True, type="secondary"):
                    st.session_state.pistas_usadas += 1
                    st.session_state.mensajes.append({"role": "user", "content": "*(Me he quedado en blanco, ¿me das una pista?)*"})
                    with st.spinner("Kai te ayuda..."):
                        resp = consultar_kai([{"role": "system", "content": get_system_prompt(dia, fase, "pista")}] + st.session_state.mensajes[-4:])
                    st.session_state.mensajes.append({"role": "assistant", "content": f"💡 **PISTA:**\n{resp}"})
                    guardar_progreso()
                    st.rerun()
            else:
                st.info("💡 0 Pistas. ¡Tú puedes!")

            st.write("") 
            if len(st.session_state.mensajes) >= 3:
                if st.button("🔥 HACER EL EXAMEN", type="primary", use_container_width=True):
                    tipo = random.choice(["traduccion", "quiz", "roleplay"])
                    st.session_state.examen_tipo = tipo
                    with st.spinner(f"Generando desafío..."):
                        raw = consultar_kai([{"role": "system", "content": get_system_prompt(dia, fase, "examen_generador", tipo)}, {"role": "user", "content": "Generar"}])
                        if tipo == "roleplay":
                            st.session_state.examen_data = "roleplay"
                            msg = f"🎭 **ROLEPLAY**\n{raw}"
                        else:
                            qs = [q.strip() for q in raw.split("|||") if q.strip()]
                            if len(qs) < 3: qs = [q.strip() for q in raw.split("\n") if q.strip() and "?" in q]
                            st.session_state.examen_data = qs[:3] if len(qs) >=3 else ["Traducción 1", "Traducción 2", "Traducción 3"]
                            msg = f"📝 **EXAMEN**\n1. {st.session_state.examen_data[0]}"
                        
                        st.session_state.modo_app = "examen_activo"
                        st.session_state.examen_progreso = 0
                        st.session_state.mensajes.append({"role": "assistant", "content": msg})
                        guardar_progreso() 
                        st.rerun()

    # COLUMNA DERECHA: CHAT
    with col_chat:
        chat_box = st.container(height=550, border=False)
        
        with chat_box:
            for msg in st.session_state.mensajes:
                avatar = "🧑‍🏫" if msg["role"] == "assistant" else "👤" # Cambiado a profe
                with st.chat_message(msg["role"], avatar=avatar):
                    st.write(msg["content"])

        if st.session_state.modo_app == "examen_activo":
            prog = st.session_state.examen_progreso
            if resp := st.chat_input(f"Simulación ({prog+1}/3)..."):
                st.session_state.mensajes.append({"role": "user", "content": resp})
                st.session_state.examen_respuestas.append(resp)
                st.session_state.examen_progreso += 1
                if st.session_state.examen_progreso >= 3:
                    st.session_state.modo_app = "examen_finalizado"
                else:
                    if st.session_state.examen_tipo == "roleplay":
                        ia_msg = consultar_kai([{"role": "system", "content": get_system_prompt(dia, fase, "examen_roleplay_activo")}] + st.session_state.mensajes[-3:])
                        st.session_state.mensajes.append({"role": "assistant", "content": ia_msg})
                    else:
                        st.session_state.mensajes.append({"role": "assistant", "content": f"➡️ {st.session_state.examen_data[st.session_state.examen_progreso]}"})
                guardar_progreso()
                st.rerun()

        elif st.session_state.modo_app == "examen_finalizado":
            if len(st.session_state.mensajes) > 0 and "RESULTADO" not in st.session_state.mensajes[-1]["content"]:
                with st.spinner("Evaluando..."):
                    log = "\n".join([f"R{i+1}: {r}" for i, r in enumerate(st.session_state.examen_respuestas)])
                    corr = consultar_kai([{"role": "system", "content": get_system_prompt(dia, fase, "corrector_final")}, {"role": "user", "content": log}])
                    st.session_state.mensajes.append({"role": "assistant", "content": f"📊 **RESULTADO:**\n\n{corr}"})
                    match = re.search(r"NOTA:\s*(\d+)", corr)
                    st.session_state.nota_final = int(match.group(1)) if match else 5
                    guardar_progreso()
                    st.rerun()

            nota = st.session_state.nota_final if st.session_state.nota_final is not None else 0
            if nota <= 5:
                st.error(f"Nota: {nota}/10. ¡Inténtalo de nuevo!")
                if st.button("🔄 REPETIR EXAMEN"):
                    st.session_state.update({"modo_app": "practica", "examen_respuestas": [], "examen_progreso": 0, "nota_final": None})
                    guardar_progreso(); st.rerun()
            else:
                st.success(f"¡Aprobado: {nota}/10!")
                if st.button("🚀 SIGUIENTE DÍA", type="primary"):
                    st.session_state.update({"dia_actual": dia + 1, "mensajes": [], "vocabulario_dia": None, "modo_app": "practica", "nota_final": None, "pistas_usadas": 0})
                    guardar_progreso(); st.rerun()

        elif st.session_state.modo_app == "practica":
            if prompt := st.chat_input("Escribe tu mensaje a Kai..."):
                st.session_state.mensajes.append({"role": "user", "content": prompt})
                with st.spinner("Kai está escribiendo..."):
                    resp = consultar_kai([{"role": "system", "content": get_system_prompt(dia, fase, "practica")}] + st.session_state.mensajes[-5:])
                st.session_state.mensajes.append({"role": "assistant", "content": resp})
                guardar_progreso() 
                st.rerun()









































