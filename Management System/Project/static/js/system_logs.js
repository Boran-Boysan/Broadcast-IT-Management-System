function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('show');
        }

        function applyFilters() {
            const userFilter = document.getElementById('userFilter').value;
            const actionFilter = document.getElementById('actionFilter').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            // Filtre uygulama mantığı
            console.log('Filtreler uygulanıyor:', {
                user: userFilter,
                action: actionFilter,
                startDate,
                endDate
            });

            // Burada AJAX ile backend'e filtre parametreleri gönderilir
        }

        function clearFilters() {
            document.getElementById('userFilter').value = '';
            document.getElementById('actionFilter').value = '';
            document.getElementById('startDate').value = '';
            document.getElementById('endDate').value = '';

            // Filtreleri temizle ve tabloyu yenile
            console.log('Filtreler temizlendi');
        }

        function exportLogs() {
            // Log verilerini CSV veya Excel formatında dışa aktarma
            console.log('Loglar dışa aktarılıyor...');

            // Örnek CSV export
            const csvContent = "data:text/csv;charset=utf-8," +
                "Tarih,Kullanıcı,İşlem,Açıklama,IP,Durum\n" +
                "06.08.2025 14:30:25,Admin,Ekipman Güncelleme,TRT Server 01 güncellendi,192.168.1.100,Başarılı\n";

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "sistem_loglari_" + new Date().toISOString().split('T')[0] + ".csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        // Mobil uyumluluk
        if (window.innerWidth <= 768) {
            document.querySelector('.toggle-sidebar').addEventListener('click', function() {
                const sidebar = document.getElementById('sidebar');
                sidebar.classList.toggle('show');
            });
        }

        // Sayfa yüklendiğinde bugünün tarihini varsayılan olarak ayarla
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('endDate').value = today;

            // 7 gün öncesini başlangıç tarihi olarak ayarla
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            document.getElementById('startDate').value = weekAgo.toISOString().split('T')[0];
        });