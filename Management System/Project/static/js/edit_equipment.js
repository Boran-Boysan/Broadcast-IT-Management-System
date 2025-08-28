 function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        // Form submission
        document.getElementById('editEquipmentForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        });

        // Status change handling
        document.getElementById('status').addEventListener('change', function() {
            const status = this.value;
            const assignedToSelect = document.getElementById('assigned_to');

            if (status === 'in_stock' || status === 'under_repair' || status === 'scrap') {
                // Bu durumlar için atama önerilmez
                if (status === 'scrap') {
                    assignedToSelect.value = '';
                    assignedToSelect.disabled = true;
                } else {
                    assignedToSelect.disabled = false;
                }
            } else {
                assignedToSelect.disabled = false;
            }
        });

        // Assignment change detection
        const originalAssignment = "{{ equipment.assigned_to or '' }}";
        document.getElementById('assigned_to').addEventListener('change', function() {
            const newAssignment = this.value;
            if (originalAssignment !== newAssignment) {
                console.log('Assignment changed:', originalAssignment, '->', newAssignment);
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

        // Detect changes for unsaved warning
        let originalData = {};
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('editEquipmentForm');
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                originalData[key] = value;
            }
        });

        window.addEventListener('beforeunload', function(e) {
            const form = document.getElementById('editEquipmentForm');
            const currentData = new FormData(form);
            let hasChanges = false;

            for (let [key, value] of currentData.entries()) {
                if (originalData[key] !== value) {
                    hasChanges = true;
                    break;
                }
            }

            if (hasChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });