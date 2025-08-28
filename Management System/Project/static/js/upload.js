// Sidebar toggle functionality
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        // Coming soon notification
        function showComingSoon(feature) {
            alert(feature + ' özelliği yakında eklenecek!');
        }

        // File upload functionality
        document.addEventListener('DOMContentLoaded', function() {
            const fileInput = document.getElementById('file');
            const fileInfo = document.getElementById('fileInfo');
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const fileUpload = document.querySelector('.file-upload');

            // File selection handler
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    displayFileInfo(file);
                } else {
                    hideFileInfo();
                }
            });

            // Drag and drop functionality
            fileUpload.addEventListener('dragover', function(e) {
                e.preventDefault();
                fileUpload.classList.add('dragover');
            });

            fileUpload.addEventListener('dragleave', function(e) {
                e.preventDefault();
                fileUpload.classList.remove('dragover');
            });

            fileUpload.addEventListener('drop', function(e) {
                e.preventDefault();
                fileUpload.classList.remove('dragover');

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    displayFileInfo(files[0]);
                }
            });

            function displayFileInfo(file) {
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                fileInfo.classList.add('show');
            }

            function hideFileInfo() {
                fileInfo.classList.remove('show');
            }

            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }

            // Form validation
            const form = document.getElementById('uploadForm');
            const titleInput = document.getElementById('title');

            form.addEventListener('submit', function(e) {
                const title = titleInput.value.trim();

                if (!title) {
                    e.preventDefault();
                    alert('Başlık alanı zorunludur!');
                    titleInput.focus();
                    return;
                }

                if (title.length > 50) {
                    e.preventDefault();
                    alert('Başlık 50 karakterden uzun olamaz!');
                    titleInput.focus();
                    return;
                }
            });

            // Character counter for title
            titleInput.addEventListener('input', function() {
                const current = this.value.length;
                const max = 50;
                const remaining = max - current;

                let counterElement = document.getElementById('titleCounter');
                if (!counterElement) {
                    counterElement = document.createElement('small');
                    counterElement.id = 'titleCounter';
                    counterElement.style.cssText = 'color: #6c757d; font-size: 0.85rem; margin-top: 5px; display: block;';
                    this.parentNode.appendChild(counterElement);
                }

                counterElement.textContent = `${current}/${max} karakter`;

                if (remaining < 10) {
                    counterElement.style.color = '#dc3545';
                } else {
                    counterElement.style.color = '#6c757d';
                }
            });
        });