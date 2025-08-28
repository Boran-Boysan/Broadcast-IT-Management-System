function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        // Form submission
        document.getElementById('licenseForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        });

        // Vendor preview
        document.getElementById('vendor').addEventListener('change', function() {
            const vendor = this.value;
            const preview = document.getElementById('vendorPreview');

            if (vendor) {
                const vendorInfo = {
                    'Adobe': { icon: 'fab fa-adobe', class: 'adobe', desc: 'Creative Cloud ve Professional Video yazılımları' },
                    'Microsoft': { icon: 'fab fa-microsoft', class: 'microsoft', desc: 'Office, Windows ve Developer araçları' },
                    'Vizrt': { icon: 'fas fa-video', class: 'vizrt', desc: 'Broadcast grafik ve video çözümleri' },
                    'Avid': { icon: 'fas fa-film', class: 'avid', desc: 'Professional video editing ve audio çözümleri' },
                    'Blackmagic': { icon: 'fas fa-camera', class: 'other', desc: 'DaVinci Resolve ve broadcast ekipmanları' },
                    'Other': { icon: 'fas fa-cube', class: 'other', desc: 'Diğer yazılım vendors' }
                };

                const info = vendorInfo[vendor];
                if (info) {
                    preview.innerHTML = `
                        <div class="vendor-icon ${info.class}">
                            <i class="${info.icon}"></i>
                        </div>
                        <span>${info.desc}</span>
                    `;
                    preview.classList.add('show');
                }
            } else {
                preview.classList.remove('show');
            }
        });

        // Expiration date warning
        document.getElementById('expiration_date').addEventListener('change', function() {
            const expiryDate = new Date(this.value);
            const today = new Date();
            const warning = document.getElementById('expiryWarning');

            if (this.value) {
                const diffTime = expiryDate - today;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

                if (diffDays < 0) {
                    warning.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Bu tarih geçmişte! Lisans zaten süresi dolmuş.`;
                    warning.classList.add('show');
                    warning.style.background = '#f8d7da';
                    warning.style.color = '#721c24';
                } else if (diffDays <= 30) {
                    warning.innerHTML = `<i class="fas fa-clock"></i> Uyarı: Bu lisansın süresi ${diffDays} gün içinde dolacak.`;
                    warning.classList.add('show');
                    warning.style.background = '#fff3cd';
                    warning.style.color = '#856404';
                } else {
                    warning.classList.remove('show');
                }
            } else {
                warning.classList.remove('show');
            }
        });

        // Generate sample license key
        function generateSampleKey() {
            const patterns = [
                'XXXX-XXXX-XXXX-XXXX',
                'XXXXX-XXXXX-XXXXX',
                'XXXXXXXX-XXXX-XXXX',
                'XXX-XXXXX-XXXXX-XXX'
            ];

            const pattern = patterns[Math.floor(Math.random() * patterns.length)];
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

            let key = pattern.replace(/X/g, () => chars.charAt(Math.floor(Math.random() * chars.length)));
            key = 'TEST-' + key; // Mark as test key

            document.getElementById('license_key').value = key;
        }

        // License key validation
        document.getElementById('license_key').addEventListener('blur', function() {
            const licenseKey = this.value.trim();
            if (licenseKey) {
                // Here you could add AJAX call to check if license key exists
                console.log('Checking license key uniqueness:', licenseKey);

                // Basic format validation
                if (licenseKey.length < 10) {
                    this.classList.add('error');
                    this.classList.remove('success');
                } else {
                    this.classList.add('success');
                    this.classList.remove('error');
                }
            }
        });

        // Auto-suggest based on software name
        document.getElementById('software_name').addEventListener('input', function() {
            const softwareName = this.value.toLowerCase();
            const vendorSelect = document.getElementById('vendor');

            // Auto-suggest vendor based on software name
            const vendorMappings = {
                'adobe': 'Adobe',
                'premiere': 'Adobe',
                'photoshop': 'Adobe',
                'after effects': 'Adobe',
                'microsoft': 'Microsoft',
                'office': 'Microsoft',
                'windows': 'Microsoft',
                'vizrt': 'Vizrt',
                'avid': 'Avid',
                'media composer': 'Avid',
                'pro tools': 'Avid',
                'davinci': 'Blackmagic',
                'resolve': 'Blackmagic'
            };

            for (const [keyword, vendor] of Object.entries(vendorMappings)) {
                if (softwareName.includes(keyword) && !vendorSelect.value) {
                    vendorSelect.value = vendor;
                    vendorSelect.dispatchEvent(new Event('change'));
                    break;
                }
            }
        });

        // Assignment logic
        document.getElementById('assigned_to').addEventListener('change', function() {
            const equipmentSelect = document.getElementById('equipment_id');

            if (this.value) {
                // If assigned to a person, suggest clearing equipment assignment
                console.log('License assigned to person, consider equipment assignment');
            }
        });

        document.getElementById('equipment_id').addEventListener('change', function() {
            const assignedToSelect = document.getElementById('assigned_to');

            if (this.value) {
                // If assigned to equipment, suggest clearing person assignment
                console.log('License assigned to equipment, consider person assignment');
            }
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

        // Form validation improvements
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('error');
                } else if (this.value.trim()) {
                    this.classList.add('success');
                    this.classList.remove('error');
                }
            });

            input.addEventListener('input', function() {
                this.classList.remove('error', 'success');
            });
        });

        // Copy license key to clipboard
        document.getElementById('license_key').addEventListener('dblclick', function() {
            this.select();
            document.execCommand('copy');

            // Show temporary feedback
            const originalBg = this.style.backgroundColor;
            this.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                this.style.backgroundColor = originalBg;
            }, 500);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'g':
                        e.preventDefault();
                        generateSampleKey();
                        break;
                    case 's':
                        e.preventDefault();
                        document.getElementById('licenseForm').submit();
                        break;
                }
            }
        });

        // Show keyboard shortcuts hint
        console.log('Klavye Kısayolları:');
        console.log('Ctrl+G: Örnek lisans anahtarı oluştur');
        console.log('Ctrl+S: Formu kaydet');
        console.log('Çift tıklama: Lisans anahtarını kopyala');