f// Tab switching functionality - KRİTİK: Bu fonksiyon çalışmazsa lisanslar görünmez
        function switchTab(tabName, element) {
            console.log('Switching to tab:', tabName); // Debug için

            // Hide all tab contents
            const allTabs = document.querySelectorAll('.tab-content');
            allTabs.forEach(tab => {
                tab.classList.remove('active');
                tab.style.display = 'none'; // Ekstra güvenlik
            });

            // Remove active class from all nav tabs
            const allNavTabs = document.querySelectorAll('.nav-tab');
            allNavTabs.forEach(nav => {
                nav.classList.remove('active');
            });

            // Show selected tab content
            const targetTab = document.getElementById(tabName + '-tab');
            if (targetTab) {
                targetTab.classList.add('active');
                targetTab.style.display = 'block'; // Ekstra güvenlik
                console.log('Tab activated:', tabName); // Debug için
            } else {
                console.error('Tab not found:', tabName + '-tab'); // Debug için
            }

            // Add active class to clicked nav tab
            element.classList.add('active');
        }

        // Toggle sidebar function
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        // Show coming soon modal
        function showComingSoon(feature) {
            alert(feature + ' özelliği yakında eklenecek!');
        }

        // Initialize page - KRİTİK: Sayfa yüklendiğinde combined view aktif olmalı
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded - Initializing combined view');

            // Combined tab'ı kesinlikle aktif yap
            const combinedTab = document.getElementById('combined-tab');
            const equipmentTab = document.getElementById('equipment-tab');
            const licensesTab = document.getElementById('licenses-tab');

            if (combinedTab) {
                combinedTab.classList.add('active');
                combinedTab.style.display = 'block';
                console.log('Combined tab activated');
            }

            if (equipmentTab) {
                equipmentTab.classList.remove('active');
                equipmentTab.style.display = 'none';
            }

            if (licensesTab) {
                licensesTab.classList.remove('active');
                licensesTab.style.display = 'none';
            }

            // Nav tab'ı da güncelle
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));

            const combinedNavTab = document.querySelector('.nav-tab[onclick*="combined"]');
            if (combinedNavTab) {
                combinedNavTab.classList.add('active');
                console.log('Combined nav tab activated');
            }
        });

        // Test function - Konsola yazdır
        function testTabs() {
            console.log('Testing tabs...');
            const combined = document.getElementById('combined-tab');
            const equipment = document.getElementById('equipment-tab');
            const licenses = document.getElementById('licenses-tab');

            console.log('Combined tab:', combined ? 'FOUND' : 'NOT FOUND');
            console.log('Equipment tab:', equipment ? 'FOUND' : 'NOT FOUND');
            console.log('Licenses tab:', licenses ? 'FOUND' : 'NOT FOUND');

            if (combined) {
                console.log('Combined classes:', combined.className);
                console.log('Combined display:', combined.style.display);
            }
        }

        // Debug için - 2 saniye sonra test yap
        setTimeout(testTabs, 2000);