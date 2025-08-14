
import React, { useState, useEffect, useCallback } from 'react';
// Firebase imports (commented for local dev)
// import { initializeApp } from 'firebase/app';
// import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
// import { getFirestore, doc, setDoc, getDoc } from 'firebase/firestore';

import {
    MessageBox,
    Phase1,
    Phase2,
    Phase3,
    Phase4,
    Phase5,
    Phase6
} from './components/OnboardingPhases';
import MasterDashboard from './components/MasterDashboard';

// Placeholder Firebase config for local dev
const appId = 'your-default-app-id';
const firebaseConfig = {};
const initialAuthToken = null;

const toggleDarkMode = () => {
    document.documentElement.classList.toggle("dark");
};

const App = () => {
    const [currentPhase, setCurrentPhase] = useState(1); // Start at phase 1 for local dev
    const [userData, setUserData] = useState({
        prometheanName: '', userName: '', coreIdentity: '', birthdate: '', focusAreas: '',
        employmentHistory: '', familyMembers: '', personalInterests: '', learningObjectives: '', legacyMotivations: '',
        initialDriftScore: 0, finalDriftScore: 0, evaluationHours: 0, significantInteractions: 0,
        bonded: false, nftMetadata: null, finalNftMetadata: null
    });
    const [isAuthReady, setIsAuthReady] = useState(true); // Always true for local dev
    const [userId, setUserId] = useState(null);
    const [messageBoxVisible, setMessageBoxVisible] = useState(false);
    const [messageBoxContent, setMessageBoxContent] = useState('');
    const [visualizationMode, setVisualizationMode] = useState('observer');

    // Message box
    const displayMessageBox = useCallback((message) => {
        setMessageBoxContent(message);
        setMessageBoxVisible(true);
    }, []);

    // Placeholder saveUserData (no Firestore in local dev)
    const saveUserData = useCallback(async (dataToSave) => {
        // No-op for local dev
    }, []);

    const nextPhase = useCallback(() => {
        setCurrentPhase(prevPhase => {
            const newPhase = prevPhase + 1;
            if (newPhase > 6) return 7;
            return newPhase;
        });
    }, []);

    const renderPhase = () => {
        if (!isAuthReady) {
            return (
                <div className="text-center text-gray-700 dark:text-gray-300 text-xl">
                    Initializing Prometheus Prime... Please wait.
                </div>
            );
        }
        switch (currentPhase) {
            case 1:
                return <Phase1 userData={userData} setUserData={setUserData} nextPhase={nextPhase} displayMessageBox={displayMessageBox} />;
            case 2:
                return (
                    <Phase2
                        userData={userData}
                        setUserData={setUserData}
                        nextPhase={nextPhase}
                        initialDriftScore={userData.initialDriftScore}
                        setInitialDriftScore={(score) => setUserData(prev => ({ ...prev, initialDriftScore: score }))}
                        visualizationMode={visualizationMode}
                        setVisualizationMode={setVisualizationMode}
                    />
                );
            case 3:
                return <Phase3 userData={userData} setUserData={setUserData} nextPhase={nextPhase} displayMessageBox={displayMessageBox} saveUserData={saveUserData} />;
            case 4:
                return <Phase4 userData={userData} setUserData={setUserData} nextPhase={nextPhase} saveUserData={saveUserData} />;
            case 5:
                return <Phase5 userData={userData} setUserData={setUserData} nextPhase={nextPhase} saveUserData={saveUserData} />;
            case 6:
                return <Phase6 userData={userData} setUserData={setUserData} nextPhase={nextPhase} saveUserData={saveUserData} />;
            case 7:
                return <MasterDashboard userData={userData} />;
            default:
                return <div className="text-center text-gray-700 dark:text-gray-300 text-xl">Something went wrong. Please refresh.</div>;
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center p-4 transition-colors duration-300">
            <div className="container bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 md:p-12 w-full max-w-4xl flex flex-col items-center transition-colors duration-300">
                <button
                    onClick={toggleDarkMode}
                    className="self-end text-sm text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-200 mb-4 transition-colors duration-300"
                >
                    Toggle Dark Mode
                </button>
                {renderPhase()}
            </div>
            {messageBoxVisible && <MessageBox message={messageBoxContent} onClose={() => setMessageBoxVisible(false)} />}
        </div>
    );
};

export default App;
