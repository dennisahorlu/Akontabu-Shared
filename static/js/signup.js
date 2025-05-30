// Firebase configuration
const firebaseConfig = {
    // Your Firebase configuration will go here
    // You'll need to replace this with your actual Firebase config
    apiKey: "AIzaSyDIqabQ80-TJBdLLpaUm7snIDnFsUCZ0Q0",
    authDomain: "akontabu.firebaseapp.com",
    projectId: "akontabu",
    storageBucket: "akontabu.appspot.com",
    messagingSenderId: "XXXXXXXXXXXX",
    appId: "1:XXXXXXXXXXXX:web:XXXXXXXXXXXX"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

auth.onAuthStateChanged(user => {
    if (user) {
      console.log("User is signed in:", user.email);
    } else {
      console.log("No user signed in");
    }
  });

// Password validation
const password = document.getElementById('password');
const requirements = {
    uppercase: document.getElementById('uppercase'),
    lowercase: document.getElementById('lowercase'),
    number: document.getElementById('number'),
    special: document.getElementById('special')
};

const patterns = {
    uppercase: /[A-Z]/,
    lowercase: /[a-z]/,
    number: /[0-9]/,
    special: /[!@#$%^&*(),.?":{}|<>]/
};

password.addEventListener('input', () => {
    const value = password.value;
    
    for (const [requirement, pattern] of Object.entries(patterns)) {
        const element = requirements[requirement];
        if (pattern.test(value)) {
            element.classList.add('valid');
        } else {
            element.classList.remove('valid');
        }
    }
});

// Form submission
const form = document.getElementById('signup-form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Validate password
    let isValid = true;
    for (const [requirement, pattern] of Object.entries(patterns)) {
        if (!pattern.test(data.password)) {
            isValid = false;
            break;
        }
    }
    
    if (!isValid) {
        alert('Please ensure your password meets all requirements.');
        return;
    }
    
    try {
        const response = await fetch('/signup', {
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
            alert(error.message || 'An error occurred during signup.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during signup.');
    }
});

// Google Sign In
const googleBtn = document.getElementById('googleSignIn');
googleBtn.addEventListener('click', async () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    
    try {
        const result = await auth.signInWithPopup(provider);
        const user = result.user;
        
        // Send user data to backend
        const response = await fetch('/google-signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: user.displayName,
                email: user.email,
                googleId: user.uid
            })
        });
        
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const error = await response.json();
            alert(error.message || 'An error occurred during Google signup.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during Google signup.');
    }
}); 