// Admin Dashboard JavaScript

// Sidebar toggle functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

// Show coming soon alert
function showComingSoon(feature) {
    alert(`${feature} modülü yakında eklenecek!`);
}

// Auto-refresh stats every 5 minutes
setInterval(function() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            console.log('Stats updated:', data);
        })
        .catch(error => console.log('Stats update failed:', error));
}, 300000); // 5 minutes

// Mobile sidebar toggle
function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

// Close sidebar on mobile when clicking outside
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.querySelector('.toggle-sidebar');

    if (window.innerWidth <= 768 &&
        !sidebar.contains(e.target) &&
        !toggleBtn.contains(e.target) &&
        sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
    }
});

// Update toggle for mobile
if (window.innerWidth <= 768) {
    document.querySelector('.toggle-sidebar').onclick = toggleMobileSidebar;
}

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Dashboard loaded successfully');

    // Add smooth transitions
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// Handle window resize
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');

    // Reset sidebar state on desktop
    if (window.innerWidth > 768) {
        sidebar.classList.remove('show');
        document.querySelector('.toggle-sidebar').onclick = toggleSidebar;
    } else {
        document.querySelector('.toggle-sidebar').onclick = toggleMobileSidebar;
    }
});