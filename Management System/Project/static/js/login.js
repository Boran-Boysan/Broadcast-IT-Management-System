 document.getElementById('loginForm').addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.btn-primary');
            submitBtn.innerHTML = 'Giriş Yapılıyor...';
            submitBtn.disabled = true;
        });

        document.getElementById('username').addEventListener('blur', function() {
            const input = this.value;

            if (input.includes('@')) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

                if (!emailRegex.test(input)) {
                    this.style.borderColor = '#dc3545';
                    this.style.backgroundColor = '#fff5f5';
                } else {
                    this.style.borderColor = '#28a745';
                    this.style.backgroundColor = '#f0fff4';
                }
            } else {
                this.style.borderColor = '#e1e5e9';
                this.style.backgroundColor = '#f8f9fa';
            }
        });

        document.getElementById('password').addEventListener('focus', function() {
            this.style.borderColor = '#667eea';
        });

        document.getElementById('password').addEventListener('blur', function() {
            if (this.value.length > 0) {
                this.style.borderColor = '#28a745';
            } else {
                this.style.borderColor = '#e1e5e9';
            }
        });