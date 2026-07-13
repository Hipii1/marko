import streamlit as st
import requests
import base64
from PIL import Image

st.set_page_config(page_title="Obračun Plate", layout="centered")

st.title("📊 Računanje Plate (Masovni Unos) - Groq")
st.write("Izaberite jednu ili više slika papira odjednom:")

# Povlačimo Groq ključ iz tajnih podešavanja sajta
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("Greška: GROQ_API_KEY nije podešen u Secrets sekciji!")
    st.stop()

uploaded_files = st.file_uploader("Ubacite slike papira:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"📸 Uspešno učitano slika: {len(uploaded_files)}")
    
    if st.button('🚀 Izračunaj Zajedničku Platu'):
        with st.spinner(f'AI trenutno čita svih {len(uploaded_files)} papira i spaja računicu...'):
            try:
                uputstvo = """
                Ovo su slike dokumenata sa spiskovima artikala i cenama (ima ih više). 
                Pažljivo pročitaj SVE ubačene slike i sve stavke sa njih, a zatim izračunaj zaradu po sledećim pravilima:
                1. Ako je tip artikla Tapacir (ili tapacirani nameštaj), procenat je 5.5% (cena * 0.055).
                2. Ako je tip artikla Ploča (ili pločasti materijal), procenat je 2.4% (cena * 0.024).
                3. Ako je tip artikla Dušek, procenat je 1.2% (cena * 0.012).
                
                Prikaži rezultat u obliku JEDNE zajedničke, pregledne tabele sa kolonama: Artikal, Cena, Tip Posla, Moja Zarada.
                Na samom kraju, masnim slovima ispiši ukupan zbir za sve papire: 'UKUPNA ZARADA ZA SVE PAPIRE: [Suma svih zarada] rsd'.
                Obrati pažnju na tačnost brojeva. Odgovori isključivo na srpskom jeziku.
                """
                
                content_list = [{"type": "text", "text": uputstvo}]
                
                for uploaded_file in uploaded_files:
                    file_bytes = uploaded_file.read()
                    base64_data = base64.b64encode(file_bytes).decode("utf-8")
                    
                    mime_type = "image/jpeg"
                    if uploaded_file.name.lower().endswith(".png"):
                        mime_type = "image/png"
                        
                    content_list.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_data}"
                        }
                    })
                
                payload = {
                    "model": "llama-3.2-11b-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": content_list
                        }
                    ]
                }
                
                # Šaljemo na Groq server koji je besplatan
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                response = requests.post(url, headers=headers, json=payload)
                response_data = response.json()
                
                if response.status_code == 200:
                    odgovor = response_data["choices"][0]["message"]["content"]
                    st.success('Završeno!')
                    st.write(odgovor)
                else:
                    st.error(f"Groq API Greška ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Došlo je do neočekivane greške: {e}")
