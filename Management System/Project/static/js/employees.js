function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        // Auto-submit form on filter change
        document.getElementById('department').addEventListener('change', function() {
            this.form.submit();
        });

        document.getElementById('role').addEventListener('change', function() {
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

        // Highlight search results
        const searchTerm = '{{ search }}';
        if (searchTerm) {
            const cells = document.querySelectorAll('td');
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchTerm.toLowerCase())) {
                    cell.innerHTML = cell.innerHTML.replace(
                        new RegExp(`(${searchTerm})`, 'gi'),
                        '<mark style="background: #fff3cd; padding: 2px 4px; border-radius: 3px;">$1</mark>'
                    );
                }
            });
        }