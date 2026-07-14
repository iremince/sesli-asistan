import os
import json
from datetime import datetime
import time
import sounddevice as sd
import numpy as np
import keyboard
import scipy.io.wavfile as wavfile
from faster_whisper import WhisperModel
from google import genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SAMPLE_RATE = 16000
GECICI_SES_DOSYASI = "kayit.wav"
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

print("Whisper modeli yükleniyor...")
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

gemini_client = genai.Client()

print("✅ Hazırlık tamamlandı.\n")

def ses_kaydet():
    print("🎙️  Boşluğa BASILI TUT, konuş, BIRAK.")

    kayit_parcalari = []

    def callback(indata, frames, time_info, status):
        kayit_parcalari.append(indata.copy())

    while not keyboard.is_pressed('space'):
        time.sleep(0.01)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16', callback=callback):
        while keyboard.is_pressed('space'):
            time.sleep(0.01)

    if not kayit_parcalari:
        print("⚠️  Hiç ses kaydedilmedi.")
        return None

    ses_verisi = np.concatenate(kayit_parcalari, axis=0)
    wavfile.write(GECICI_SES_DOSYASI, SAMPLE_RATE, ses_verisi)
    sure = len(ses_verisi) / SAMPLE_RATE
    print(f"Kayıt tamamlandı ({sure:.1f} sn)")
    return GECICI_SES_DOSYASI

while not keyboard.is_pressed('space'):
    time.sleep(0.01)


def sesi_metne_cevir(dosya_yolu):
    print("Ses metne çevriliyor...")
    segmentler, _ = whisper_model.transcribe(dosya_yolu, language="tr")
    tam_metin = ""
    for segment in segmentler:
        tam_metin += segment.text
    return tam_metin.strip()


def niyet_analizi_yap(metin):
    print("Metin analiz ediliyor...")

    bugun = datetime.now().strftime("%d %B %Y, %A")

    prompt = f"""
Bugünün tarihi: {bugun}

Aşağıdaki metinden bir takvim etkinliği çıkar.
Metin: "{metin}"

SADECE aşağıdaki formatta JSON döndür, başka hiçbir açıklama ekleme:
{{
  "baslik": "etkinliğin kısa başlığı",
  "tarih": "YYYY-MM-DD formatında",
  "saat": "HH:MM formatında (24 saat)"
}}
"""

    yanit = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    metin_temiz = yanit.text.strip().replace("```json", "").replace("```", "")
    return json.loads(metin_temiz)


def takvim_servisi_olustur():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def takvime_etkinlik_ekle(baslik, tarih, saat):
    servis = takvim_servisi_olustur()

    baslangic = f"{tarih}T{saat}:00"
    saat_int = int(saat.split(":")[0])
    dakika_int = int(saat.split(":")[1])
    bitis_saat = saat_int + 1
    bitis = f"{tarih}T{bitis_saat:02d}:{dakika_int:02d}:00"

    etkinlik = {
        "summary": baslik,
        "start": {"dateTime": baslangic, "timeZone": "Europe/Istanbul"},
        "end": {"dateTime": bitis, "timeZone": "Europe/Istanbul"},
    }

    sonuc = servis.events().insert(calendarId="primary", body=etkinlik).execute()
    print(f"✅ Takvime eklendi: {sonuc.get('htmlLink')}")


def main():
    print("=" * 50)
    print("🎙️  Sesli Asistan")
    print("Boşluğa basılı tutup konuş, bırakınca işlem başlar.")
    print("Çıkmak için ESC'ye bas.")
    print("=" * 50)

    while True:
        if keyboard.is_pressed('esc'):
            print("👋 Çıkılıyor...")
            break

        if keyboard.is_pressed('space'):
            dosya = ses_kaydet()
            if dosya is None:
                continue

            metin = sesi_metne_cevir(dosya)
            print(f"📝 Anlaşılan: {metin}")

            try:
                veri = niyet_analizi_yap(metin)
                takvime_etkinlik_ekle(veri["baslik"], veri["tarih"], veri["saat"])
            except Exception as e:
                print(f"⚠️  Bir hata oluştu: {e}")

            print("\nHazır, tekrar dinlemek için Boşluğa bas.\n")

        time.sleep(0.05)


if __name__ == "__main__":
    main()