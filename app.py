import streamlit as st
from openai import OpenAI
import random
import time
import re
import json 
import os   

# --- 1. CONFIGURACIÓN (AHORA EN MODO WIDE) ---
st.set_page_config(page_title="unmute.", page_icon="🌊", layout="wide")

# --- 2. ESTILOS VISUALES ZEN & DASHBOARD ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #2C3E50; 
        letter-spacing: -0.3px; /* Esto le da un toque aún más premium y compacto */
    }
    
    .stApp { background-color: #F4F7F6; }

    /* Reducir márgenes superiores para aprovechar la pantalla */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    
    /* Títulos */
    .gradient-text {
        background: linear-gradient(135deg, #00B4DB, #0083B0);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 2.8rem; margin-bottom: 0; line-height: 1.2;
    }
    .subtitle { color: #7F8C8D; font-size: 1.1rem; font-weight: 600; margin-bottom: 1.5rem; }
    
    /* Tarjeta de Vocabulario (Ahora más compacta y elegante) */
    .vocab-card {
        background: #FFFFFF; 
        border-left: 5px solid #00B4DB;
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        color: #2C3E50 !important;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .vocab-card strong { color: #0083B0 !important; }
    
    /* Burbujas de chat */
    .stChatMessage { padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) { background-color: #EDF7F9; border: 1px solid #D6EAF8; border-radius: 18px 18px 18px 4px; }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) { background-color: #FFFFFF; border: 1px solid #E0E6ED; border-radius: 18px 18px 4px 18px; }
    
    /* Botones Control Panel */
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #00B4DB, #0083B0) !important;
        border: none !important; border-radius: 10px !important; color: white !important; font-weight: 700 !important;
    }
    button[data-testid="baseButton-secondary"] {
         border: 2px solid #00B4DB !important; color: #00B4DB !important; background: transparent !important; border-radius: 10px !important; font-weight: 700 !important;
    }
    
    /* Input de chat moderno */
    .stChatInput textarea { border: 2px solid #E0E6ED !important; border-radius: 16px !important; background: #FFFFFF !important; color: #2C3E50 !important; }
    .stChatInput textarea:focus { border-color: #00B4DB !important; }
    
    #MainMenu, footer, header, [data-testid="stToolbar"] {visibility: hidden;}
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

# --- 4. CEREBRO DE KAI ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    perfil = ""
    nombre = st.session_state.get('nombre_usuario', "")
    hobbies = st.session_state.get('intereses_usuario', "")
    
    if nombre: perfil += f" Se llama {nombre}."
    if hobbies: perfil += f" Le gusta: {hobbies}."
        
    instruccion_perfil = f"\nINFO DEL ALUMNO:{perfil} Úsalo para personalizar la charla." if perfil else ""
    formato_idioma = "FORMATO OBLIGATORIO: Frase en Francés (Traducción en Español)." if dia <= 7 else "Habla en francés. Usa español solo para dudas." if dia <= 14 else "Solo francés."
    base = f"Eres Kai. SITUACIÓN ACTUAL: '{fase}'. {formato_idioma} {instruccion_perfil}"

    if modo == "vocab":
        ext = "IMPORTANTE: Incluye 'S'il vous plaît', 'Merci' y 'Je voudrais...'." if dia <= 7 else ""
        return f"{base} Genera 5 frases clave en FRANCÉS para esta situación. {ext} Formato: Emoji Palabra (Pronunciación) - Traducción."
    elif modo == "inicio_activo":
        if dia == 1: return f"{base} ¡PRIMER DÍA! 1. PRESÉNTATE (En Español). 2. TRANSICIÓN: '¡Vamos allá!'. 3. ACCIÓN (En Francés + Español): Entra en rol y pregunta."
        else: return f"{base} 1. CONTEXTO (En Español): Explica la situación. 2. ACCIÓN (En Francés): Cambia de línea, entra en tu rol y pregunta."
    elif modo == "practica": return f"{base} TU ROL: Eres un ACTOR. 1. NO REPITAS lo que dice el usuario. 2. Responde natural. 3. CORRECCIÓN INVISIBLE: Si falla, usa la forma correcta sin regañar."
    elif modo == "pista": return f"{base} El usuario está en blanco. Sé su tutor en español. Dale 2 opciones breves de qué decir en francés."
    elif modo == "examen_generador":
        sep = "Separa con '|||'. NO uses guiones."
        if contexto_extra == "traduccion": return f"3 frases en ESPAÑOL sobre '{fase}' para traducir. {sep}"
        elif contexto_extra == "quiz": return f"3 preguntas test en FRANCÉS sobre '{fase}' (con traducción). {sep}"
        elif contexto_extra == "roleplay": return f"Inicia un roleplay sobre '{fase}'. Tu primera frase en FRANCÉS (con traducción)."
    elif modo == "examen_roleplay_activo": return f"Roleplay examen. Actúa y responde. No ayudes."
    elif modo == "corrector_final": return f"Evalúa. Formato: NOTA: [0-10]/10. FEEDBACK: [Resumen]. TIPS: [Consejos]."

# --- 5. SISTEMA DE GUARDADO ---
ARCHIVO_PROGRESO = "progreso_kai.json"

def guardar_progreso():
    datos = {
        "dia_actual": st.session_state.dia_actual, "mensajes": st.session_state.mensajes, "vocabulario_dia": st.session_state.vocabulario_dia,
        "modo_app": st.session_state.modo_app, "examen_tipo": st.session_state.examen_tipo, "examen_data": st.session_state.examen_data,
        "examen_respuestas": st.session_state.examen_respuestas, "examen_progreso": st.session_state.examen_progreso, "nota_final": st.session_state.nota_final,
        "nombre_usuario": st.session_state.get('nombre_usuario', ""), "intereses_usuario": st.session_state.get('intereses_usuario', ""), "pistas_usadas": st.session_state.get('pistas_usadas', 0)
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
        if 'pistas_usadas' not in st.session_state: st.session_state.pistas_usadas = 0
        if 'nombre_usuario' not in st.session_state: st.session_state.nombre_usuario = ""
        if 'intereses_usuario' not in st.session_state: st.session_state.intereses_usuario = ""
    else:
        st.session_state.update({
            "dia_actual": 1, "mensajes": [], "vocabulario_dia": None, "modo_app": "practica", "examen_tipo": None,
            "examen_data": [], "examen_respuestas": [], "examen_progreso": 0, "nota_final": None, "nombre_usuario": "", "intereses_usuario": "", "pistas_usadas": 0
        })
    st.session_state.iniciado = True

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header("🗺️ Ruta 30 Días")
    dia = st.session_state.dia_actual
    
    fases_map = {1: "Cafetería: Pedir", 2: "Transporte: Metro", 3: "Supermercado", 4: "Restaurante: Alergias", 5: "Calle: Direcciones", 6: "Farmacia: Dolor", 7: "Hotel: Check-in"}
    fase = fases_map.get(dia, "Social: Conocer gente" if dia <= 14 else "Vida Profesional")
    
    st.progress(dia / 30)
    st.caption(f"Día {dia}: {fase}")
    st.divider()

    with st.expander("👤 Tu Perfil", expanded=False):
        st.text_input("Tu nombre:", key="nombre_usuario", on_change=guardar_progreso)
        st.text_input("Hobbies (ej: cine, deporte):", key="intereses_usuario", on_change=guardar_progreso)
    st.divider()
    if st.button("🔄 Borrar Partida"):
        if os.path.exists(ARCHIVO_PROGRESO): os.remove(ARCHIVO_PROGRESO)
        for k in ["mensajes", "vocabulario_dia", "examen_tipo", "examen_data", "examen_respuestas", "nota_final"]: st.session_state[k] = None if k in ["vocabulario_dia", "examen_tipo", "nota_final"] else []
        st.session_state.update({"dia_actual": 1, "modo_app": "practica", "examen_progreso": 0, "pistas_usadas": 0})
        st.rerun()

# --- 8. ARQUITECTURA DASHBOARD (PANTALLA DIVIDIDA) ---
# Generación inicial en segundo plano
if not st.session_state.vocabulario_dia:
    with st.spinner(f"Preparando Misión: {fase}..."):
        prompt_v = get_system_prompt(dia, fase, "vocab")
        st.session_state.vocabulario_dia = consultar_kai([{"role": "system", "content": prompt_v}, {"role": "user", "content": "Generar"}])
        if len(st.session_state.mensajes) == 0:
            prompt_i = get_system_prompt(dia, fase, "inicio_activo")
            inicio = consultar_kai([{"role": "system", "content": prompt_i}, {"role": "user", "content": f"Vocabulario: {st.session_state.vocabulario_dia}. Empieza."}])
            st.session_state.mensajes.append({"role": "assistant", "content": inicio})
            guardar_progreso() 

# DIVIDIMOS LA PANTALLA EN 2 COLUMNAS (30% Izquierda / 70% Derecha)
col_panel, espacio, col_chat = st.columns([1.2, 0.1, 2.5])

# --- COLUMNA IZQUIERDA: PANEL DE CONTROL ---
with col_panel:
    st.markdown('<div class="gradient-text">unmute.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Día {dia} | {fase}</div>', unsafe_allow_html=True)
    
    st.markdown("### 📚 Tu Chuleta")
    st.markdown(f'<div class="vocab-card">{st.session_state.vocabulario_dia}</div>', unsafe_allow_html=True)
    
    st.markdown("### ⚡ Acciones")
    
    # Botonera movida al panel izquierdo para limpiar el chat
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

        st.write("") # Espacio
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

# --- COLUMNA DERECHA: CHAT INMERSIVO ---
with col_chat:
    # Contenedor con altura fija para que tenga scroll propio (como WhatsApp)
    chat_box = st.container(height=550, border=False)
    
    with chat_box:
        for msg in st.session_state.mensajes:
            avatar = "🧢" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

    # Lógica de inputs según el estado
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



































