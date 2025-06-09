import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import nltk
from transformers import pipeline
import re
import requests
import os


#   cd InNews                      python -m streamlit run App.py
# Gerekli kütüphaneleri indir
nltk.download('punkt')

# Sayfa ayarları
st.set_page_config(
    page_title='InNews 🇹🇷 - Özetlenmiş Haber Platformu',
    page_icon='./Meta/newspaper.ico',
    layout="centered"
)

# Sayfa stil ayarları (renkler ve fontlar)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #004e92, #000428);
        color: white;
    }
    .title {
        font-size: 45px;
        font-weight: bold;
        text-align: center;
        color: #FFD700;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.5);
        margin-top: 20px;
    }
    .publish-date {
        color: #00FF00;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Özetleme modeli
ozetleyici = pipeline("summarization")

# Haber RSS kaynaklarını çekme
def haberleri_getir_kategoriye_gore(kategori):
    url = f'https://news.google.com/news/rss/headlines/section/topic/{kategori}'
    sayfa = urlopen(url).read()
    veri = soup(sayfa, 'xml')
    return veri.find_all('item')

def haberleri_getir_aranan_konu(konu):
    url = f'https://news.google.com/rss/search?q={konu}'
    sayfa = urlopen(url).read()
    veri = soup(sayfa, 'xml')
    return veri.find_all('item')

def haberleri_getir_trending():
    url = 'https://news.google.com/news/rss'
    sayfa = urlopen(url).read()
    veri = soup(sayfa, 'xml')
    return veri.find_all('item')

# Haber başlığına göre uygun görseli göster
def kategori_gorseli_goster(kategori):
    try:
        kategori = kategori.lower()
        dosya_yolu = f'./Meta/{kategori}.jpg'
        if os.path.exists(dosya_yolu):
            st.image(dosya_yolu, use_container_width=False)
        else:
            st.image('./Meta/default_news.jpg', use_container_width=False)
    except Exception as e:
        st.error(f"Görsel yüklenemedi: {e}")

# Temizlik ve özetleme
def metin_temizle(metin):
    metin = re.sub(r'<.*?>', '', metin)
    metin = re.sub(r'\d+', '', metin)
    metin = re.sub(r'[^\w\s]', '', metin)
    metin = re.sub(r'\s+', ' ', metin)
    return metin

def metni_ozetle(metin):
    try:
        temiz_metin = metin_temizle(metin)
        ozet = ozetleyici(temiz_metin, max_length=150, min_length=50, do_sample=False)
        return ozet[0]['summary_text']
    except Exception as e:
        st.error(f"Özetleme hatası: {e}")
        return None

# Haberleri ekrana yazdır
def haberleri_goster(haber_listesi, adet, kategori='default'):
    sayac = 0
    for haber in haber_listesi:
        sayac += 1
        st.write(f'### ({sayac}) {haber.title.text}')
        
        kategori_gorseli_goster(kategori)

        makale = Article(haber.link.text)
        try:
            makale.download()
            makale.parse()
            makale.nlp()
        except Exception as e:
            st.error(f"Haber analiz hatası: {e}")
            continue

        with st.expander(haber.title.text):
            st.markdown(f'<p style="text-align: justify; font-size: 16px;">{makale.summary}</p>', unsafe_allow_html=True)
            st.markdown(f"[Haberi Tamamını Oku]({haber.link.text})")
        st.markdown(f'<p class="publish-date">Yayın Tarihi: {haber.pubDate.text}</p>', unsafe_allow_html=True)

        if sayac >= adet:
            break

# Ana uygulama
def calistir():
    st.markdown('<h1 class="title"> InNews: Özetlenmiş Haber Platformu</h1>', unsafe_allow_html=True)
    st.image("Meta/newspaper.jpg")
    st.markdown("---")

    secenekler = ['--Kategori Seç--', ' Gündem Haberleri', ' Favori Konularım', ' Konu Ara', ' Metin Özetle']
    secim = st.selectbox("Bir kategori seçin:", secenekler)

    if secim == secenekler[0]:
        st.warning("Lütfen bir kategori seçin!")

    elif secim == secenekler[1]:
        st.subheader(" Gündem Haberleri")
        adet = st.slider('Kaç haber gösterilsin?', min_value=5, max_value=25, step=1)
        haberler = haberleri_getir_trending()
        haberleri_goster(haberler, adet, kategori="Trending")

    elif secim == secenekler[2]:
        konular = ['Birini Seçin', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        st.subheader(" Favori Konunuzu Seçin")
        secilen_konu = st.selectbox("Konu Seçin", konular)
        if secilen_konu != konular[0]:
            adet = st.slider('Kaç haber gösterilsin?', min_value=5, max_value=25, step=1)
            haberler = haberleri_getir_kategoriye_gore(secilen_konu)
            haberleri_goster(haberler, adet, kategori=secilen_konu)

    elif secim == secenekler[3]:
        arama = st.text_input(" Aramak istediğiniz konuyu yazın:")
        adet = st.slider('Kaç haber gösterilsin?', min_value=5, max_value=15, step=1)
        if st.button("Ara") and arama:
            haberler = haberleri_getir_aranan_konu(arama)
            haberleri_goster(haberler, adet, kategori=arama)

    elif secim == secenekler[4]:
        st.subheader(" Metin Girin ve Özetleyin")
        metin = st.text_area("Metni buraya yapıştırın", height=300)
        if st.button("Özetle"):
            ozet = metni_ozetle(metin)
            if ozet:
                st.write("### Özet:")
                st.success(ozet)

# Uygulamayı çalıştır
calistir()
