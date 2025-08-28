 function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function showComingSoon(feature) {
            alert(`${feature} modülü yakında eklenecek!`);
        }

        // Auto-submit form on filter change
        document.getElementById('category').addEventListener('change', function() {
            this.form.submit();
        });

        document.getElementById('status').addEventListener('change', function() {
            this.form.submit();
        });

        document.getElementById('assigned').addEventListener('change', function() {
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