function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} özelliği yakında eklenecek!`);
        }

        function confirmDelete() {
            return confirm('{{ equipment.equipment_name }} adlı ekipmanı silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz ve tüm veriler silinecektir!');
        }

        function printEquipmentInfo() {
            // Create a print-friendly version
            const printWindow = window.open('', '_blank');
            const printContent = `
                <html>
                <head>
                    <title>{{ equipment.equipment_name }} - Ekipman Bilgileri</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
                        .info-section { margin-bottom: 25px; }
                        .info-section h3 { background: #f5f5f5; padding: 10px; margin: 0 0 15px 0; }
                        .info-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
                        .info-label { font-weight: bold; }
                        .status { padding: 4px 8px; background: #f0f0f0; border-radius: 4px; }
                        @media print { body { margin: 0; } }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{{ equipment.equipment_name }}</h1>
                        <h2>TRT Broadcast IT - Ekipman Bilgileri</h2>
                        <p>Yazdırma Tarihi: ${new Date().toLocaleDateString('tr-TR')}</p>
                    </div>

                    <div class="info-section">
                        <h3>Temel Bilgiler</h3>
                        <div class="info-item">
                            <span class="info-label">Ekipman ID:</span>
                            <span>#{{ equipment.equipment_id }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Kategori:</span>
                            <span>{{ equipment.category }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Marka:</span>
                            <span>{{ equipment.brand or 'Belirtilmemiş' }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Model:</span>
                            <span>{{ equipment.model or 'Belirtilmemiş' }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Seri No:</span>
                            <span>{{ equipment.serial_number or 'Belirtilmemiş' }}</span>
                        </div>
                    </div>

                    <div class="info-section">
                        <h3>Durum Bilgileri</h3>
                        <div class="info-item">
                            <span class="info-label">Durum:</span>
                            <span class="status">{{ equipment.status_display }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Konum:</span>
                            <span>{{ equipment.location or 'Belirtilmemiş' }}</span>
                        </div>
                        {% if assigned_employee %}
                        <div class="info-item">
                            <span class="info-label">Atanan Kişi:</span>
                            <span>{{ assigned_employee.name }} {{ assigned_employee.surname }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Departman:</span>
                            <span>{{ assigned_employee.department or 'Belirtilmemiş' }}</span>
                        </div>
                        {% endif %}
                    </div>

                    <div class="info-section">
                        <h3>Satın Alma Bilgileri</h3>
                        <div class="info-item">
                            <span class="info-label">Satın Alma Tarihi:</span>
                            <span>{{ equipment.purchase_date.strftime('%d.%m.%Y') if equipment.purchase_date else 'Belirtilmemiş' }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Son Güncelleme:</span>
                            <span>{{ equipment.last_updated.strftime('%d.%m.%Y %H:%M') if equipment.last_updated else 'Belirtilmemiş' }}</span>
                        </div>
                    </div>
                </body>
                </html>
            `;

            printWindow.document.write(printContent);
            printWindow.document.close();
            printWindow.print();
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

        // Copy serial number to clipboard
        document.addEventListener('DOMContentLoaded', function() {
            const serialElement = document.querySelector('.info-value');
            if (serialElement && '{{ equipment.serial_number }}') {
                // Add click-to-copy functionality for serial number
                // This would be implemented when serial number is clicked
            }
        });

        // Auto-refresh equipment status
        function refreshEquipmentStatus() {
            // Fetch updated equipment status
            fetch(`/api/admin/equipment/{{ equipment.equipment_id }}/status`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update status badge if changed
                        console.log('Equipment status updated:', data);
                    }
                })
                .catch(error => console.log('Status refresh failed:', error));
        }

        // Refresh every 30 seconds
        setInterval(refreshEquipmentStatus, 30000);

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'e':
                        e.preventDefault();
                        window.location.href = "{{ url_for('main.admin_edit_equipment', equipment_id=equipment.equipment_id) }}";
                        break;
                    case 'p':
                        e.preventDefault();
                        printEquipmentInfo();
                        break;
                    case 'b':
                        e.preventDefault();
                        window.location.href = "{{ url_for('main.admin_inventory_equipment') }}";
                        break;
                }
            }
        });

        // Show keyboard shortcuts hint
        console.log('Klavye Kısayolları:');
        console.log('Ctrl+E: Düzenle');
        console.log('Ctrl+P: Yazdır');
        console.log('Ctrl+B: Geri Dön');