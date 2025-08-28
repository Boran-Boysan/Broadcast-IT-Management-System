// Çeviri metinleri
const translations = {
    tr: {
        'page-title': '⚙️ Ayarlar',
        'page-subtitle': 'Kişiselleştirme ve tercihler',
        'back-text': 'Dashboard\'a Dön',
        'dark-mode-title': 'Karanlık Mod',
        'dark-mode-desc': 'Gözlerinizi koruyun ve batarya tasarrufu yapın',
        'language-title': 'Dil Seçimi',
        'language-desc': 'Site dilini değiştirin',
        'additional-title': 'Ek Ayarlar',
        'additional-desc': 'Gelişmiş özellikler ve tercihler',
        'notifications-label': 'Bildirimler',
        'notifications-desc': 'Push bildirimleri alın',
        'animations-label': 'Animasyonlar',
        'animations-desc': 'Sayfa geçiş animasyonları',
        'autosave-label': 'Otomatik Kaydet',
        'autosave-desc': 'Değişiklikleri otomatik kaydet',
        'status-title': 'Sistem Durumu',
        'status-desc': 'Geçerli ayarlar ve sistem bilgisi',
        'theme-status': 'Tema:',
        'lang-status': 'Dil:',
        'save-status': 'Son Kayıt:',
        'current-theme-light': 'Açık Mod',
        'current-theme-dark': 'Karanlık Mod',
        'current-lang': 'Türkçe',
        'last-save': 'Az önce',
        'save-btn': '💾 Ayarları Kaydet'
    },
    en: {
        'page-title': '⚙️ Settings',
        'page-subtitle': 'Personalization and preferences',
        'back-text': 'Back to Dashboard',
        'dark-mode-title': 'Dark Mode',
        'dark-mode-desc': 'Protect your eyes and save battery',
        'language-title': 'Language Selection',
        'language-desc': 'Change site language',
        'additional-title': 'Additional Settings',
        'additional-desc': 'Advanced features and preferences',
        'notifications-label': 'Notifications',
        'notifications-desc': 'Receive push notifications',
        'animations-label': 'Animations',
        'animations-desc': 'Page transition animations',
        'autosave-label': 'Auto Save',
        'autosave-desc': 'Automatically save changes',
        'status-title': 'System Status',
        'status-desc': 'Current settings and system information',
        'theme-status': 'Theme:',
        'lang-status': 'Language:',
        'save-status': 'Last Save:',
        'current-theme-light': 'Light Mode',
        'current-theme-dark': 'Dark Mode',
        'current-lang': 'English',
        'last-save': 'Just now',
        'save-btn': '💾 Save Settings'
    }
};

// Varsayılan ayarlar
let currentLang = 'tr';
let currentTheme = 'light';

// DOM elementleri
const darkModeToggle = document.getElementById('dark-mode-toggle');
const languageOptions = document.querySelectorAll('.language-option');
const saveBtn = document.getElementById('save-btn');
const backToDashboard = document.getElementById('back-to-dashboard');

// Dashboard'a dön butonu
if (backToDashboard) {
    backToDashboard.addEventListener('click', function(e) {
        e.preventDefault();

        // Animasyon efekti
        this.style.transform = 'scale(0.95)';
        this.style.opacity = '0.8';

        setTimeout(() => {
            // Dashboard URL'ini dinamik olarak oluştur
            const dashboardUrl = '/admin/dashboard'; // veya Flask route'unuza göre ayarlayın
            window.location.href = dashboardUrl;
        }, 150);
    });
}

// Dark mode toggle
if (darkModeToggle) {
    darkModeToggle.addEventListener('change', function() {
        currentTheme = this.checked ? 'dark' : 'light';
        document.body.setAttribute('data-theme', currentTheme);
        updateThemeStatus();
        showSaveNotification();

        // Body class güncellemesi (CSS ile uyumlu)
        if (currentTheme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    });
}

// Dil değiştirme
languageOptions.forEach(option => {
    option.addEventListener('click', function() {
        // Aktif sınıfı güncelle
        languageOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');

        // Dili değiştir
        currentLang = this.getAttribute('data-lang');
        translatePage();
        updateLangStatus();
        showSaveNotification();

        // Butona tıklama efekti
        this.style.transform = 'scale(0.98)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
    });
});

// Sayfa çevirisi
function translatePage() {
    const texts = translations[currentLang];

    Object.keys(texts).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            if (id === 'back-text') {
                // Back button için özel işlem
                element.innerHTML = `<i class="fas fa-arrow-left"></i> ${texts[id]}`;
            } else {
                element.textContent = texts[id];
            }
        }
    });

    // Özel durumlar
    updateThemeStatus();
    updateLangStatus();
}

// Tema durumu güncelleme
function updateThemeStatus() {
    const themeText = document.getElementById('current-theme');
    if (themeText) {
        const themeKey = currentTheme === 'dark' ? 'current-theme-dark' : 'current-theme-light';
        themeText.textContent = translations[currentLang][themeKey];
    }
}

// Dil durumu güncelleme
function updateLangStatus() {
    const langText = document.getElementById('current-lang');
    if (langText) {
        langText.textContent = translations[currentLang]['current-lang'];
    }
}

// Kaydetme bildirimi
function showSaveNotification() {
    const lastSaveElement = document.getElementById('last-save');
    if (lastSaveElement) {
        lastSaveElement.textContent = translations[currentLang]['last-save'];

        // Animasyon efekti
        lastSaveElement.style.color = '#28a745';
        lastSaveElement.style.fontWeight = '600';

        setTimeout(() => {
            lastSaveElement.style.color = '';
            lastSaveElement.style.fontWeight = '';
        }, 1500);
    }

    // Toast notification göster
    showToastNotification(
        currentLang === 'tr' ? 'Ayarlar güncellendi' : 'Settings updated',
        'success'
    );
}

// Toast notification fonksiyonu
function showToastNotification(message, type = 'success') {
    // Varolan toast'ları temizle
    const existingToasts = document.querySelectorAll('.settings-toast');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `settings-toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close">&times;</button>
    `;

    // CSS stilleri ekle
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
        color: ${type === 'success' ? '#155724' : '#721c24'};
        border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
        border-left: 4px solid ${type === 'success' ? '#28a745' : '#dc3545'};
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 300px;
        max-width: 400px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;

    document.body.appendChild(toast);

    // Animasyon ile göster
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);

    // Close button event
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        margin-left: 15px;
        opacity: 0.7;
    `;

    closeBtn.addEventListener('click', () => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    });

    // Otomatik kapanma
    setTimeout(() => {
        if (document.body.contains(toast)) {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 3000);
}

// Kaydet butonu
if (saveBtn) {
    saveBtn.addEventListener('click', function() {
        // Butona basılma animasyonu
        this.style.transform = 'scale(0.95)';

        // Ayarları local storage'a kaydet
        const settings = {
            theme: currentTheme,
            language: currentLang,
            notifications: document.getElementById('notifications-toggle')?.checked || false,
            animations: document.getElementById('animations-toggle')?.checked || false,
            autosave: document.getElementById('autosave-toggle')?.checked || false,
            timestamp: new Date().getTime()
        };

        try {
            localStorage.setItem('siteSettings', JSON.stringify(settings));

            // Başarı efekti
            const originalBg = this.style.background;
            const originalText = this.textContent;

            this.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            this.textContent = currentLang === 'tr' ? '✅ Kaydedildi!' : '✅ Saved!';

            setTimeout(() => {
                this.style.background = originalBg;
                this.textContent = originalText;
                this.style.transform = 'scale(1)';
            }, 2000);

            showSaveNotification();

            // Sayfayı yenile efekti (opsiyonel)
            // setTimeout(() => window.location.reload(), 1000);

        } catch (error) {
            console.error('Ayarlar kaydedilirken hata:', error);
            showToastNotification(
                currentLang === 'tr' ? 'Ayarlar kaydedilemedi' : 'Failed to save settings',
                'error'
            );
        }
    });
}

// Sayfa yüklendiğinde ayarları yükle
window.addEventListener('DOMContentLoaded', function() {
    try {
        const savedSettings = localStorage.getItem('siteSettings');

        if (savedSettings) {
            const settings = JSON.parse(savedSettings);

            // Tema ayarı
            if (settings.theme) {
                currentTheme = settings.theme;
                document.body.setAttribute('data-theme', currentTheme);
                if (darkModeToggle) {
                    darkModeToggle.checked = currentTheme === 'dark';
                }

                // Body class güncellemesi
                if (currentTheme === 'dark') {
                    document.body.classList.add('dark-mode');
                } else {
                    document.body.classList.remove('dark-mode');
                }
            }

            // Dil ayarı
            if (settings.language) {
                currentLang = settings.language;
                languageOptions.forEach(opt => {
                    opt.classList.remove('active');
                    if (opt.getAttribute('data-lang') === currentLang) {
                        opt.classList.add('active');
                    }
                });
                translatePage();
            }

            // Diğer ayarlar
            if (typeof settings.notifications !== 'undefined') {
                const notificationsToggle = document.getElementById('notifications-toggle');
                if (notificationsToggle) {
                    notificationsToggle.checked = settings.notifications;
                }
            }
            if (typeof settings.animations !== 'undefined') {
                const animationsToggle = document.getElementById('animations-toggle');
                if (animationsToggle) {
                    animationsToggle.checked = settings.animations;
                }
            }
            if (typeof settings.autosave !== 'undefined') {
                const autosaveToggle = document.getElementById('autosave-toggle');
                if (autosaveToggle) {
                    autosaveToggle.checked = settings.autosave;
                }
            }
        }
    } catch (error) {
        console.error('Ayarlar yüklenirken hata:', error);
    }

    updateThemeStatus();
    updateLangStatus();

    // Sayfa yükleme animasyonu
    const settingsCards = document.querySelectorAll('.setting-card');
    settingsCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Diğer toggle'lar için değişiklik dinleyicileri
document.querySelectorAll('input[type="checkbox"]:not(#dark-mode-toggle)').forEach(toggle => {
    toggle.addEventListener('change', function() {
        showSaveNotification();

        // Toggle animasyonu
        const parent = this.closest('.setting-item');
        if (parent) {
            parent.style.transform = 'scale(0.98)';
            setTimeout(() => {
                parent.style.transform = 'scale(1)';
            }, 100);
        }
    });
});

// Klavye kısayolları
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S ile kaydet
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (saveBtn) {
            saveBtn.click();
        }
    }

    // Escape ile dashboard'a dön
    if (e.key === 'Escape' && backToDashboard) {
        backToDashboard.click();
    }
});

// Window blur/focus olayları için ayar senkronizasyonu
window.addEventListener('focus', function() {
    // Sayfa odaklandığında ayarları kontrol et
    const savedSettings = localStorage.getItem('siteSettings');
    if (savedSettings) {
        try {
            const settings = JSON.parse(savedSettings);
            if (settings.timestamp && settings.timestamp > (Date.now() - 60000)) {
                // Son 1 dakikada güncellenmiş ayarlar varsa göster
                showToastNotification(
                    currentLang === 'tr' ? 'Ayarlar senkronize edildi' : 'Settings synchronized',
                    'success'
                );
            }
        } catch (error) {
            console.error('Ayar senkronizasyonu hatası:', error);
        }
    }
});