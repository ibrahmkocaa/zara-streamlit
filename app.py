import streamlit as st
import json
import os
import re
import requests
from supabase import create_client, Client
from bs4 import BeautifulSoup

# Supabase URL ve Anahtarı (bunları Supabase projenizden alın)
SUPABASE_URL = 'https://ggpakaubpgghwsboiglb.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdncGFrYXVicGdnaHdzYm9pZ2xiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI5MzgwMDEsImV4cCI6MjAzODUxNDAwMX0.HXBPLxmkY5vee65H76iSD08LM9BxQ3CCFFZXUFdauW8'

# Supabase istemcisini oluştur
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def zara_product_detail(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    if soup.find('span', string='TÜKENDİ'):
        return False
    elif soup.find('button', string='Ekle'):
        return True
    else:
        return None

# Function to validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Function to validate URL
def is_valid_url(url):
    try:
        headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
        }
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

st.title('Zara Ürün Kontrol ve Mail Gönderme Uygulaması')

with st.form(key='product_form'):
    product_url = st.text_input('Ürün URL\'sini girin:')
    user_email = st.text_input('Email adresinizi girin:')
    submit_button = st.form_submit_button(label='Kontrol Et')

if submit_button:
    if product_url and user_email:
        if not is_valid_email(user_email):
            st.error("Lütfen geçerli bir email adresi girin.")
        elif not is_valid_url(product_url):
            st.error("Lütfen geçerli bir ürün URL'si girin.")
        else:
            product_available = zara_product_detail(product_url)
            if product_available:
                st.success('Ürün zaten mevcut.')
            else:
                # Supabase'e veriyi kaydet
                data = {'url': product_url, 'email': user_email}
                try:
                    response = supabase.table('maintable').insert(data).execute()
                    st.success('Ürün stokta yok, bilgiler kaydedildi. Ürün stoğa geldiğinde bildirim alacaksınız.')
                except Exception as e:
                    st.error(f'Bir hata oluştu: {e}')
    else:
        st.error("Lütfen geçerli bir URL ve email girin.")
