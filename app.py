import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# 1. NASTAVENÍ API KLÍČE
API_KEY = "AIzaSyAMvKTCBb0kaBk6__z8XJ-HVH02MuJj8mo"
genai.configure(api_key=API_KEY)

# Funkce pro načtení předpisů ze složky 'data'
def nacti_predpisy():
    text_vse = ""
    if os.path.exists("data"):
        for soubor in sorted(os.listdir("data")):
            if soubor.endswith(".txt"):
                with open(os.path.join("data", soubor), "r", encoding="utf-8") as f:
                    text_vse += f.read() + "\n\n"
    return text_vse

# Funkce pro vymazání textového pole po odeslání
def zpracovat_a_smazat():
    st.session_state.aktualni_dotaz = st.session_state.vstupni_pole
    st.session_state.vstupni_pole = ""

# --- DESIGN STRÁNKY ---
st.set_page_config(page_title="Rádce v předpisech", page_icon="🤖")

try:
    if os.path.exists("postavicka.png"):
        img = Image.open("postavicka.png")
        st.image(img, width=150)
    else:
        st.write("🤖")
except:
    st.write("🤖")

st.title("Tvůj rádce v předpisech")

if 'aktualni_dotaz' not in st.session_state:
    st.session_state.aktualni_dotaz = ""

st.text_input(
    "Tvoje otázka:", 
    placeholder="Napiš, co potřebuješ vědět a stiskni Enter...", 
    key="vstupni_pole", 
    on_change=zpracovat_a_smazat
)

kontext = nacti_predpisy()
dotaz = st.session_state.aktualni_dotaz

if dotaz:
    if not kontext:
        st.warning("Nemůžu najít žádné předpisy ve složce 'data'.")
    else:
        try:
            os.environ["GOOGLE_GENERATIVE_AI_DEFAULT_API_VERSION"] = "v1beta"
            model = genai.GenerativeModel('models/gemini-flash-lite-latest')
            
            prompt = f"""
            Jsi přátelský a odborný asistent, který pomáhá kolegům s výkladem předpisů. 
            
            Odpovídej POUZE na základě těchto textů: {kontext}.
            
            Pravidla:
            1. Odpovídej věcně a srozumitelně. Drž se faktů v předpisech.
            2. Používej tykání a na závěr přidej trochu ironie.
            3. Pokud odpověď v textu není, slušně to přiznej.
            4. Na konci odpovědi přidej jeden jemný emotikon 😊.
            
            Uživatel se ptá: {dotaz}
            """
            
            with st.spinner('Pavel listuje v papírech...'):
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        temperature=0.3,
                        max_output_tokens=1000
                    )
                )
                st.chat_message("user").write(dotaz)
                st.chat_message("assistant").write(response.text)
        except Exception as e:
            st.error(f"Chyba: {e}")
            
    st.session_state.aktualni_dotaz = ""



