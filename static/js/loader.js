function displayErrorMessage(message) {
    let errorContainer = document.getElementById('error-message');

    if (!errorContainer) {
        // Create the container if it doesn't exist
        errorContainer = document.createElement('div');
        errorContainer.id = 'error-message';
        errorContainer.style.position = 'fixed';
        errorContainer.style.top = '20px';
        errorContainer.style.left = '50%';
        errorContainer.style.transform = 'translateX(-50%)';
        errorContainer.style.backgroundColor = '#ff4d4d';
        errorContainer.style.color = '#fff';
        errorContainer.style.padding = '12px 20px';
        errorContainer.style.borderRadius = '8px';
        errorContainer.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        errorContainer.style.zIndex = '1000';
        errorContainer.style.fontFamily = 'Arial, sans-serif';
        errorContainer.style.fontSize = '16px';
        errorContainer.style.maxWidth = '80%';
        errorContainer.style.textAlign = 'center';
        document.body.appendChild(errorContainer);
    }

    // Set the error message content
    errorContainer.textContent = message;

    // Optionally hide after a while
    setTimeout(() => {
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
    }, 5000);
}


async function checkStatus() {
    try {
        const response = await fetch('/processing-status', {
            method: 'GET',
            credentials: 'include'
        });

        const data = await response.json();
        console.log('Status response:', data);

        if (data.status === 'done') {
            console.log('✅ Processing complete. Redirecting to main page...');
            window.location.href = '/';
        } else if (data.status === 'error') {
            console.error('❌ Error during processing. Redirecting to main page...');
            displayErrorMessage('There was an issue processing your data. Redirecting...');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);  // slight delay for user to see the message
        } else {
            console.log('⏳ Still processing... Checking again in 2 seconds.');
            setTimeout(checkStatus, 5000);  // keep polling if still processing
        }
    } catch (error) {
        console.error('⚠️ Error checking processing status:', error);
        displayErrorMessage('An error occurred while checking your status. Please try again.');
        // Do not redirect here — let user manually refresh or recover
    }
}

checkStatus()