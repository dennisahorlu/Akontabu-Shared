// Firebase configuration
const firebaseConfig = {
    // Your Firebase configuration will go here
    // You'll need to replace this with your actual Firebase config
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Form submission
const form = document.getElementById('login-form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const error = await response.json();
            alert(error.message || 'Invalid email or password.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login.');
    }
});

// Google Sign In
const googleBtn = document.getElementById('google-signin');
googleBtn.addEventListener('click', async () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    
    try {
        const result = await auth.signInWithPopup(provider);
        const user = result.user;
        
        // Send user data to backend
        const response = await fetch('/google-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: user.email,
                googleId: user.uid
            })
        });
        
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const error = await response.json();
            alert(error.message || 'An error occurred during Google login.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during Google login.');
    }
}); 