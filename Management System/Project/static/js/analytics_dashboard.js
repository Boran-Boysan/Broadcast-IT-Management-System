// Global variables for chart instances
let equipmentChart, categoryChart, licenseChart, departmentChart;

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Analytics Dashboard başlatılıyor...');

    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js library not loaded!');
        showErrorMessage('Chart.js kütüphanesi yüklenemedi. Sayfayı yenileyin.');
        return;
    }

    console.log('✅ Chart.js yüklendi');

    // Add loading indicators
    showLoadingIndicators();

    // Initialize charts with error handling
    setTimeout(() => {
        initializeCharts();
    }, 500);
});

function showLoadingIndicators() {
    const chartContainers = [
        'equipmentStatusChart',
        'categoryChart',
        'licenseStatusChart',
        'departmentChart'
    ];

    chartContainers.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas) {
            const container = canvas.parentElement;
            const originalCanvas = canvas.outerHTML;
            container.innerHTML = `
                <div class="chart-loading" style="display: flex; align-items: center; justify-content: center; height: 300px; color: #999;">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-right: 10px;"></i>
                        <span>Grafik yükleniyor...</span>
                    </div>
                </div>
                ${originalCanvas}
            `;
            canvas.style.display = 'none';
        }
    });
}

function hideLoadingIndicator(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (canvas) {
        const loadingDiv = canvas.parentElement.querySelector('.chart-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
        canvas.style.display = 'block';
    }
}

function initializeCharts() {
    try {
        console.log('🚀 Grafikler başlatılıyor...');

        // Get real data
        const equipmentData = getEquipmentData();
        const categoryData = getCategoryData();
        const licenseData = getLicenseData();
        const departmentData = getDepartmentData();

        console.log('📊 Alınan veriler:', {
            equipment: equipmentData,
            category: categoryData,
            license: licenseData,
            department: departmentData
        });

        // Initialize charts
        initEquipmentStatusChart(equipmentData);
        initCategoryChart(categoryData);
        initLicenseChart(licenseData);
        initDepartmentChart(departmentData);

        console.log('✅ Tüm grafikler başlatıldı');

    } catch (error) {
        console.error('❌ Grafik başlatma hatası:', error);
        showErrorMessage('Grafikler yüklenirken hata oluştu: ' + error.message);
    }
}

function getEquipmentData() {
    try {
        console.log('🔍 Ekipman verisi alınıyor...');

        // 1. Dashboard data script'den al
        const dashboardDataScript = document.getElementById('dashboard-data');
        if (dashboardDataScript) {
            const data = JSON.parse(dashboardDataScript.textContent);
            console.log('📄 Dashboard script verisi:', data.equipment);
            return data.equipment;
        }

        // 2. Meta tag'lerden al
        const totalMeta = document.querySelector('meta[name="equipment-total"]');
        if (totalMeta) {
            console.log('🏷️ Meta tag verisi bulundu');
            return {
                total: parseInt(totalMeta.content) || 0,
                in_use: parseInt(document.querySelector('meta[name="equipment-in-use"]')?.content) || 0,
                in_stock: parseInt(document.querySelector('meta[name="equipment-in-stock"]')?.content) || 0,
                under_repair: parseInt(document.querySelector('meta[name="equipment-under-repair"]')?.content) || 0,
                scrap: parseInt(document.querySelector('meta[name="equipment-scrap"]')?.content) || 0
            };
        }

        // 3. Template'den direkt al (global değişkenler)
        if (typeof window.equipmentStats !== 'undefined') {
            console.log('🌐 Global değişken bulundu:', window.equipmentStats);
            return window.equipmentStats;
        }

        console.log('⚠️ Ekipman verisi bulunamadı, fallback kullanılıyor');

    } catch (error) {
        console.error('❌ Ekipman verisi alma hatası:', error);
    }

    // Fallback - demo data
    return {
        total: 3,
        in_use: 2,
        in_stock: 1,
        under_repair: 0,
        scrap: 0
    };
}

function getCategoryData() {
    try {
        console.log('🔍 Kategori verisi alınıyor...');

        const dashboardDataScript = document.getElementById('dashboard-data');
        if (dashboardDataScript) {
            const data = JSON.parse(dashboardDataScript.textContent);
            if (data.categories && data.categories.length > 0) {
                console.log('📄 Dashboard script kategori verisi:', data.categories);
                return {
                    labels: data.categories.map(cat => cat.name),
                    data: data.categories.map(cat => cat.count)
                };
            }
        }

        console.log('⚠️ Kategori verisi bulunamadı, fallback kullanılıyor');
    } catch (error) {
        console.error('❌ Kategori verisi alma hatası:', error);
    }

    // Fallback - demo data
    return {
        labels: ['PC', 'Server', 'Network'],
        data: [1, 1, 1]
    };
}

function getLicenseData() {
    try {
        console.log('🔍 Lisans verisi alınıyor...');

        const dashboardDataScript = document.getElementById('dashboard-data');
        if (dashboardDataScript) {
            const data = JSON.parse(dashboardDataScript.textContent);
            console.log('📄 Dashboard script lisans verisi:', data.license);
            return data.license;
        }

        console.log('⚠️ Lisans verisi bulunamadı, fallback kullanılıyor');
    } catch (error) {
        console.error('❌ Lisans verisi alma hatası:', error);
    }

    // Fallback - demo data
    return {
        total: 3,
        active: 2,
        expired: 1,
        cancelled: 0,
        expiring_soon: 0
    };
}

function getDepartmentData() {
    try {
        console.log('🔍 Departman verisi alınıyor...');

        const dashboardDataScript = document.getElementById('dashboard-data');
        if (dashboardDataScript) {
            const data = JSON.parse(dashboardDataScript.textContent);
            if (data.departments && data.departments.length > 0) {
                console.log('📄 Dashboard script departman verisi:', data.departments);
                return {
                    labels: data.departments.map(dept => dept.name),
                    data: data.departments.map(dept => dept.count)
                };
            }
        }

        console.log('⚠️ Departman verisi bulunamadı, fallback kullanılıyor');
    } catch (error) {
        console.error('❌ Departman verisi alma hatası:', error);
    }

    // Fallback - demo data
    return {
        labels: ['IT', 'Yayın'],
        data: [2, 1]
    };
}

function initEquipmentStatusChart(data) {
    const canvas = document.getElementById('equipmentStatusChart');
    if (!canvas) {
        console.error('❌ Equipment chart canvas bulunamadı');
        return;
    }

    console.log('📊 Ekipman grafiği oluşturuluyor, veri:', data);

    // Destroy existing chart
    if (equipmentChart) {
        equipmentChart.destroy();
    }

    const ctx = canvas.getContext('2d');

    try {
        // Minimum 1 veri varsa grafik oluştur
        if (data && data.total >= 1) {
            const chartData = [
                data.in_use || 0,
                data.in_stock || 0,
                data.under_repair || 0,
                data.scrap || 0
            ];

            // Eğer hepsi 0 ise toplam değeri kullanımda göster
            if (chartData.every(val => val === 0) && data.total > 0) {
                chartData[0] = data.total;
            }

            equipmentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Kullanımda', 'Stokta', 'Tamirde', 'Hurda'],
                    datasets: [{
                        data: chartData,
                        backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: '#fff',
                            bodyColor: '#fff'
                        }
                    }
                }
            });

            hideLoadingIndicator('equipmentStatusChart');
            console.log('✅ Ekipman grafiği oluşturuldu');

        } else {
            hideLoadingIndicator('equipmentStatusChart');
            showNoDataMessage(canvas.parentElement, 'ekipman');
            console.log('ℹ️ Ekipman verisi yetersiz:', data);
        }

    } catch (error) {
        console.error('❌ Ekipman grafiği hatası:', error);
        hideLoadingIndicator('equipmentStatusChart');
        showErrorOnChart(canvas.parentElement, 'Ekipman grafiği oluşturulamadı: ' + error.message);
    }
}

function initCategoryChart(data) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) {
        console.error('❌ Category chart canvas bulunamadı');
        return;
    }

    console.log('📊 Kategori grafiği oluşturuluyor, veri:', data);

    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }

    const ctx = canvas.getContext('2d');

    try {
        if (data && data.labels && data.labels.length > 0) {
            categoryChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Miktar',
                        data: data.data,
                        backgroundColor: '#667eea',
                        borderColor: '#5a6fd8',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });

            hideLoadingIndicator('categoryChart');
            console.log('✅ Kategori grafiği oluşturuldu');

        } else {
            hideLoadingIndicator('categoryChart');
            showNoDataMessage(canvas.parentElement, 'kategori');
            console.log('ℹ️ Kategori verisi yetersiz:', data);
        }

    } catch (error) {
        console.error('❌ Kategori grafiği hatası:', error);
        hideLoadingIndicator('categoryChart');
        showErrorOnChart(canvas.parentElement, 'Kategori grafiği oluşturulamadı: ' + error.message);
    }
}

function initLicenseChart(data) {
    const canvas = document.getElementById('licenseStatusChart');
    if (!canvas) {
        console.error('❌ License chart canvas bulunamadı');
        return;
    }

    console.log('📊 Lisans grafiği oluşturuluyor, veri:', data);

    // Destroy existing chart
    if (licenseChart) {
        licenseChart.destroy();
    }

    const ctx = canvas.getContext('2d');

    try {
        if (data && data.total >= 1) {
            licenseChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Aktif', 'Süresi Dolmuş', 'İptal Edilmiş'],
                    datasets: [{
                        label: 'Lisans Sayısı',
                        data: [data.active || 0, data.expired || 0, data.cancelled || 0],
                        backgroundColor: ['#28a745', '#dc3545', '#6c757d'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });

            hideLoadingIndicator('licenseStatusChart');
            console.log('✅ Lisans grafiği oluşturuldu');

        } else {
            hideLoadingIndicator('licenseStatusChart');
            showNoDataMessage(canvas.parentElement, 'lisans');
            console.log('ℹ️ Lisans verisi yetersiz:', data);
        }

    } catch (error) {
        console.error('❌ Lisans grafiği hatası:', error);
        hideLoadingIndicator('licenseStatusChart');
        showErrorOnChart(canvas.parentElement, 'Lisans grafiği oluşturulamadı: ' + error.message);
    }
}

function initDepartmentChart(data) {
    const canvas = document.getElementById('departmentChart');
    if (!canvas) {
        console.error('❌ Department chart canvas bulunamadı');
        return;
    }

    console.log('📊 Departman grafiği oluşturuluyor, veri:', data);

    // Destroy existing chart
    if (departmentChart) {
        departmentChart.destroy();
    }

    const ctx = canvas.getContext('2d');

    try {
        if (data && data.labels && data.labels.length > 0) {
            departmentChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Ekipman Sayısı',
                        data: data.data,
                        backgroundColor: ['#667eea', '#28a745', '#17a2b8', '#ffc107'],
                        borderWidth: 0
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });

            hideLoadingIndicator('departmentChart');
            console.log('✅ Departman grafiği oluşturuldu');

        } else {
            hideLoadingIndicator('departmentChart');
            showNoDataMessage(canvas.parentElement, 'departman');
            console.log('ℹ️ Departman verisi yetersiz:', data);
        }

    } catch (error) {
        console.error('❌ Departman grafiği hatası:', error);
        hideLoadingIndicator('departmentChart');
        showErrorOnChart(canvas.parentElement, 'Departman grafiği oluşturulamadı: ' + error.message);
    }
}

function showNoDataMessage(container, dataType) {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #999; font-size: 1.1rem; padding: 20px;">
            <i class="fas fa-chart-bar" style="font-size: 4rem; margin-bottom: 20px; color: #dee2e6;"></i>
            <h4 style="margin-bottom: 15px; color: #6c757d; text-align: center;">Henüz ${dataType} verisi yok</h4>
            <p style="text-align: center; color: #999; margin-bottom: 25px; max-width: 300px; line-height: 1.5;">
                ${dataType === 'ekipman' ? 'Sistem yönetim panelinden ekipman ekleyerek grafikleri görüntüleyebilirsiniz.' :
                  dataType === 'lisans' ? 'Sistem yönetim panelinden lisans ekleyerek grafikleri görüntüleyebilirsiniz.' :
                  dataType === 'kategori' ? 'Ekipman kategorileri otomatik olarak ekipman eklendikçe oluşacaktır.' :
                  dataType === 'departman' ? 'Departman dağılımı ekipman atamalarına göre oluşacaktır.' :
                  'Veri ekleyerek grafikleri görüntüleyebilirsiniz.'}
            </p>
            <div style="display: flex; gap: 10px;">
                <button onclick="refreshData()" class="btn btn-sm btn-primary">
                    <i class="fas fa-sync-alt"></i> Yenile
                </button>
                ${dataType === 'ekipman' ? '<a href="/admin/inventory/equipment/add" class="btn btn-sm btn-success"><i class="fas fa-plus"></i> Ekipman Ekle</a>' :
                  dataType === 'lisans' ? '<a href="/admin/inventory/licenses/add" class="btn btn-sm btn-success"><i class="fas fa-plus"></i> Lisans Ekle</a>' :
                  '<a href="/admin/inventory" class="btn btn-sm btn-success"><i class="fas fa-plus"></i> Envanter</a>'}
            </div>
        </div>
    `;
}

function showErrorOnChart(container, errorMessage) {
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #dc3545; padding: 20px;">
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 15px;"></i>
            <h4 style="margin-bottom: 10px;">Grafik Hatası</h4>
            <p style="text-align: center; font-size: 0.9rem;">${errorMessage}</p>
            <button onclick="location.reload()" class="btn btn-sm btn-danger" style="margin-top: 15px;">
                <i class="fas fa-redo"></i> Sayfayı Yenile
            </button>
        </div>
    `;
}

function showErrorMessage(message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'alert alert-danger';
    errorContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 8px;
        border: none;
    `;
    errorContainer.innerHTML = `
        <div style="display: flex; align-items: center;">
            <i class="fas fa-exclamation-triangle" style="margin-right: 10px; font-size: 1.2rem;"></i>
            <div style="flex: 1;">
                <strong>Hata:</strong> ${message}
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; margin-left: 10px; opacity: 0.7;">&times;</button>
        </div>
    `;
    document.body.appendChild(errorContainer);

    setTimeout(() => {
        if (errorContainer.parentElement) {
            errorContainer.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => errorContainer.remove(), 300);
        }
    }, 10000);
}

// Utility functions
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

function showComingSoon(feature) {
    showNotification(`${feature} modülü yakında eklenecek!`, 'info');
}

function exportReport() {
    showNotification('Rapor indiriliyor... Bu özellik yakında eklenecek!', 'info');
}

function refreshData() {
    showNotification('Veriler yenileniyor...', 'info');
    showLoadingIndicators();
    setTimeout(() => {
        location.reload();
    }, 1500);
}

function updateEquipmentChart() {
    const period = document.getElementById('equipmentPeriod')?.value || 'all';
    showNotification(`Grafik güncelleniyor (${period})... Bu özellik yakında eklenecek!`, 'info');
}

function toggleChartType(chartId) {
    showNotification('Grafik tipi değiştiriliyor... Bu özellik yakında eklenecek!', 'info');
}

function showDepartmentDetails() {
    showNotification('Departman detayları gösteriliyor... Bu özellik yakında eklenecek!', 'info');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 8px;
        border: none;
    `;

    const iconMap = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle'
    };

    notification.innerHTML = `
        <div style="display: flex; align-items: center;">
            <i class="fas fa-${iconMap[type] || 'info-circle'}" style="margin-right: 10px; font-size: 1.2rem;"></i>
            <div style="flex: 1;">${message}</div>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; margin-left: 10px; opacity: 0.7;">&times;</button>
        </div>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Debug function
function debugChartData() {
    console.log('=== 🔍 Chart Data Debug Info ===');
    console.log('Chart.js loaded:', typeof Chart !== 'undefined');

    // Dashboard data script kontrolü
    const dashboardDataScript = document.getElementById('dashboard-data');
    if (dashboardDataScript) {
        try {
            const data = JSON.parse(dashboardDataScript.textContent);
            console.log('📄 Dashboard Data Script:', data);
        } catch (error) {
            console.error('❌ Dashboard data parsing error:', error);
        }
    } else {
        console.error('❌ Dashboard data script BULUNAMADI!');
    }

    console.log('📊 Alınan veriler:');
    console.log('  Equipment:', getEquipmentData());
    console.log('  Category:', getCategoryData());
    console.log('  License:', getLicenseData());
    console.log('  Department:', getDepartmentData());

    console.log('📈 Grafik durumları:', {
        equipmentChart: !!equipmentChart,
        categoryChart: !!categoryChart,
        licenseChart: !!licenseChart,
        departmentChart: !!departmentChart
    });

    // Canvas kontrolü
    console.log('🎨 Canvas elementleri:');
    ['equipmentStatusChart', 'categoryChart', 'licenseStatusChart', 'departmentChart'].forEach(id => {
        const canvas = document.getElementById(id);
        console.log(`  ${id}:`, canvas ? '✅ Bulundu' : '❌ Bulunamadı');
    });
}

// Global olarak erişilebilir yap
window.debugChartData = debugChartData;

// CSS for animations and styling
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .loading-spinner {
        display: flex;
        align-items: center;
        color: #667eea;
        font-weight: 500;
    }
    .chart-loading {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(5px);
        border-radius: 8px;
    }
    .btn {
        padding: 8px 16px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .btn-sm { padding: 6px 12px; font-size: 0.875rem; }
    .btn-primary { background: #667eea; color: white; }
    .btn-primary:hover { background: #5a6fd8; transform: translateY(-1px); }
    .btn-success { background: #28a745; color: white; }
    .btn-success:hover { background: #218838; transform: translateY(-1px); }
    .btn-danger { background: #dc3545; color: white; }
    .btn-danger:hover { background: #c82333; transform: translateY(-1px); }
    .alert {
        padding: 15px 20px;
        border-radius: 8px;
        border: none;
    }
    .alert-danger { background: linear-gradient(135deg, #dc3545, #c82333); color: white; }
    .alert-info { background: linear-gradient(135deg, #17a2b8, #138496); color: white; }
    .alert-success { background: linear-gradient(135deg, #28a745, #218838); color: white; }
    .alert-warning { background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }
`;
document.head.appendChild(style);

// Auto debug after load
setTimeout(() => {
    console.log('🚀 Analytics Dashboard yüklendi!');
    console.log('🔍 Debug için: window.debugChartData() komutunu kullanın');
    window.debugChartData();
}, 2000);

console.log('✅ Analytics Dashboard JavaScript loaded successfully');