import streamlit as st
import google.generativeai as genai
from PIL import Image

# Povlačimo ključ iz tajnih podešavanja sajta
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Greška: API ključ nije podešen u Secrets sekciji!")

st.set_page_config(page_title="Obračun Plate", layout="centered")

st.title("📊 Računanje Plate (Masovni Unos)")
st.write("Izaberite jednu ili više slika papira odjednom:")

# DODATO: accept_multiple_files=True omogućava izbor više slika odjednom
uploaded_files = st.file_uploader("Ubacite slike papira:", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    slike = []
    
    # Prolazimo kroz sve ubačene fajlove i otvaramo ih
    for uploaded_file in uploaded_files:
        slika = Image.open(uploaded_file)
        slike.append(slika)
        
    st.success(f"📸 Uspešno učitano slika: {len(uploaded_files)}")
    
    # Dugme koje pokreće zajednički obračun
    if st.button('🚀 Izračunaj Zajedničku Platu'):
        with st.spinner(f'AI trenutno čita svih {len(uploaded_files)} papira i spaja računicu...'):
            try:
                # Koristimo 2.0 Flash model koji bez problema guta više slika odjednom
                model = genai.GenerativeModel('gemini-1.5-flash')
                
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
                
                # Spajamo tekstualno uputstvo i listu svih slika u jedan paket za AI
                sadrzaj = [uputstvo] + slike
                
                response = model.generate_content(sadrzaj)
                st.success('Završeno!')
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Došlo je do greške: {e}")
