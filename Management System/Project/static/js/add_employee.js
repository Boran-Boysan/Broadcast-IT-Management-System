function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        // Form validation and interactions
        document.getElementById('employeeForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        });

        // Email validation
        document.getElementById('email').addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (email && !emailRegex.test(email)) {
                this.classList.add('error');
                this.classList.remove('success');
            } else if (email) {
                this.classList.add('success');
                this.classList.remove('error');
            } else {
                this.classList.remove('error', 'success');
            }
        });

        // Password strength indicator
        document.getElementById('password').addEventListener('input', function() {
            const password = this.value;
            const strengthDiv = document.getElementById('passwordStrength');

            if (password.length === 0) {
                strengthDiv.style.display = 'none';
                return;
            }

            let strength = getPasswordStrength(password);
            strengthDiv.className = `password-strength ${strength.level}`;
            strengthDiv.textContent = strength.message;

            if (strength.level === 'weak') {
                this.classList.add('error');
                this.classList.remove('success');
            } else if (strength.level === 'strong') {
                this.classList.add('success');
                this.classList.remove('error');
            } else {
                this.classList.remove('error', 'success');
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

        // Auto-suggest email domain
        document.getElementById('name').addEventListener('input', updateEmailSuggestion);
        document.getElementById('surname').addEventListener('input', updateEmailSuggestion);

        function updateEmailSuggestion() {
            const name = document.getElementById('name').value.toLowerCase();
            const surname = document.getElementById('surname').value.toLowerCase();
            const emailInput = document.getElementById('email');

            if (name && surname && !emailInput.value) {
                emailInput.placeholder = `${name}.${surname}@trt.net.tr`;
            }
        }

        // Mobile sidebar toggle
        function toggleMobileSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('show');
        }

        // Update toggle for mobile
        if (window.innerWidth <= 768) {
            document.querySelector('.toggle-sidebar').onclick = toggleMobileSidebar;
        }

        // Auto-save draft (optional enhancement)
        let draftTimer;
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(draftTimer);
                draftTimer = setTimeout(() => {
                    // Could save draft to localStorage here
                    console.log('Draft saved');
                }, 2000);
            });
        });