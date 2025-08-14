
import React, { useState, useEffect, useRef, useCallback, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, Link } from 'react-router-dom';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc } from 'firebase/firestore';



// --- FULL ONBOARDING, CONTEXT, DASHBOARD, AND ROUTING LOGIC ---

// (1) MessageBox Component
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

// (2) Firebase Context/Provider
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
  const [userData, setUserData] = useState(null);
  useEffect(() => {
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
          const userDocRef = doc(dbInstance, `artifacts/${appId}/users/${user.uid}/promethean_data/onboarding_profile`);
          const docSnap = await getDoc(userDocRef);
          if (docSnap.exists()) setUserData(docSnap.data());
          else setUserData({ prometheanName: '', userName: '', coreIdentity: '', birthdate: '', focusAreas: '', employmentHistory: '', familyMembers: '', personalInterests: '', learningObjectives: '', legacyMotivations: '', initialDriftScore: 0, finalDriftScore: 0, evaluationHours: 0, significantInteractions: 0, bonded: false, nftMetadata: null, finalNftMetadata: null, currentPhase: 1, realignTimerSetting: 'Monthly' });
        } else {
          try {
            if (initialAuthToken) await signInWithCustomToken(authInstance, initialAuthToken);
            else await signInAnonymously(authInstance);
          } catch (error) {
            displayMessageBox(`Authentication failed: ${error.message}. Please try again.`);
            setIsAuthReady(true);
            setUserData({ currentPhase: 1, realignTimerSetting: 'Monthly' });
          }
        }
      });
      return () => unsubscribe();
    } catch (error) {
      displayMessageBox("Failed to initialize Prometheus Prime. Please check your configuration.");
      setIsAuthReady(true);
      setUserData({ currentPhase: 1, realignTimerSetting: 'Monthly' });
    }
  }, [displayMessageBox]);
  const saveUserData = useCallback(async (dataToSave) => {
    if (!isAuthReady || !userId || !dbInstance) return;
    try {
      const userDocRef = doc(dbInstance, `artifacts/${appId}/users/${userId}/promethean_data/onboarding_profile`);
      await setDoc(userDocRef, dataToSave, { merge: true });
    } catch (error) {
      displayMessageBox("Failed to save your progress. Please check your connection.");
    }
  }, [isAuthReady, userId, displayMessageBox]);
  return (
    <FirebaseContext.Provider value={{ db: dbInstance, auth: authInstance, userId, isAuthReady, userData, setUserData, saveUserData, appId }}>
      {children}
    </FirebaseContext.Provider>
  );
};


// (3) Minimal Onboarding/Dashboard Routing Example
const AppContent = () => {
  const { isAuthReady, userData, setUserData, saveUserData } = useFirebase();
  const [currentPhase, setCurrentPhase] = useState(0);
  const [messageBoxVisible, setMessageBoxVisible] = useState(false);
  const [messageBoxContent, setMessageBoxContent] = useState('');
  const [visualizationMode, setVisualizationMode] = useState('observer');

  const displayMessageBox = useCallback((message) => {
    setMessageBoxContent(message);
    setMessageBoxVisible(true);
  }, []);

  useEffect(() => {
    if (isAuthReady && userData) {
      setCurrentPhase(userData.currentPhase || 1);
    }
  }, [isAuthReady, userData]);

  useEffect(() => {
    if (isAuthReady && userData && userData.currentPhase > 0) {
      const handler = setTimeout(() => {
        saveUserData(userData);
      }, 1000);
      return () => clearTimeout(handler);
    }
  }, [userData, currentPhase, isAuthReady, saveUserData]);

  const nextPhase = useCallback(() => {
    setCurrentPhase(prevPhase => {
      const newPhase = prevPhase + 1;
      setUserData(prev => ({ ...prev, currentPhase: newPhase }));
      return newPhase;
    });
  }, [setUserData]);

  // Placeholder: Replace with your actual onboarding phase components
  const Phase1 = () => <div className="text-center">Phase 1: Cognitive Priming</div>;
  const Phase2 = () => <div className="text-center">Phase 2: Drift Field Activation</div>;
  const Phase3 = () => <div className="text-center">Phase 3: Cellular Integration</div>;
  const Phase4 = () => <div className="text-center">Phase 4: NFT Genesis Protocol</div>;
  const Phase5 = () => <div className="text-center">Phase 5: Knowledge Osmosis</div>;
  const Phase6 = () => <div className="text-center">Phase 6: Cognitive Stabilization</div>;

  const renderContent = () => {
    if (!isAuthReady) return <div className="text-center text-gray-700 dark:text-gray-300 text-xl">Initializing Prometheus Prime... Please wait.</div>;
    if (currentPhase === 7) return <div className="text-center">Onboarding Complete! Dashboard coming soon.</div>;
    return (
      <>
        {currentPhase === 1 && <Phase1 />}
        {currentPhase === 2 && <Phase2 />}
        {currentPhase === 3 && <Phase3 />}
        {currentPhase === 4 && <Phase4 />}
        {currentPhase === 5 && <Phase5 />}
        {currentPhase === 6 && <Phase6 />}
      </>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center p-4 transition-colors duration-300">
      <div className="container bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 md:p-12 w-full max-w-4xl flex flex-col items-center transition-colors duration-300">
        <button
          onClick={() => document.documentElement.classList.toggle("dark")}
          className="self-end text-sm text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-200 mb-4 transition-colors duration-300"
        >Activate Synaptic Dimming</button>
        {renderContent()}
      </div>
      {messageBoxVisible && <MessageBox message={messageBoxContent} onClose={() => setMessageBoxVisible(false)} />}
    </div>
  );
};

const App = () => {
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

export default App;
