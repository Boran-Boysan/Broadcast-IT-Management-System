function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} özelliği yakında eklenecek!`);
        }

        function confirmDelete() {
            return confirm('{{ employee.name }} {{ employee.surname }} adlı çalışanı silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz ve tüm veriler silinecektir!');
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

        // Copy email to clipboard
        document.addEventListener('DOMContentLoaded', function() {
            const emailElement = document.querySelector('[data-email]');
            if (emailElement) {
                emailElement.style.cursor = 'pointer';
                emailElement.title = 'E-postayı kopyalamak için tıklayın';

                emailElement.addEventListener('click', function() {
                    navigator.clipboard.writeText('{{ employee.email }}').then(() => {
                        alert('E-posta adresi kopyalandı!');
                    });
                });
            }
        });

        // Add copy functionality to email
        const emailSpan = document.querySelector('.info-card p:nth-child(2) span');
        if (emailSpan) {
            emailSpan.setAttribute('data-email', '{{ employee.email }}');
            emailSpan.style.cursor = 'pointer';
            emailSpan.title = 'E-postayı kopyalamak için tıklayın';
        }