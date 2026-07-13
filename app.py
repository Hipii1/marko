import streamlit as st
import google.generativeai as genai
from PIL import Image

# Povlačimo ključ iz tajnih podešavanja sajta
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Greška: API ključ nije podešen u Secrets sekciji!")

st.set_page_config(page_title="Obračun Plate", layout="centered")

st.title("📊 Računanje Plate")
st.write("Uslikajte papir sa posla i sačekajte računicu.")

# Polje za kameru ili galeriju na telefonu
uploaded_file = st.file_uploader("Klikni ispod da uslikaš papir:", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    slika = Image.open(uploaded_file)
    st.image(slika, caption='Učitana slika', use_container_width=True)
    
    if st.button('🚀 Izračunaj Platu'):
        with st.spinner('AI trenutno čita papir i računa...'):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                uputstvo = """
                Ovo je slika sa spiskom artikala i cenama. 
                Pažljivo pročitaj sve stavke i cene, a zatim izračunaj zaradu po sledećim pravilima:
                1. Ako je tip artikla Tapacir (ili tapacirani nameštaj), procenat je 5.5% (cena * 0.055).
                2. Ako je tip artikla Ploča (ili pločasti materijal), procenat je 2.4% (cena * 0.024).
                3. Ako je tip artikla Dušek, procenat je 1.2% (cena * 0.012).
                
                Prikaži rezultat u obliku uredne tabele sa kolonama: Artikal, Cena, Tip Posla, Moja Zarada.
                Na samom kraju, masnim slovima ispiši: 'UKUPNA ZARADA: [Suma svih zarada] rsd'.
                Obrati pažnju na tačnost brojeva. Odgovori isključivo na srpskom jeziku.
                """
                
                response = model.generate_content([uputstvo, slika])
                st.success('Završeno!')
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Došlo je do greške: {e}")
