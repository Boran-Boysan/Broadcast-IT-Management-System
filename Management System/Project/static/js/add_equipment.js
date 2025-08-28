function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        // Form submission
        document.getElementById('equipmentForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        });

        // Category preview
        document.getElementById('category').addEventListener('change', function() {
            const category = this.value;
            const preview = document.getElementById('categoryPreview');

            if (category) {
                const categoryInfo = {
                    'Server': { icon: 'server', class: 'server', desc: 'Sunucu sistemleri ve donanımları' },
                    'Switch': { icon: 'network-wired', class: 'switch', desc: 'Ağ anahtarlama cihazları' },
                    'PC': { icon: 'desktop', class: 'pc', desc: 'Masaüstü bilgisayarlar' },
                    'Laptop': { icon: 'laptop', class: 'laptop', desc: 'Taşınabilir bilgisayarlar' },
                    'Monitor': { icon: 'tv', class: 'monitor', desc: 'Monitör ve ekran cihazları' },
                    'Camera': { icon: 'video', class: 'camera', desc: 'Kamera ve görüntü cihazları' },
                    'Storage': { icon: 'hdd', class: 'storage', desc: 'Depolama cihazları' },
                    'Network': { icon: 'wifi', class: 'network', desc: 'Ağ ekipmanları' },
                    'Audio': { icon: 'volume-up', class: 'audio', desc: 'Ses ekipmanları' },
                    'Video': { icon: 'play-circle', class: 'video', desc: 'Video ekipmanları' },
                    'Other': { icon: 'cube', class: 'other', desc: 'Diğer ekipmanlar' }
                };

                const info = categoryInfo[category];
                if (info) {
                    preview.innerHTML = `
                        <div class="category-icon ${info.class}">
                            <i class="fas fa-${info.icon}"></i>
                        </div>
                        <span>${info.desc}</span>
                    `;
                    preview.classList.add('show');
                }
            } else {
                preview.classList.remove('show');
            }
        });

        // Status info
        document.getElementById('status').addEventListener('change', function() {
            const status = this.value;
            const statusInfo = document.getElementById('statusInfo');

            const statusTexts = {
                'in_stock': 'Ekipman depoda/stokta bekliyor ve kullanıma hazır.',
                'in_use': 'Ekipman aktif olarak bir çalışana atanmış ve kullanılıyor.',
                'under_repair': 'Ekipman arızalı ve tamir sürecinde.',
                'scrap': 'Ekipman kullanım dışı ve hurdaya çıkarılmış.'
            };

            if (status && statusTexts[status]) {
                statusInfo.textContent = statusTexts[status];
                statusInfo.classList.add('show');
            } else {
                statusInfo.classList.remove('show');
            }
        });

        // Serial number validation
        document.getElementById('serial_number').addEventListener('blur', function() {
            const serialNumber = this.value.trim();
            if (serialNumber) {
                // Here you could add AJAX call to check if serial number exists
                console.log('Checking serial number:', serialNumber);
            }
        });

        // Auto-fill suggestions based on brand
        document.getElementById('brand').addEventListener('input', function() {
            const brand = this.value.toLowerCase();
            const modelInput = document.getElementById('model');

            // Common models for popular brands
            const brandModels = {
                'dell': ['OptiPlex', 'PowerEdge', 'Latitude'],
                'hp': ['EliteBook', 'ProLiant', 'EliteDesk'],
                'cisco': ['Catalyst', 'ASR', 'ISR'],
                'lenovo': ['ThinkPad', 'ThinkCentre', 'IdeaPad'],
                'apple': ['MacBook', 'iMac', 'Mac Pro']
            };

            if (brandModels[brand] && !modelInput.value) {
                modelInput.placeholder = `Örn: ${brandModels[brand].join(', ')}`;
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