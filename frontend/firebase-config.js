import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyBpgpMhMt51L584EGZdB9jB5Qa51bMwHwU",
  authDomain: "storymagic-ai-c84ae.firebaseapp.com",
  projectId: "storymagic-ai-c84ae",
  storageBucket: "storymagic-ai-c84ae.firebasestorage.app",
  messagingSenderId: "767791946995",
  appId: "1:767791946995:web:b710636a4163b9c630ab86"
};

const app = initializeApp(firebaseConfig);
export const db  = getFirestore(app);
export const auth = getAuth(app);

