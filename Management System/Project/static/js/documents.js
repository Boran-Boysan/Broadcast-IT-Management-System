// static/js/documents.js

function openDocument(documentId, filePath) {
    console.log('Opening document:', documentId, filePath);

    if (!filePath || filePath.trim() === '') {
        window.location.href = '/admin/knowledge-base/view/' + documentId;
        return;
    }

    const fileExtension = filePath.split('.').pop().toLowerCase();
    console.log('File extension:', fileExtension);

    if (['pdf', 'jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
        console.log('Opening PDF/Image in new tab');
        window.open('/admin/knowledge-base/preview/' + documentId, '_blank');
    } else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(fileExtension)) {
        console.log('Downloading Office file');
        window.location.href = '/admin/knowledge-base/download/' + documentId;
    } else {
        console.log('Going to view page');
        window.location.href = '/admin/knowledge-base/view/' + documentId;
    }
}

function deleteDocument(documentId, documentTitle) {
    console.log('Delete function called:', documentId, documentTitle);
    document.getElementById('documentTitle').textContent = documentTitle;
    document.getElementById('deleteForm').action = '/admin/knowledge-base/delete/' + documentId;
    document.getElementById('deleteModal').style.display = 'block';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Sayfa yüklendiğinde çalışacak kodlar
document.addEventListener('DOMContentLoaded', function() {
    console.log('Documents JS loaded successfully!');

    // Modal kapatma eventi
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.onclick = closeDeleteModal;
    }

    // Window click eventi
    window.onclick = function(event) {
        // Modal kapatma
        const modal = document.getElementById('deleteModal');
        if (event.target === modal) {
            closeDeleteModal();
        }
    }
});