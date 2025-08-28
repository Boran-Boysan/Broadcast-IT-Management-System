function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} özelliği yakında eklenecek!`);
        }

        function confirmDeleteLicense(licenseName) {
            return confirm(`"${licenseName}" lisansını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!`);
        }

        function toggleLicenseKey(element) {
            element.classList.toggle('masked');

            if (!element.classList.contains('masked')) {
                // Show full license key (in real implementation, this would fetch from server)
                const originalText = element.textContent;
                setTimeout(() => {
                    element.classList.add('masked');
                }, 3000); // Hide again after 3 seconds
            }
        }

        function showLicenseDetails(licenseId) {
            const modal = document.getElementById('licenseModal');
            const content = document.getElementById('licenseModalContent');

            // In real implementation, fetch license details from server
            content.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #17a2b8;"></i>
                    <p style="margin-top: 10px;">Lisans detayları yükleniyor...</p>
                </div>
            `;

            modal.style.display = 'block';

            // Simulate loading
            setTimeout(() => {
                content.innerHTML = `
                    <div>
                        <h4>Lisans Bilgileri</h4>
                        <p><strong>ID:</strong> ${licenseId}</p>
                        <p><strong>Detaylı görünüm:</strong> Yakında eklenecek</p>
                        <div style="margin-top: 20px; text-align: right;">
                            <button onclick="closeLicenseModal()" class="btn btn-info">Kapat</button>
                        </div>
                    </div>
                `;
            }, 1000);
        }

        function closeLicenseModal() {
            document.getElementById('licenseModal').style.display = 'none';
        }

        // Close modal when clicking outside
        document.getElementById('licenseModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeLicenseModal();
            }
        });

        // Auto-submit form on filter change
        document.getElementById('status').addEventListener('change', function() {
            this.form.submit();
        });

        document.getElementById('vendor').addEventListener('change', function() {
            this.form.submit();
        });

        // Search on Enter
        document.getElementById('search').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.form.submit();
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

        // Highlight search results
        const searchTerm = '{{ search }}';
        if (searchTerm) {
            const cells = document.querySelectorAll('td');
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchTerm.toLowerCase())) {
                    const regex = new RegExp(`(${searchTerm})`, 'gi');
                    if (cell.querySelector('h4')) {
                        const h4 = cell.querySelector('h4');
                        h4.innerHTML = h4.innerHTML.replace(regex, '<mark style="background: #fff3cd; padding: 2px 4px; border-radius: 3px;">$1</mark>');
                    }
                }
            });
        }

        // Check for expiring licenses and show notifications
        document.addEventListener('DOMContentLoaded', function() {
            const expiringLicenses = document.querySelectorAll('.expiry-soon');
            const expiredLicenses = document.querySelectorAll('.expiry-expired');

            if (expiringLicenses.length > 0 || expiredLicenses.length > 0) {
                console.log(`Uyarı: ${expiringLicenses.length} lisansın süresi yaklaşıyor, ${expiredLicenses.length} lisansın süresi dolmuş.`);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'f':
                        e.preventDefault();
                        document.getElementById('search').focus();
                        break;
                    case 'n':
                        e.preventDefault();
                        window.location.href = "{{ url_for('main.admin_add_license') }}";
                        break;
                }
            }
        });

        // Show keyboard shortcuts hint
        console.log('Klavye Kısayolları:');
        console.log('Ctrl+F: Arama kutusuna odaklan');
        console.log('Ctrl+N: Yeni lisans ekle');