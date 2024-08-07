import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from supabase import create_client, Client

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

def send_email(to_email, product_url):
    from_email = "kocaibrahim52@gmail.com"
    from_password = "bygialvwvxaxrnar"
    subject = "Zara Ürün Mevcut"
    body = f"İlgilendiğiniz Zara ürünü tekrar stoklarda! Hemen göz atın: {product_url}"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Mail gönderildi: {to_email}")
    except Exception as e:
        print(f"Mail gönderilemedi. Hata: {e}")

def check_product_availability():
    response = supabase.table('maintable').select('*').execute()
    products = response.data

    for product in products:
        product_id = product['id']
        product_url = product['url']
        user_email = product['email']
        available = zara_product_detail(product_url)
        print(available)
        if available:
            send_email(user_email, product_url)
            print(f"Mail gönderildi: {user_email} için {product_url}")
            # Ürünü veritabanından sil
            try:
                supabase.table('maintable').delete().eq('id', product_id).execute()
                print(f"Veritabanından silindi: {product_url}")
            except Exception as e:
                print(f"Veritabanından silinemedi. Hata: {e}")

if __name__ == "__main__":
    while True:
        check_product_availability()
        print("Kontrol tamamlandı, 30 dk bekleniyor...")
        response = supabase.table('maintable').select('*').execute()
        products = response.data
        print(products)

        time.sleep(10*1)  # 30 dk bekle
