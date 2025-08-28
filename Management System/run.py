import subprocess
import time
import os
import sys
import signal
import atexit
from Project import create_app

# Global değişkenler
dash_process = None
flask_app = None


def start_dash_dashboard():
    """Dash dashboard'ını ayrı process olarak başlat"""
    global dash_process

    try:
        dash_file_path = os.path.join(os.getcwd(), 'dash_dashboard.py')

        if not os.path.exists(dash_file_path):
            print("⚠️ dash_dashboard.py dosyası bulunamadı!")
            return False

        print("🚀 Dash Dashboard başlatılıyor...")

        # Dash process'ini başlat
        dash_process = subprocess.Popen([
            sys.executable, dash_file_path
        ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Dashboard'ın başlaması için kısa bir süre bekle
        time.sleep(3)

        # Process durumunu kontrol et
        if dash_process.poll() is None:
            print("✅ Dash Dashboard başarıyla başlatıldı!")
            print("📊 Dashboard: http://localhost:8050")
            return True
        else:
            stdout, stderr = dash_process.communicate()
            print(f"❌ Dash Dashboard başlatılamadı!")
            print(f"Stdout: {stdout.decode()}")
            print(f"Stderr: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"❌ Dashboard başlatma hatası: {e}")
        return False


def cleanup():
    """Uygulama kapatılırken temizlik yap"""
    global dash_process

    if dash_process and dash_process.poll() is None:
        print("\n🛑 Dash Dashboard kapatılıyor...")
        try:
            dash_process.terminate()
            dash_process.wait(timeout=5)
            print("✅ Dashboard başarıyla kapatıldı")
        except subprocess.TimeoutExpired:
            print("⚠️ Dashboard zorla kapatılıyor...")
            dash_process.kill()
        except Exception as e:
            print(f"⚠️ Dashboard kapatma hatası: {e}")


def signal_handler(signum, frame):
    """Sinyal yakalandığında temizlik yap"""
    print(f"\n🔔 Sinyal alındı: {signum}")
    cleanup()
    sys.exit(0)


def main():
    global flask_app

    print("=" * 60)
    print("🎯 TRT Broadcast IT Management System")
    print("=" * 60)

    # Temizlik fonksiyonunu kaydet
    atexit.register(cleanup)

    # Sinyal handler'ları kaydet
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Dash Dashboard'ı başlat
    dashboard_started = start_dash_dashboard()

    if dashboard_started:
        print("✅ Dashboard servisi hazır")
    else:
        print("⚠️ Dashboard servisi başlatılamadı, sadece ana uygulama çalışacak")

    # Flask uygulamasını oluştur
    flask_app = create_app()

    print("\n🌐 Ana uygulama başlatılıyor...")
    print("🔗 Ana Uygulama: http://localhost:5000")

    if dashboard_started:
        print("📊 Dashboard: http://localhost:8050")

    print("\n📋 Kullanılabilir Özellikler:")
    print("  • Personel Yönetimi")
    print("  • Donanım Takibi")
    print("  • Lisans Yönetimi")
    print("  • Raporlama")
    if dashboard_started:
        print("  • Analytics Dashboard (Ayrı port)")
    print("\n🔄 Durdurmak için Ctrl+C tuşlarına basın")
    print("-" * 60)

    try:
        # Flask uygulamasını çalıştır
        flask_app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Reloader'ı kapat çünkü subprocess'lerimiz var
        )
    except KeyboardInterrupt:
        print("\n👋 Uygulama kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Flask uygulama hatası: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()