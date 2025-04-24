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
            setTimeout(checkStatus, 2000);  // keep polling if still processing
        }
    } catch (error) {
        console.error('⚠️ Error checking processing status:', error);
        displayErrorMessage('An error occurred while checking your status. Please try again.');
        // Do not redirect here — let user manually refresh or recover
    }
}
