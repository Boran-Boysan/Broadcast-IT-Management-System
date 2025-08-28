 function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        function confirmDelete() {
            return confirm('{{ employee.name }} {{ employee.surname }} adlı çalışanı silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz ve tüm veriler silinecektir!');
        }

        // Form validation and interactions
        document.getElementById('editEmployeeForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        });

        // Email validation
        document.getElementById('email').addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (email && !emailRegex.test(email)) {
                this.style.borderColor = '#dc3545';
                this.style.backgroundColor = '#fff5f5';
            } else if (email) {
                this.style.borderColor = '#28a745';
                this.style.backgroundColor = '#f0fff4';
            } else {
                this.style.borderColor = '#e1e5e9';
                this.style.backgroundColor = '#f8f9fa';
            }
        });

        // Password strength indicator
        document.getElementById('new_password').addEventListener('input', function() {
            const password = this.value;
            const strengthDiv = document.getElementById('passwordStrength');

            if (password.length === 0) {
                strengthDiv.style.display = 'none';
                this.style.borderColor = '#e1e5e9';
                this.style.backgroundColor = '#f8f9fa';
                return;
            }

            let strength = getPasswordStrength(password);
            strengthDiv.className = `password-strength ${strength.level}`;
            strengthDiv.textContent = strength.message;

            if (strength.level === 'weak') {
                this.style.borderColor = '#dc3545';
                this.style.backgroundColor = '#fff5f5';
            } else if (strength.level === 'strong') {
                this.style.borderColor = '#28a745';
                this.style.backgroundColor = '#f0fff4';
            } else {
                this.style.borderColor = '#ffc107';
                this.style.backgroundColor = '#fff9c4';
            }
        });

        function getPasswordStrength(password) {
            let score = 0;
            let feedback = [];

            if (password.length >= 8) score++;
            else feedback.push('en az 8 karakter');

            if (/[a-z]/.test(password)) score++;
            else feedback.push('küçük harf');

            if (/[A-Z]/.test(password)) score++;
            else feedback.push('büyük harf');

            if (/[0-9]/.test(password)) score++;
            else feedback.push('rakam');

            if (/[^a-zA-Z0-9]/.test(password)) score++;
            else feedback.push('özel karakter');

            if (score <= 2) {
                return {
                    level: 'weak',
                    message: `Zayıf şifre. Eksik: ${feedback.slice(0, 3).join(', ')}`
                };
            } else if (score <= 3) {
                return {
                    level: 'medium',
                    message: `Orta güçlükte şifre. ${feedback.length > 0 ? 'Eksik: ' + feedback.join(', ') : ''}`
                };
            } else {
                return {
                    level: 'strong',
                    message: 'Güçlü şifre ✓'
                };
            }
        }

        // Name and surname formatting
        function formatName(input) {
            return input.value.charAt(0).toUpperCase() + input.value.slice(1).toLowerCase();
        }

        document.getElementById('name').addEventListener('blur', function() {
            if (this.value) this.value = formatName(this);
        });

        document.getElementById('surname').addEventListener('blur', function() {
            if (this.value) this.value = formatName(this);
        });

        // Mobile sidebar toggle
        function toggleMobileSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('show');
        }

        // Update toggle for mobile
        if (window.innerWidth <= 768) {
            document.querySelector('.toggle-sidebar').onclick = toggleMobileSidebar;
        }

        // Detect changes for unsaved warning
        let originalData = {};
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('editEmployeeForm');
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                originalData[key] = value;
            }
        });

        window.addEventListener('beforeunload', function(e) {
            const form = document.getElementById('editEmployeeForm');
            const currentData = new FormData(form);
            let hasChanges = false;

            for (let [key, value] of currentData.entries()) {
                if (originalData[key] !== value) {
                    hasChanges = true;
                    break;
                }
            }

            if (hasChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Auto-save indication
        let saveTimer;
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(saveTimer);
                this.style.borderColor = '#ffc107';

                saveTimer = setTimeout(() => {
                    this.style.borderColor = '#e1e5e9';
                }, 1000);
            });
        });


// Form element kontrolü
document.addEventListener('DOMContentLoaded', function() {
    // Form'un var olup olmadığını kontrol et
    const form = document.getElementById('editEmployeeForm');
    if (!form) {
        console.error('editEmployeeForm bulunamadı!');
        return;
    }

    // Email alanı kontrolü
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            this.classList.remove('success', 'error');

            if (email && !emailRegex.test(email)) {
                this.classList.add('error');
            } else if (email) {
                this.classList.add('success');
            }
        });
    }

    // Password strength kontrolü
    const passwordInput = document.getElementById('new_password');
    const strengthDiv = document.getElementById('passwordStrength');

    if (passwordInput && strengthDiv) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;

            this.classList.remove('success', 'error');

            if (password.length === 0) {
                strengthDiv.style.display = 'none';
                return;
            }

            let strength = getPasswordStrength(password);
            strengthDiv.className = `password-strength ${strength.level}`;
            strengthDiv.textContent = strength.message;

            if (strength.level === 'weak') {
                this.classList.add('error');
            } else if (strength.level === 'strong') {
                this.classList.add('success');
            }
        });
    }

    // Form submit kontrolü
    form.addEventListener('submit', function(e) {
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        }
    });
});

// Password strength function düzeltmesi
function getPasswordStrength(password) {
    let score = 0;
    let feedback = [];

    if (password.length >= 8) score++;
    else feedback.push('en az 8 karakter');

    if (/[a-z]/.test(password)) score++;
    else feedback.push('küçük harf');

    if (/[A-Z]/.test(password)) score++;
    else feedback.push('büyük harf');

    if (/[0-9]/.test(password)) score++;
    else feedback.push('rakam');

    if (/[^a-zA-Z0-9]/.test(password)) score++;
    else feedback.push('özel karakter');

    if (score <= 2) {
        return {
            level: 'weak',
            message: `⚠️ Zayıf şifre. Eksik: ${feedback.slice(0, 3).join(', ')}`
        };
    } else if (score <= 3) {
        return {
            level: 'medium',
            message: `⚡ Orta güçlükte şifre. ${feedback.length > 0 ? 'Eksik: ' + feedback.join(', ') : 'İyileştirilebilir.'}`
        };
    } else {
        return {
            level: 'strong',
            message: '✅ Güçlü şifre!'
        };
    }
}