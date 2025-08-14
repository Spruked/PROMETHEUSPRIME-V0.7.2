
import React, { useState, useCallback, useContext, createContext } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { initializeApp } from 'firebase/app';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// --- ADMIN DASHBOARD, CONTEXT, AND ROUTING LOGIC ---

// (1) MessageBox Component (shared UI for admin alerts)
const MessageBox = ({ message, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
    <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-xl text-center max-w-sm w-11/12 transition-colors duration-300">
      <p className="text-lg mb-6 text-gray-800 dark:text-gray-100">{message}</p>
      <button
        onClick={onClose}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-xl transition-all duration-200 transform hover:scale-105"
      >OK</button>
    </div>
  </div>
);

// (2) Shared Firebase Context/Provider (admin-aware)
const FirebaseContext = createContext(null);
const useFirebase = () => {
  const context = useContext(FirebaseContext);
  if (!context) throw new Error('useFirebase must be used within a FirebaseProvider');
  return context;
};
const appId = typeof __app_id !== 'undefined' ? __app_id : 'your-default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
let firebaseAppInstance, dbInstance, authInstance;
const FirebaseProvider = ({ children, displayMessageBox }) => {
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [userId, setUserId] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  React.useEffect(() => {
    try {
      if (!firebaseAppInstance) {
        firebaseAppInstance = initializeApp(firebaseConfig);
        dbInstance = getFirestore(firebaseAppInstance);
        authInstance = getAuth(firebaseAppInstance);
      }
      const unsubscribe = onAuthStateChanged(authInstance, async (user) => {
        if (user) {
          setUserId(user.uid);
          setIsAuthReady(true);
          // Admin check: implement your admin check logic here (e.g., custom claims, Firestore roles)
          // For now, treat all authenticated users as admin for demo
          setIsAdmin(true);
        } else {
          setIsAuthReady(true);
          setIsAdmin(false);
        }
      });
      return () => unsubscribe();
    } catch (error) {
      displayMessageBox("Failed to initialize admin dashboard. Please check your configuration.");
      setIsAuthReady(true);
      setIsAdmin(false);
    }
  }, [displayMessageBox]);
  return (
    <FirebaseContext.Provider value={{ db: dbInstance, auth: authInstance, userId, isAuthReady, isAdmin, appId }}>
      {children}
    </FirebaseContext.Provider>
  );
};

// (3) Minimal Master/Admin Dashboard Routing Example
const AdminHome = () => (
  <div className="text-center text-2xl font-bold text-gray-800 dark:text-gray-100">
    Master Dashboard: User Monitoring & System Controls
    <div className="mt-6 text-base font-normal text-gray-600 dark:text-gray-300">
      {/* Placeholder: Add user analytics, system status, controls, etc. */}
      <p>Welcome, Admin. Here you can monitor users, view analytics, and manage system settings.</p>
    </div>
  </div>
);

const AppContent = () => {
  const { isAuthReady, isAdmin } = useFirebase();
  if (!isAuthReady) return <div className="text-center text-xl">Initializing Admin Dashboard...</div>;
  if (!isAdmin) return <div className="text-center text-xl text-red-600">Access Denied: Admins Only</div>;
  return <AdminHome />;
};

const MasterDashboard = () => {
  const [messageBoxVisible, setMessageBoxVisible] = useState(false);
  const [messageBoxContent, setMessageBoxContent] = useState('');
  const displayMessageBox = useCallback((message) => {
    setMessageBoxContent(message);
    setMessageBoxVisible(true);
  }, []);
  return (
    <Router>
      <FirebaseProvider displayMessageBox={displayMessageBox}>
        <Routes>
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </FirebaseProvider>
      {messageBoxVisible && <MessageBox message={messageBoxContent} onClose={() => setMessageBoxVisible(false)} />}
    </Router>
  );
};

export default MasterDashboard;
