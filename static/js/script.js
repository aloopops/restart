document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const browseBtn = document.getElementById('browse-btn');
    const previewImage = document.getElementById('preview-image');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const processingContainer = document.getElementById('processing-container');
    const resultContainer = document.getElementById('result-container');
    const resultImage = document.getElementById('result-image');
    const downloadBtn = document.getElementById('download-btn');
    const newImageBtn = document.getElementById('new-image-btn');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const progressBar = document.getElementById('processing-progress-bar');

    // Event Listeners for drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    browseBtn.addEventListener('click', function() {
        fileInput.click();
    });
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            handleFileSelect(this.files[0]);
        }
    });
    newImageBtn.addEventListener('click', resetUI);

    // Drag and Drop handlers
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.add('highlight');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('highlight');
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    }

    // Handle file selection
    function handleFileSelect(file) {
        // Check file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            showError('Please select a valid image file (PNG, JPG, JPEG, WEBP)');
            return;
        }

        // Hide error message if visible
        hideError();

        // Display image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewImage.classList.remove('preview-hidden');
            uploadPlaceholder.style.display = 'none';
            
            // Set a small delay to show the preview before starting upload
            setTimeout(() => {
                uploadImage(file);
            }, 500);
        };
        reader.readAsDataURL(file);
    }

    // Upload image to server
    function uploadImage(file) {
        // Show processing indicator
        uploadArea.style.display = 'none';
        processingContainer.classList.remove('d-none');
        
        // Set progress bar animation
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 75) {
                progress += 5;
                progressBar.style.width = progress + '%';
            }
        }, 300);

        // First convert the file to base64
        const reader = new FileReader();
        reader.onloadend = function() {
            const base64data = reader.result;
            
            // Send base64 data to server
            fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_data: base64data,
                    filename: file.name
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to process image');
                }
                return response.json();
            })
            .then(data => {
                clearInterval(progressInterval);
                progressBar.style.width = '100%';
                
                // Set a small delay to complete the progress bar animation
                setTimeout(() => {
                    displayResult(data.filename);
                }, 500);
            })
            .catch(error => {
                clearInterval(progressInterval);
                processingContainer.classList.add('d-none');
                uploadArea.style.display = 'flex';
                showError(error.message || 'An error occurred while processing the image');
            });
        };
        reader.readAsDataURL(file);
    }

    // Display processed image
    function displayResult(filename) {
        processingContainer.classList.add('d-none');
        resultContainer.classList.remove('d-none');
        
        // Set result image source
        resultImage.src = `/processed/${filename}`;
        
        // Set download link
        downloadBtn.href = `/processed/${filename}`;
        downloadBtn.download = 'removed-background.png';
    }

    // Reset UI for new image
    function resetUI() {
        // Reset all UI elements
        previewImage.classList.add('preview-hidden');
        uploadPlaceholder.style.display = 'block';
        uploadArea.style.display = 'flex';
        processingContainer.classList.add('d-none');
        resultContainer.classList.add('d-none');
        
        // Clear file input
        fileInput.value = '';
    }

    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('d-none');
    }

    // Hide error message
    function hideError() {
        errorAlert.classList.add('d-none');
    }
});
