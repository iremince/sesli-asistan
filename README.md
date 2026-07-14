# sesli-asistan
Sesli Asistan — Konuşarak Takvime Etkinlik Ekleme

Bilgisayarında çalışan, sesli komutlarla Google Takvim'ine otomatik etkinlik ekleyen bir Python projesi. Boşluk tuşuna basılı tutup doğal bir cümleyle konuşuyorsun, gerisini yapay zeka hallediyor.

# Nasıl Çalışıyor?

Boşluğa bas, konuş, bırak
        ↓
        
faster-whisper ile ses → Türkçe metin
        ↓
        
Gemini ile metinden başlık / tarih / saat çıkarma
        ↓
        
Google Calendar API ile otomatik etkinlik ekleme



Örnek kullanım:


"Haftaya salı günü saat 14:00'te proje çalışması yapalım"



→ Google Takvim'inde otomatik olarak 21 Temmuz Salı, 14:00 - proje çalışması etkinliği oluşturulur, telefonuna da anında senkronize olur.

Kullanılan Teknolojiler


faster-whisper — hızlı ses-metin dönüşümü
Google Gemini API — doğal dilden yapılandırılmış veri (JSON) çıkarma
Google Calendar API — otomatik takvim entegrasyonu
sounddevice / keyboard — push-to-talk (basılı tut-konuş) ses kaydı



# Kurulum

1. Kütüphaneleri kur

bashpip install sounddevice numpy keyboard scipy faster-whisper google-genai google-auth-oauthlib google-api-python-client

2. Gemini API anahtarı al

Google AI Studio üzerinden ücretsiz bir API anahtarı oluştur, ortam değişkeni olarak tanımla:

powershell# Windows (PowerShell) - kalıcı olması için Sistem Ortam Değişkenleri'nden de eklenebilir
$env:GEMINI_API_KEY="senin-api-anahtarin"

3. Google Calendar API kimlik bilgisi al


Google Cloud Console üzerinden yeni bir proje oluştur
Google Calendar API'yi etkinleştir
OAuth consent screen'i "External" olarak ayarla, kendi email'ini "Test users" olarak ekle
Credentials > Create Credentials > OAuth Client ID > Desktop app ile bir kimlik oluştur
İndirilen JSON dosyasını credentials.json olarak yeniden adlandırıp proje klasörüne koy


4. Çalıştır

bashpython sesli_asistan.py

İlk çalıştırmada tarayıcı üzerinden Google hesabınla giriş yapıp takvim erişimine izin vermen istenecek

⚠️ Güvenlik Notu

credentials.json ve token.json dosyaları kişisel kimlik bilgilerini içerir, asla paylaşmayın veya GitHub'a yüklemeyin


Lisans

Bu proje kişisel/eğitim amaçlı geliştirilmiştir.
