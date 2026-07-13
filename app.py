import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

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
                # DETALJNA PRAVILA ZA KLASIFIKACIJU DA AI VIŠE NE GREŠI ARTIKLE
                uputstvo = """
                Ovo su slike dokumenata sa spiskovima artikala i cenama (ima ih više). 
                Pažljivo pročitaj SVE ubačene slike i sve stavke sa njih, a zatim kategorizuj artikle i izračunaj zaradu po sledećim STRIKTNIM pravilima:

                KATEGORIJE I PROCENTI:

                1. TAPACIR (Procenat: 5.5% -> cena * 0.055):
                   * Svi LEŽAJEVI (npr. Ležaj Fido, Ležaj Rock, Fido Rock, i bilo koji drugi ležaj). "Ležaj" NIJE dušek!
                   * Trosedi, dvosedi, fotelje, ugaone garniture, garniture, francuski ležajevi, kaučevi, sofe, taburei.
                   * Tapacirane stolice i bilo koji drugi tapacirani nameštaj.

                2. PLOČA (Procenat: 2.4% -> cena * 0.024):
                   * Sav pločasti nameštaj.
                   * Stolovi (trpezarijski, klub, radni, pisaći), komode, ormari, garderoberi, noćni ormarići, cipelarnici, police, kuhinje, predsoblja, TV komode, vitrine.
                   * Drveni kreveti (koji nisu tapacirani).

                3. DUŠEK (Procenat: 1.2% -> cena * 0.012):
                   * Isključivo i samo DUŠECI i NADDUŠECI (artikli koji u nazivu sadrže reč "dušek" ili "naddušek").

                Pravila za prikaz i računanje:
                - Prikaži rezultat u obliku JEDNE zajedničke, pregledne tabele sa kolonama: Artikal, Cena, Tip Posla (Tapacir, Ploča ili Dušek), Moja Zarada.
                - Na samom kraju, masnim slovima ispiši ukupan zbir za sve papire: 'UKUPNA ZARADA ZA SVE PAPIRE: [Suma svih zarada] rsd'.
                
                Budi ekstremno precizan sa brojevima. Prvo uradi matematiku u pozadini, pa onda prikaži tabelu.
                Odgovori isključivo na srpskom jeziku.
                """
                
                content_list = [{"type": "text", "text": uputstvo}]
                
                for uploaded_file in uploaded_files:
                    img = Image.open(uploaded_file)
                    
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Održavamo visoku oštrinu za čitanje sitnog teksta
                    max_size = 2000
                    if img.width > max_size or img.height > max_size:
                        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    file_bytes = buffer.getvalue()
                    
                    base64_data = base64.b64encode(file_bytes).decode("utf-8")
                    
                    content_list.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_data}"
                        }
                    })
                
                payload = {
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [
                        {
                            "role": "user",
                            "content": content_list
                        }
                    ],
                    "temperature": 0.0
                }
                
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
