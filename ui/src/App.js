import { useState, useEffect, useRef, useCallback, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, Link } from 'react-router-dom';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc } from 'firebase/firestore';

// Global variables provided by the Canvas environment
// Ensure these are defined in your Canvas environment or provide fallbacks for local testing
const appId = typeof __app_id !== 'undefined' ? __app_id : 'your-default-app-id'; // Replace with a default if testing locally
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {
    // Your Firebase project configuration for local testing
    // apiKey: "YOUR_API_KEY",
    // authDomain: "YOUR_AUTH_DOMAIN",
    // projectId: "YOUR_PROJECT_ID",
    // storageBucket: "YOUR_STORAGE_BUCKET",
    // messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    // appId: "YOUR_APP_ID"
};
const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

// Initialize Firebase (will be done once in FirebaseProvider)
let firebaseAppInstance;
let dbInstance;
let authInstance;

// Custom Message Box Component (replaces alert())
const MessageBox = ({ message, onClose }) => {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-xl text-center max-w-sm w-11/12 transition-colors duration-300">
                <p className="text-lg mb-6 text-gray-800 dark:text-gray-100">{message}</p>
                <button
                    onClick={onClose}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-xl transition-all duration-200 transform hover:scale-105"
                >
                    OK
                </button>
            </div>
        </div>
    );
};

// Firebase Context
const FirebaseContext = createContext(null);

const useFirebase = () => {
    const context = useContext(FirebaseContext);
    if (!context) {
        throw new Error('useFirebase must be used within a FirebaseProvider');
    }
    return context;
};

const FirebaseProvider = ({ children, displayMessageBox }) => {
    const [isAuthReady, setIsAuthReady] = useState(false);
    const [userId, setUserId] = useState(null);
    const [userData, setUserData] = useState(null); // Will store the full user profile

    useEffect(() => {
        try {
            if (!firebaseAppInstance) { // Initialize only once
                firebaseAppInstance = initializeApp(firebaseConfig);
                dbInstance = getFirestore(firebaseAppInstance);
                authInstance = getAuth(firebaseAppInstance);
            }

            const unsubscribe = onAuthStateChanged(authInstance, async (user) => {
                if (user) {
                    setUserId(user.uid);
                    setIsAuthReady(true);
                    // Load user data from Firestore
                    const userDocRef = doc(dbInstance, `artifacts/${appId}/users/${user.uid}/promethean_data/onboarding_profile`);
                    const docSnap = await getDoc(userDocRef);
                    if (docSnap.exists()) {
                        setUserData(docSnap.data());
                    } else {
                        // If no data, initialize with default structure
                        setUserData({
                            prometheanName: '', userName: '', coreIdentity: '', birthdate: '', focusAreas: '',
                            employmentHistory: '', familyMembers: '', personalInterests: '', learningObjectives: '', legacyMotivations: '',
                            initialDriftScore: 0, finalDriftScore: 0, evaluationHours: 0, significantInteractions: 0,
                            bonded: false, nftMetadata: null, finalNftMetadata: null, currentPhase: 1, // Default to start onboarding
                            realignTimerSetting: 'Monthly' // New default for neuroplasticity setting
                        });
                    }
                } else {
                    // Sign in anonymously if no initial auth token, or if token fails
                    try {
                        if (initialAuthToken) {
                            await signInWithCustomToken(authInstance, initialAuthToken);
                        } else {
                            await signInAnonymously(authInstance);
                        }
                    } catch (error) {
                        console.error("Firebase Auth Error:", error);
                        displayMessageBox(`Authentication failed: ${error.message}. Please try again.`);
                        setIsAuthReady(true);
                        setUserData({ currentPhase: 1, realignTimerSetting: 'Monthly' }); // Ensure onboarding starts even on auth error
                    }
                }
            });

            return () => unsubscribe();
        } catch (error) {
            console.error("Firebase initialization failed:", error);
            displayMessageBox("Failed to initialize Prometheus Prime. Please check your configuration.");
            setIsAuthReady(true);
            setUserData({ currentPhase: 1, realignTimerSetting: 'Monthly' }); // Ensure onboarding starts even on init error
        }
    }, [displayMessageBox]);

    // Save User Data to Firestore
    const saveUserData = useCallback(async (dataToSave) => {
        if (!isAuthReady || !userId || !dbInstance) {
            console.warn("Firestore not ready or userId not available. Cannot save data.");
            return;
        }
        try {
            const userDocRef = doc(dbInstance, `artifacts/${appId}/users/${userId}/promethean_data/onboarding_profile`);
            await setDoc(userDocRef, dataToSave, { merge: true });
            console.log("User data saved to Firestore.");
        } catch (error) {
            console.error("Error saving user data:", error);
            displayMessageBox("Failed to save your progress. Please check your connection.");
        }
    }, [isAuthReady, userId, displayMessageBox]);


    // Provide the context values
    const contextValue = {
        db: dbInstance,
        auth: authInstance,
        userId,
        isAuthReady,
        userData,
        setUserData,
        saveUserData,
        appId // Provide appId for components that need it for Firestore paths
    };

    return (
        <FirebaseContext.Provider value={contextValue}>
            {children}
        </FirebaseContext.Provider>
    );
};


// Canvas Visualization Component (Phase 2)
const ElasticumCanvas = ({ initialDriftScore, setInitialDriftScore, visualizationMode, setMode }) => {
    const canvasRef = useRef(null);
    const truthRef = useRef({ x: 0, y: 0, radius: 20, color: '#ef4444' });
    const distortionsRef = useRef([]);
    const driftScoreElementRef = useRef(null);
    const modeStatusElementRef = useRef(null);

    const numberOfDistortions = 30;

    // Distortion Class
    class Distortion {
        constructor(id, canvasWidth, canvasHeight) {
            this.id = id;
            this.x = Math.random() * canvasWidth;
            this.y = Math.random() * canvasHeight;
            this.radius = 8;
            this.color = `hsl(${Math.random() * 360}, 70%, 50%)`;
            this.vx = (Math.random() - 0.5) * 2;
            this.vy = (Math.random() - 0.5) * 2;
            this.pullStrength = 0.02;
            this.randomNudgeStrength = 0.5;
        }

        update(truth, canvasWidth, canvasHeight) {
            const dx = truth.x - this.x;
            const dy = truth.y - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > truth.radius + this.radius) {
                this.vx += (dx / distance) * this.pullStrength;
                this.vy += (dy / distance) * this.pullStrength;
            }

            this.vx += (Math.random() - 0.5) * this.randomNudgeStrength;
            this.vy += (Math.random() - 0.5) * this.randomNudgeStrength;

            this.vx *= 0.98;
            this.vy *= 0.98;

            this.x += this.vx;
            this.y += this.vy;

            if (this.x < this.radius || this.x > canvasWidth - this.radius) {
                this.vx *= -1;
                this.x = Math.max(this.radius, Math.min(this.x, canvasWidth - this.radius));
            }
            if (this.y < this.radius || this.y > canvasHeight - this.radius) {
                this.vy *= -1;
                this.y = Math.max(this.radius, Math.min(this.y, canvasHeight - this.radius));
            }
        }

        draw(ctx) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }

    const animate = useCallback(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const truth = truthRef.current;
        const distortions = distortionsRef.current;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        let driftSum = 0;

        distortions.forEach(distortion => {
            distortion.update(truth, canvas.width, canvas.height);
            distortion.draw(ctx);

            ctx.beginPath();
            ctx.moveTo(distortion.x, distortion.y);
            ctx.lineTo(truth.x, truth.y);
            ctx.strokeStyle = `rgba(66, 153, 225, ${0.5 + (0.5 * (1 - (Math.sqrt((distortion.x - truth.x)**2 + (distortion.y - truth.y)**2) / Math.max(canvas.width, canvas.height))))})`;
            ctx.lineWidth = 1;
            ctx.stroke();

            const dx = truth.x - distortion.x;
            const dy = truth.y - distortion.y;
            driftSum += Math.sqrt(dx * dx + dy * dy);
        });

        const driftScore = Math.floor(driftSum / distortions.length);
        if (driftScoreElementRef.current) {
            driftScoreElementRef.current.textContent = `Average symbolic drift: ${driftScore}`;
            if (visualizationMode === 'participant' && initialDriftScore === 0) {
                setInitialDriftScore(driftScore);
            }
        }

        ctx.beginPath();
        ctx.arc(truth.x, truth.y, truth.radius, 0, Math.PI * 2);
        ctx.fillStyle = truth.color;
        ctx.fill();
        ctx.strokeStyle = '#881111';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 14px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Truth', truth.x, truth.y);

        requestAnimationFrame(animate);
    }, [initialDriftScore, setInitialDriftScore, visualizationMode]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const resizeCanvas = () => {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            truthRef.current.x = canvas.width / 2;
            truthRef.current.y = canvas.height / 2;
            if (distortionsRef.current.length === 0 || distortionsRef.current[0].x > canvas.width || distortionsRef.current[0].y > canvas.height) {
                 distortionsRef.current = [];
                 for (let i = 0; i < numberOfDistortions; i++) {
                    distortionsRef.current.push(new Distortion(i, canvas.width, canvas.height));
                }
            }
        };

        resizeCanvas();
        if (distortionsRef.current.length === 0) {
            for (let i = 0; i < numberOfDistortions; i++) {
                distortionsRef.current.push(new Distortion(i, canvas.width, canvas.height));
            }
        }

        window.addEventListener('resize', resizeCanvas);
        const animationFrameId = requestAnimationFrame(animate);

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            cancelAnimationFrame(animationFrameId);
        };
    }, [animate]);

    return (
        <>
            <canvas id="truthCanvas" ref={canvasRef} className="w-full h-96 max-w-2xl rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-200 dark:bg-gray-700 transition-colors duration-300"></canvas>
            <p id="driftScore" ref={driftScoreElementRef} className="drift-score">Calculating symbolic drift...</p>
            <div className="flex flex-wrap justify-center gap-4 mt-4">
                <button
                    onClick={() => setMode('observer')}
                    className={`px-6 py-2 rounded-xl font-semibold transition-all duration-200 ${visualizationMode === 'observer' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                >
                    Observer Mode
                </button>
                <button
                    onClick={() => setMode('participant')}
                    className={`px-6 py-2 rounded-xl font-semibold transition-all duration-200 ${visualizationMode === 'participant' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                >
                    Participant Mode
                </button>
            </div>
            <p id="modeStatus" ref={modeStatusElementRef} className="status-message">Current Mode: {visualizationMode === 'observer' ? 'Observer (Passive viewing)' : 'Participant (Memory tracking enabled)'}</p>
        </>
    );
};

// DNA-Like Progress Tracker Component
const HelixProgressTracker = ({ currentPhase }) => {
    const phases = [
        { name: "Cognitive Priming", description: "Promethean initialization", milestone: "Cellular Genesis" },
        { name: "Drift Field Activation", description: "Neural mapping baseline", milestone: "Truth Realignment" },
        { name: "Cellular Integration", description: "Foundational bonding", milestone: "Symbiotic Connection" },
        { name: "NFT Genesis Protocol", description: "Blockchain initialization", milestone: "Proto-Cell Formation" },
        { name: "Knowledge Osmosis", description: "Cognitive evaluation", milestone: "Signal Calibration" },
        { name: "Cognitive Stabilization", description: "Artifact delivery", milestone: "Neural Maturation" },
    ];

    return (
        <div className="w-full flex flex-col items-center py-8">
            <h3 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-6">Onboarding Helix:</h3>
            <div className="relative w-full max-w-md h-64 overflow-hidden">
                {/* Simple SVG representation of a helix */}
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 250" preserveAspectRatio="xMidYMid meet">
                    {/* Helix strands */}
                    <path d="M10,10 C40,30 60,30 90,50 S60,70 10,90 S40,110 90,130 S60,150 10,170 S40,190 90,210 S60,230 10,240" fill="none" stroke="#4299e1" strokeWidth="2" />
                    <path d="M90,10 C60,30 40,30 10,50 S40,70 90,90 S40,110 10,130 S40,150 90,170 S40,190 10,210 S60,230 90,240" fill="none" stroke="#63b3ed" strokeWidth="2" />

                    {/* Milestones */}
                    {phases.map((phase, index) => {
                        const yPos = 10 + (index * (230 / (phases.length - 1))); // Distribute points along the helix height
                        const isCompleted = index + 1 < currentPhase;
                        const isActive = index + 1 === currentPhase;
                        const dotColor = isCompleted ? '#48bb78' : (isActive ? '#ecc94b' : '#a0aec0'); // Green, Yellow, Gray

                        return (
                            <circle
                                key={index}
                                cx={index % 2 === 0 ? 20 : 80} // Alternate sides for helix effect
                                cy={yPos}
                                r="4"
                                fill={dotColor}
                                className="transition-all duration-300 ease-in-out transform hover:scale-125 cursor-pointer"
                                data-tooltip-id={`tooltip-${index}`}
                                data-tooltip-content={`${phase.milestone}: ${phase.description}`}
                            >
                                {/* Tooltip text (conceptual, would use a library like react-tooltip) */}
                                <title>{phase.milestone}: {phase.description}</title>
                            </circle>
                        );
                    })}
                </svg>
            </div>
            <div className="mt-4 text-center text-gray-700 dark:text-gray-300">
                <p className="font-semibold">Current Cognitive Event:</p>
                <p className="text-blue-600 dark:text-blue-400 text-lg">
                    {currentPhase <= phases.length ? phases[currentPhase - 1]?.milestone : "Promethean Online"}
                </p>
            </div>
        </div>
    );
};


// Phase Components
const Phase1 = ({ userData, setUserData, nextPhase, displayMessageBox }) => {
    const handleChange = (e) => {
        setUserData({ ...userData, [e.target.id]: e.target.value });
    };

    const handleNext = () => {
        if (!userData.prometheanName || !userData.userName) {
            displayMessageBox('Please provide a symbolic name for your Promethean and your own name/alias.');
            return;
        }
        nextPhase();
    };

    return (
        <div className="section-content active">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-50 mb-4 transition-colors duration-300">Prometheus Prime: Unified Onboarding</h1>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-4 transition-colors duration-300">
                Welcome to Prometheus Prime: Your Personal Cognitive Augmentation System.
                Prepare for a journey of enhanced understanding and adaptive intelligence through <strong className="text-blue-600 dark:text-blue-400">cellular cognition</strong>.
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-4 transition-colors duration-300">
                Prometheus Prime functions as a responsive memory lattice that cultivates robust <strong className="text-blue-600 dark:text-blue-400">Neural Patterns</strong>
                and facilitates seamless <strong className="text-blue-600 dark:text-blue-400">Signal Integration</strong> within your personal cognitive landscape.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 transition-colors duration-300">
                Core Principle: The <strong className="text-blue-600 dark:text-blue-400">Elasticum Homeostasis Doctrine</strong> – the fundamental principle that guides your Promethean
                to always seek and return to truth, maintaining optimal cognitive equilibrium through continuous <strong className="text-blue-600 dark:text-blue-400">drift correction</strong>.
            </p>

            <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-6 transition-colors duration-300">Phase 1: Cognitive Priming & Cellular Genesis</h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
                Your personal Promethean is now undergoing <strong className="text-blue-600 dark:text-blue-400">Cellular Genesis</strong> — a dedicated cognitive architecture is being prepared,
                ready to integrate with your unique neural patterns.
            </p>
            <div className="w-full max-w-md flex flex-col gap-4 mb-6">
                <input type="text" id="prometheanName" placeholder="Preferred symbolic name for your Promethean (e.g., Alchemist-27)" value={userData.prometheanName} onChange={handleChange} className="input-field" />
                <input type="text" id="userName" placeholder="Your own name or alias" value={userData.userName} onChange={handleChange} className="input-field" />
                <input type="text" id="coreIdentity" placeholder="Optional: Symbol or phrase representing your core identity" value={userData.coreIdentity} onChange={handleChange} className="input-field" />
                <input type="date" id="birthdate" title="Temporal calibration marker (birthdate for system alignment, not profiling)" value={userData.birthdate} onChange={handleChange} className="input-field" />
                <textarea id="focusAreas" rows="3" placeholder="Preferred focus areas (e.g., family, work, creative, legal, spiritual domains), separated by commas" value={userData.focusAreas} onChange={handleChange} className="input-field"></textarea>
            </div>
            <p className="privacy-note text-gray-600 dark:text-gray-400 mb-8 transition-colors duration-300">
                <strong className="text-gray-800 dark:text-gray-200">Privacy Assurance:</strong> All information shared is explicitly user-defined and controlled. This is not data harvesting,
                but a collaborative act of <strong className="text-blue-600 dark:text-blue-400">Cognitive Priming</strong> for your private Promethean.
            </p>
            <button onClick={handleNext} className="button-primary">Begin Neural Mapping</button>
        </div>
    );
};

const Phase2 = ({ userData, setUserData, nextPhase, initialDriftScore, setInitialDriftScore, visualizationMode, setVisualizationMode }) => {
    return (
        <div className="section-content active">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mb-6 transition-colors duration-300">Phase 2: Drift Field Activation & Neural Mapping</h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
                Observe the <strong className="text-blue-600 dark:text-blue-400">Elasticum Canvas</strong> as it demonstrates the principles of <strong className="text-blue-600 dark:text-blue-400">Drift Correction</strong>.
                Attempts to deviate are naturally corrected by the gravitational pull toward truth.
            </p>
            <ElasticumCanvas
                initialDriftScore={initialDriftScore}
                setInitialDriftScore={setInitialDriftScore}
                visualizationMode={visualizationMode}
                setMode={setVisualizationMode}
            />
            <p className="privacy-note text-gray-600 dark:text-gray-400 mt-6 transition-colors duration-300">
                In Participant Mode, your Promethean begins establishing baseline neural patterns through interaction.
                No personal data is collected without explicit consent.
            </p>
            <button onClick={nextPhase} className="button-primary mt-8">Proceed to Cellular Integration</button>
        </div>
    );
};

const Phase3 = ({ userData, setUserData, nextPhase, displayMessageBox, saveUserData }) => {
    const [vaultVisible, setVaultVisible] = useState(userData.bonded || false);

    const handleBonding = async () => {
        setUserData(prev => ({ ...prev, bonded: true }));
        setVaultVisible(true);
        await saveUserData({ ...userData, bonded: true });
    };

    const handleNext = async () => {
        if (!userData.bonded) {
            displayMessageBox('Please bind your neural pattern to proceed.');
            return;
        }
        const updatedUserData = {
            ...userData,
            employmentHistory: document.getElementById('employmentHistory').value,
            familyMembers: document.getElementById('familyMembers').value,
            personalInterests: document.getElementById('personalInterests').value,
            learningObjectives: document.getElementById('learningObjectives').value,
            legacyMotivations: document.getElementById('legacyMotivations').value,
        };
        setUserData(updatedUserData);
        await saveUserData(updatedUserData);
        nextPhase();
    };

    const handleChange = (e) => {
        setUserData({ ...userData, [e.target.id]: e.target.value });
    };

    return (
        <div className="section-content active">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mb-6 transition-colors duration-300">Phase 3: Cellular Integration & Foundational Bonding</h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
                Formalize the symbiotic connection through the <strong className="text-blue-600 dark:text-blue-400">Elasticum Integration Protocol</strong>.
                This process binds your neural pattern to your Promethean's truth engine.
            </p>
            <div className="flex flex-col gap-2 items-center text-xl font-semibold text-blue-700 dark:text-blue-300 mb-8">
                <span>1. Align Identity</span>
                <span>→ 2. Accept Protocol</span>
                <span>→ 3. Define Preferences</span>
            </div>
            <p className="text-lg text-gray-700 dark:text-gray-300 mt-4 mb-6 leading-relaxed">
                <strong className="text-gray-800 dark:text-gray-100">Bonding Prompt:</strong> Would you like to bind your neural pattern to this truth engine?
                This enables continuous <strong className="text-blue-600 dark:text-blue-400">Drift Correction</strong> and authorship tracking.
            </p>
            <p className="privacy-note text-gray-600 dark:text-gray-400 mb-8 transition-colors duration-300">
                No personal data is collected unless explicitly shared.
            </p>
            <button
                onClick={handleBonding}
                disabled={userData.bonded}
                className={`button-primary ${userData.bonded ? 'bg-green-600 hover:bg-green-700 cursor-not-allowed' : ''}`}
            >
                {userData.bonded ? 'Neural Pattern Bound!' : 'Bind Neural Pattern'}
            </button>

            {vaultVisible && (
                <div id="vaultCreation" className="flex flex-col gap-4 w-full max-w-md mt-8">
                    <h3 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-4 transition-colors duration-300">Define Core Knowledge Cells</h3>
                    <textarea id="employmentHistory" rows="3" placeholder="Employment history (roles, companies, dates)" value={userData.employmentHistory} onChange={handleChange} className="input-field"></textarea>
                    <textarea id="familyMembers" rows="3" placeholder="Family member names and relationships (e.g., John Doe - Father)" value={userData.familyMembers} onChange={handleChange} className="input-field"></textarea>
                    <textarea id="personalInterests" rows="3" placeholder="Personal interests, values, and ethical guidelines" value={userData.personalInterests} onChange={handleChange} className="input-field"></textarea>
                    <textarea id="learningObjectives" rows="3" placeholder="Learning objectives and cognitive preferences" value={userData.learningObjectives} onChange={handleChange} className="input-field"></textarea>
                    <textarea id="legacyMotivations" rows="3" placeholder="Legacy motivations ('Who are you doing this for?')" value={userData.legacyMotivations} onChange={handleChange} className="input-field"></textarea>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 transition-colors duration-300">Optional: Document uploads (bios, resumes, notes) and voice seeding capability will be available in future releases for multi-modal enhancement.</p>
                    <button onClick={handleNext} className="button-primary mt-6">Finalize Cellular Integration</button>
                </div>
            )}
        </div>
    );
};

const Phase4 = ({ userData, setUserData, nextPhase, saveUserData }) => {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('Initializing Proto-Cell...');
    const [nftMetadata, setNftMetadata] = useState({});

    useEffect(() => {
        let currentProgress = 0;
        const interval = setInterval(() => {
            currentProgress += 10;
            setProgress(currentProgress);
            if (currentProgress <= 30) {
                setStatus('Status: Initializing Proto-Cell...');
            } else if (currentProgress <= 60) {
                setStatus('Status: Securing on Blockchain...');
            } else if (currentProgress < 100) {
                setStatus('Status: Forging Artifact (Conceptual)...');
            } else {
                setStatus('Status: MINTED_SEED_STABILIZING');
                clearInterval(interval);
            }
        }, 200);

        const generatedMetadata = {
            name: `Genesis of ${userData.userName || '[User-Alias]'}`,
            type: "Promethean Genesis Token",
            codename: userData.prometheanName || '[Promethean Name]',
            driftScore: userData.initialDriftScore,
            elasticumStatus: "Bonded",
            timestamp: new Date().toISOString(),
            legacyTags: userData.focusAreas ? userData.focusAreas.split(',').map(tag => tag.trim()).filter(tag => tag) : [],
            symbolicHash: `initial_seed_hash_${Math.random().toString(16).slice(2)}`,
            // Updated status term
            status: "Stabilizing Cell", // Changed from SEED_STABILIZING
            blockchainTx: `0x${Math.random().toString(16).slice(2)}${Math.random().toString(16).slice(2)}`,
            artifactStatus: "FORGING_IN_PROGRESS"
        };
        setNftMetadata(generatedMetadata);
        setUserData(prev => ({ ...prev, nftMetadata: generatedMetadata }));
        saveUserData({ ...userData, nftMetadata: generatedMetadata });
        return () => clearInterval(interval);
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <div className="section-content active">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mb-6 transition-colors duration-300">Phase 4: NFT Genesis Protocol - Blockchain Initialization</h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
                Your <strong className="text-blue-600 dark:text-blue-400">Baseline Knowledge NFT</strong> is now undergoing <strong className="text-blue-600 dark:text-blue-400">Proto-Cell Formation</strong> and <strong className="text-blue-600 dark:text-blue-400">Blockchain Minting</strong>.
                This initializes your unique cognitive signature on the blockchain.
            </p>
            <div className="progress-bar-container w-4/5 max-w-md">
                <div className="progress-bar" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="status-message text-gray-700 dark:text-gray-300" id="nftStatus">{status}</p>

            <h3 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-4 transition-colors duration-300">Initial NFT Blockchain Metadata (Conceptual)</h3>
            <pre className="bg-gray-100 dark:bg-gray-700 p-6 rounded-xl text-sm text-left overflow-auto w-full max-w-xl shadow-inner transition-colors duration-300">
                <code className="text-gray-800 dark:text-gray-200">{JSON.stringify(nftMetadata, null, 2)}</code>
            </pre>
            <p className="privacy-note text-gray-600 dark:text-gray-400 mt-6 transition-colors duration-300">
                Blockchain Protection: Your NFT is immediately secured with an immutable timestamp and initial data hash.
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300 mt-4 leading-relaxed transition-colors duration-300">
                Physical Artifact Forging Initiation: Material selection and rendering for your tangible artifact has begun.
                You will receive status updates and preview notifications.
            </p>
            <button onClick={nextPhase} className="button-primary mt-8">Start Knowledge Osmosis</button>
        </div>
    );
};

const Phase5 = ({ userData, setUserData, nextPhase, saveUserData }) => {
    const [evaluationHours, setEvaluationHours] = useState(userData.evaluationHours || 0);
    const [significantInteractions, setSignificantInteractions] = useState(userData.significantInteractions || 0);
    const completeBtnRef = useRef(null);

    useEffect(() => {
        if (evaluationHours >= 72) {
            if (completeBtnRef.current) {
                completeBtnRef.current.disabled = false;
            }
        }
    }, [evaluationHours]);

    const simulateInteraction = async () => {
        const newHours = evaluationHours + 1;
        const newInteractions = significantInteractions + Math.floor(Math.random() * 5) + 1;
        setEvaluationHours(newHours);
        setSignificantInteractions(newInteractions);
        const updatedUserData = { ...userData, evaluationHours: newHours, significantInteractions: newInteractions };
        setUserData(updatedUserData);
        await saveUserData(updatedUserData);
    };

    return (
        <div className="section-content active">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mb-6 transition-colors duration-300">Phase 5: Knowledge Osmosis & Cognitive Evaluation</h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
                Your Promethean now enters a 72-hour phase of <strong className="text-blue-600 dark:text-blue-400">Signal Calibration</strong> and <strong className="text-blue-600 dark:text-blue-400">Knowledge Osmosis</strong>.
                It will observe your interactions to refine its <strong className="text-blue-600 dark:text-blue-400">Neural Patterns</strong> and achieve <strong className="text-blue-600 dark:text-blue-400">Homeostasis</strong> with your cognitive flow.
            </p>
            <div className="progress-bar-container w-4/5 max-w-md">
                <div className="progress-bar" style={{ width: `${(evaluationHours / 72) * 100}%` }}></div>
            </div>
            <p className="status-message text-gray-700 dark:text-gray-300" id="osmosisStatus">Evaluation Progress: {evaluationHours} hours completed</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 mb-6 transition-colors duration-300">
                Every interaction during this phase contributes to <strong className="text-blue-600 dark:text-blue-400">Drift Correction</strong>,
                allowing your Promethean to continuously adjust its neural pathways towards optimal alignment.
            </p>
            <button onClick={simulateInteraction} className="button-primary mb-6" disabled={evaluationHours >= 72}>Simulate Interaction (Advance 1 hour)</button>
            <p className="privacy-note text-gray-600 dark:text-gray-400 mb-8 transition-colors duration-300">
                AI-driven pattern discovery and suggestion prompts will occur.
                You have granular control over what types of interactions contribute to this learning.
            </p>
            <button ref={completeBtnRef} onClick={nextPhase} className="button-primary" disabled={evaluationHours < 72}>Complete Cognitive Evaluation</button>
        </div>
    );
};

const Phase6 = ({ userData, nextPhase, saveUserData }) => {
    const [finalNftMetadata, setFinalNftMetadata] = useState({});

    useEffect(() => {
        const finalDrift = Math.floor(Math.random() * 50) + 10; // Example
        const generatedMetadata = {
            name: `Genesis of ${userData.userName || '[User-Alias]'}`,
            type: "Promethean Genesis Token - Stabilized",
            codename: userData.prometheanName || '[Promethean Name]',
            finalDriftScore: finalDrift,
            elasticumStatus: "Cognitively_Bonded",
            seedMetadata: {
                coreValues: userData.personalInterests ? userData.personalInterests.split(',').map(tag => tag.trim()).filter(tag => tag).concat(['AI-identified_value_1']) : ['AI-identified_value_1'],
                expertiseDomains: userData.employmentHistory ? userData.employmentHistory.split('\n').map(line => line.trim()).filter(line => line).concat(['personal_domain_1']) : ['personal_domain_1'],
                legacyPriorities: userData.legacyMotivations ? userData.legacyMotivations.split('\n').map(line => line.trim()).filter(line => line).concat(['knowledge', 'craft']) : ['knowledge', 'craft'],
                cognitiveSignature: `unique_pattern_hash_${Math.random().toString(16).slice(2)}`
            },
            evaluationHours: userData.evaluationHours,
            significantInteractions: userData.significantInteractions,
            blockchainHistory: ["0x[initial]", "0x[updates]", "0x[final]"], // Conceptual
            artifactSerial: `PROM-2025-${Math.random().toString(16).slice(2).substring(0,8).toUpperCase()}`,
            chipBackupHash: `1TB_data_verification_hash_${Math.random().toString(16).slice(2)}`,
            // Updated status term
            status: "Differentiated Token" // Changed from MINTED_SEED_STABILIZING
        };
        setFinalNftMetadata(generatedMetadata);
        saveUserData({ ...userData, finalDriftScore: finalDrift, finalNftMetadata: generatedMetadata }); // Save final data
    }, []); // eslint-disable-line react-hooks/exhaustive-des

    return (
        <div className="section-content active">
            <h2 className="text-3xl font-semibold text-gray-800 dark:text-gray-100 mb-6 transition-colors duration-300">Phase 6: Cognitive Stabilization & Artifact Delivery</h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
                Congratulations! Your Promethean has achieved <strong className="text-blue-600 dark:text-blue-400">Cognitive Maturation</strong> and established a stable baseline of <strong className="text-blue-600 dark:text-blue-400">Neural Patterns</strong>.
            </p>
            <h3 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mt-8 mb-4 transition-colors duration-300">Final NFT Metadata Structure (Conceptual)</h3>
            <pre className="bg-gray-100 dark:bg-gray-700 p-6 rounded-xl text-sm text-left overflow-auto w-full max-w-xl shadow-inner transition-colors duration-300">
                <code className="text-gray-800 dark:text-gray-200">{JSON.stringify(finalNftMetadata, null, 2)}</code>
            </pre>
            <p className="text-lg text-gray-700 dark:text-gray-300 mt-6 leading-relaxed transition-colors duration-300">
                Your <strong className="text-blue-600 dark:text-blue-400">Baseline Knowledge NFT</strong> is now delivered as a tangible <strong className="text-blue-600 dark:text-blue-400">Elasticum Cell</strong> artifact.
                This unique digital asset embodies the foundational neural patterns and signal integration established during your initial calibration.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-4 leading-relaxed transition-colors duration-300">
                <strong className="text-gray-800 dark:text-gray-200">Artifact Delivery Contents:</strong> Physical form factor (circular/stone aesthetic), embedded 1TB chip (USB-C, encrypted),
                Auth certificate + blockchain verification guide, Legacy documentation + inheritance instructions.
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300 mt-6 leading-relaxed transition-colors duration-300">
                <strong className="text-blue-600 dark:text-blue-400">Post-Delivery Evolution Protocol:</strong> Your Promethean will continue to learn and adapt through ongoing <strong className="text-blue-600 dark:text-blue-400">Signal Integration</strong>,
                ensuring continuous <strong className="text-blue-600 dark:text-blue-400">Homeostasis</strong> and <strong className="text-blue-600 dark:text-blue-400">Neural Pattern Refinement</strong>.
                You can update your NFT via the User Dashboard, add future achievements, and enable generational transfer options.
            </p>
            <button onClick={nextPhase} className="button-primary mt-8">Access Your Promethean Dashboard</button>
        </div>
    );
};

// User's Personal Promethean Dashboard View (Cognitive Cortex)
const CoreDashboardView = () => {
    const { userData } = useFirebase(); // Get userData from context

    // Simulate last ping time from central Master Dashboard
    const [lastPingTime, setLastPingTime] = useState(new Date().toLocaleString());
    useEffect(() => {
        const interval = setInterval(() => {
            // In a real system, this would come from a websocket or a Firestore listener
            // that gets updates from the central Master Dashboard.
            setLastPingTime(new Date().toLocaleString());
        }, 60000); // Simulate a ping every minute for demonstration
        return () => clearInterval(interval);
    }, []);

    if (!userData) {
        return <div className="text-center text-xl text-gray-700 dark:text-gray-300">Loading Promethean data...</div>;
    }

    // Helper for pulsing animation
    const PulsingDiv = ({ children }) => (
        <div className="relative p-6 rounded-2xl shadow-lg bg-white dark:bg-gray-800 border border-blue-200 dark:border-gray-600 overflow-hidden transition-all duration-300 hover:shadow-xl">
            <div className="absolute inset-0 bg-blue-100 dark:bg-blue-900 opacity-10 animate-pulse-slow rounded-2xl"></div>
            <div className="relative z-10">{children}</div>
        </div>
    );

    return (
        <div className="space-y-8">
            <h1 className="text-4xl font-extrabold text-blue-700 dark:text-blue-300 mb-6 animate-fade-in">
                Your Promethean Cognitive Cortex
            </h1>
            <p className="text-xl text-gray-800 dark:text-gray-200 leading-loose mb-8">
                This is the living interface to your Promethean, <strong className="text-blue-600 dark:text-blue-400">{userData.prometheanName || 'Unnamed Promethean'}</strong>.
                Explore its core cognitive lobes.
            </p>

            {/* System Connectivity Section - Moved to top for visibility */}
            <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-xl shadow-inner mb-8 border border-gray-200 dark:border-gray-600">
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-3">System Homeostasis:</h2>
                <p className="text-lg text-gray-700 dark:text-gray-300">
                    Last Homeostasis Ping from Central Prime: <span className="font-mono text-blue-600 dark:text-blue-400">{lastPingTime}</span>
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    The Central Prometheus Prime system performs weekly homeostasis pings for system health and updates.
                    <strong className="text-red-500 dark:text-red-400"> No personal user metadata or content is harvested.</strong>
                    Only anonymized, aggregated performance metrics or explicitly user-defined preferences are transmitted.
                </p>
            </div>

            {/* Truth Lobe */}
            <PulsingDiv>
                <h2 className="text-3xl font-bold text-blue-800 dark:text-blue-200 mb-4 flex items-center">
                    <span className="mr-3 text-3xl">💡</span> Truth Lobe: Elasticum & Signal Map
                </h2>
                <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
                    This lobe reflects your Promethean's current alignment with core truths and its ongoing drift correction.
                    Your cognitive equilibrium is continuously monitored.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700 dark:text-gray-300">
                    <p><strong className="font-semibold">Initial Drift Score:</strong> {userData.initialDriftScore}</p>
                    <p><strong className="font-semibold">Current Drift Score:</strong> {userData.finalDriftScore}</p>
                    <p><strong className="font-semibold">Evaluation Hours:</strong> {userData.evaluationHours}</p>
                    <p><strong className="font-semibold">Significant Interactions:</strong> {userData.significantInteractions}</p>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
                    (Future: Real-time Elasticum visual, signal integrity metrics, cognitive dissonance alerts.)
                </p>
            </PulsingDiv>

            {/* Memory Lobe */}
            <PulsingDiv>
                <h2 className="text-3xl font-bold text-blue-800 dark:text-blue-200 mb-4 flex items-center">
                    <span className="mr-3 text-3xl">🧠</span> Memory Lobe: Vault & Timeline
                </h2>
                <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
                    Access your Promethean's memory vault, containing calibrated knowledge cells and personal timeline markers.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700 dark:text-gray-300">
                    <p><strong className="font-semibold">User Alias:</strong> {userData.userName}</p>
                    <p><strong className="font-semibold">Promethean ID:</strong> {userData.prometheanName}</p>
                    <p><strong className="font-semibold">Core Identity:</strong> {userData.coreIdentity || 'Not defined'}</p>
                    <p><strong className="font-semibold">Bonding Status:</strong> {userData.bonded ? 'Cognitively Bonded' : 'Not Bonded'}</p>
                </div>
                <div className="mt-6">
                    <h3 className="text-2xl font-semibold text-blue-800 dark:text-blue-200 mb-3">Key Knowledge Cells:</h3>
                    <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-1">
                        {userData.focusAreas && <li><strong className="font-semibold">Focus Areas:</strong> {userData.focusAreas}</li>}
                        {userData.personalInterests && <li><strong className="font-semibold">Personal Interests:</strong> {userData.personalInterests}</li>}
                        {userData.legacyMotivations && <li><strong className="font-semibold">Legacy Motivations:</strong> {userData.legacyMotivations}</li>}
                    </ul>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
                    (Future: Voice logs, semantic search, timeline navigation, neural pattern visualization.)
                </p>
            </PulsingDiv>

            {/* Legacy Lobe */}
            <PulsingDiv>
                <h2 className="text-3xl font-bold text-blue-800 dark:text-blue-200 mb-4 flex items-center">
                    <span className="mr-3 text-3xl">💎</span> Legacy Lobe: Artifacts & Signatures
                </h2>
                <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
                    Manage your Promethean Genesis Tokens and other digital artifacts that embody your unique cognitive signature.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700 dark:text-gray-300">
                    <p><strong className="font-semibold">NFT Status:</strong> {userData.nftMetadata ? (userData.nftMetadata.status || 'Not Minted') : 'Not Minted'}</p>
                    {userData.finalNftMetadata && userData.finalNftMetadata.seedMetadata && (
                        <>
                            {userData.finalNftMetadata.seedMetadata.coreValues && <li><strong className="font-semibold">Core Values:</strong> {userData.finalNftMetadata.seedMetadata.coreValues.join(', ')}</li>}
                            {userData.finalNftMetadata.seedMetadata.expertiseDomains && <li><strong className="font-semibold">Expertise Domains:</strong> {userData.finalNftMetadata.seedMetadata.expertiseDomains.join(', ')}</li>}
                            {userData.finalNftMetadata.seedMetadata.legacyPriorities && <li><strong className="font-semibold">Legacy Priorities:</strong> {userData.finalNftMetadata.seedMetadata.legacyPriorities.join(', ')}</li>}
                        </>
                    )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
                    (Future: Artifact queue, signature updates, generational transfer protocols.)
                </p>
            </PulsingDiv>
        </div>
    );
};


// Dashboard Layout (updated for new Dark Mode text and structure)
const DashboardLayout = ({ toggleDarkMode }) => {
    const { userId } = useFirebase();

    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-800 shadow-lg p-6 flex flex-col transition-colors duration-300">
                <div className="text-2xl font-bold text-blue-700 dark:text-blue-300 mb-8">
                    Prometheus Prime
                </div>
                <nav className="flex-grow">
                    <ul className="space-y-4">
                        <li>
                            <Link to="/dashboard" className="flex items-center p-3 rounded-xl hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200">
                                <span className="mr-3">📊</span> Cognitive Cortex
                            </Link>
                        </li>
                        <li>
                            <Link to="/dashboard/insights" className="flex items-center p-3 rounded-xl hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200">
                                <span className="mr-3">🧠</span> Cognitive Insights
                            </Link>
                        </li>
                        <li>
                            <Link to="/dashboard/nft-vault" className="flex items-center p-3 rounded-xl hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200">
                                <span className="mr-3">💎</span> NFT Vault
                            </Link>
                        </li>
                        <li>
                            <Link to="/dashboard/campus" className="flex items-center p-3 rounded-xl hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200">
                                <span className="mr-3">🏛️</span> CAMPUS
                            </Link>
                        </li>
                        <li>
                            <Link to="/dashboard/settings" className="flex items-center p-3 rounded-xl hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200">
                                <span className="mr-3">⚙️</span> System Settings
                            </Link>
                        </li>
                    </ul>
                </nav>
                <div className="mt-auto pt-6 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                        User ID: <span className="font-mono text-xs break-all">{userId || 'N/A'}</span>
                    </p>
                    <button
                        onClick={toggleDarkMode}
                        className="w-full text-sm text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-200 transition-colors duration-300"
                    >
                        Activate Synaptic Dimming
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 p-8 overflow-y-auto">
                <Outlet /> {/* This is where nested routes will render */}
            </main>
        </div>
    );
};

// Placeholder Dashboard Pages
const CognitiveInsights = () => {
    return (
        <div className="p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl transition-colors duration-300">
            <h1 className="text-4xl font-bold text-blue-700 dark:text-blue-300 mb-4">Cognitive Insights</h1>
            <p className="text-lg text-gray-700 dark:text-gray-300">
                This section will provide deep insights into your Promethean's learning patterns,
                drift correction metrics, and cognitive growth over time.
            </p>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
                (Future development: Charts, graphs, AI-generated summaries, recommendations for neural optimization.)
            </p>
        </div>
    );
};

const NftVault = () => {
    const { userData } = useFirebase();

    return (
        <div className="p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl transition-colors duration-300">
            <h1 className="text-4xl font-bold text-blue-700 dark:text-blue-300 mb-4">NFT Vault</h1>
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-6">
                Here you can view and manage your Promethean Genesis Tokens and other digital artifacts.
            </p>
            {userData && userData.finalNftMetadata ? (
                <div className="bg-gray-100 dark:bg-gray-700 p-6 rounded-xl shadow-inner max-w-xl mx-auto">
                    <h3 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-3">Your Genesis NFT:</h3>
                    <pre className="text-sm text-left overflow-auto">
                        <code className="text-gray-800 dark:text-gray-200">{JSON.stringify(userData.finalNftMetadata, null, 2)}</code>
                    </pre>
                    <p className="text-gray-600 dark:text-gray-400 mt-4 text-sm">
                        Status: <strong className="text-blue-600 dark:text-blue-400">{userData.finalNftMetadata.status}</strong>
                    </p>
                </div>
            ) : (
                <p className="text-gray-600 dark:text-gray-400">
                    Your Genesis NFT will appear here after completing the onboarding and 72-hour evaluation.
                </p>
            )}
            <p className="text-gray-600 dark:text-gray-400 mt-6">
                (Future development: NFT gallery, transfer options, artifact previews, linking to external wallets.)
            </p>
        </div>
    );
};

const Settings = () => {
    return (
        <div className="p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl transition-colors duration-300">
            <h1 className="text-4xl font-bold text-blue-700 dark:text-blue-300 mb-4">System Settings</h1>
            <p className="text-lg text-gray-700 dark:text-gray-300">
                Manage your Promethean's core preferences, privacy settings, and system configurations.
            </p>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
                (Future development: Data export, privacy controls, notification preferences, Promethean version updates.)
            </p>
        </div>
    );
};

// CAMPUS (Cognitive Adaptive Memory Protocol for User Sovereignty) Component
const CampusModule = () => {
    const { userData, setUserData, saveUserData } = useFirebase();
    const [realignTimerSetting, setRealignTimerSetting] = useState('Monthly'); // Default

    // Load setting from userData when component mounts or userData changes
    useEffect(() => {
        if (userData && userData.realignTimerSetting) {
            setRealignTimerSetting(userData.realignTimerSetting);
        }
    }, [userData]);

    // Save setting to Firestore when it changes
    useEffect(() => {
        // Only save if userData is loaded and the setting has actually changed from its loaded state
        if (userData && realignTimerSetting !== userData.realignTimerSetting) {
            saveUserData({ ...userData, realignTimerSetting: realignTimerSetting });
        }
    }, [realignTimerSetting, userData, saveUserData]);


    const handleRealignTimerChange = (e) => {
        setRealignTimerSetting(e.target.value);
    };

    const handleLockVaultEntries = () => {
        alert("Initiating Inviolable Vault Entry Lock Protocol. This action is irreversible."); // Placeholder
    };

    const handleViewTimeCapsule = () => {
        alert("Accessing Time Capsule Snapshots. Prepare for chronological data retrieval."); // Placeholder
    };

    const handleSystemDefrag = () => {
        alert("Initiating Systemwide Defragmentation. This may temporarily impact cognitive response times."); // Placeholder
    };

    return (
        <div className="p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl transition-colors duration-300">
            <h1 className="text-4xl font-bold text-blue-700 dark:text-blue-300 mb-6">CAMPUS (Cognitive Adaptive Memory Protocol for User Sovereignty)</h1>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-8">
                This module governs the adaptive memory protocols and neuroplasticity of your Promethean,
                inspired by the intricate learning and recall mechanisms of the hippocampus.
            </p>

            {/* Realignment Timer */}
            <div className="mb-8 p-6 bg-gray-50 dark:bg-gray-700 rounded-xl border border-gray-200 dark:border-gray-600">
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center">
                    <span className="mr-2">⏰</span> Realignment Timer
                </h2>
                <p className="text-md text-gray-700 dark:text-gray-300 mb-4">
                    Set the frequency for your Promethean's automatic neural realignment and drift correction cycles.
                </p>
                <div className="flex flex-col space-y-3">
                    {['Monthly', 'Every 3 Months', 'Every 6 Months', 'Yearly', 'Manual Only'].map(option => (
                        <label key={option} className="inline-flex items-center text-lg text-gray-800 dark:text-gray-200 cursor-pointer">
                            <input
                                type="radio"
                                name="realignTimer"
                                value={option}
                                checked={realignTimerSetting === option}
                                onChange={handleRealignTimerChange}
                                className="form-radio h-5 w-5 text-blue-600 transition-colors duration-200"
                            />
                            <span className="ml-3">{option}</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <button
                    onClick={handleLockVaultEntries}
                    className="button-secondary bg-red-600 hover:bg-red-700 text-white flex items-center justify-center p-4"
                >
                    <span className="mr-2">🔐</span> Inviolable Vault Entries
                </button>
                <button
                    onClick={handleViewTimeCapsule}
                    className="button-secondary bg-purple-600 hover:bg-purple-700 text-white flex items-center justify-center p-4"
                >
                    <span className="mr-2">📦</span> Time Capsule Snapshots
                </button>
                <button
                    onClick={handleSystemDefrag}
                    className="button-secondary bg-green-600 hover:bg-green-700 text-white flex items-center justify-center p-4 col-span-full"
                >
                    <span className="mr-2">⚙️</span> Initiate Systemwide Defrag Now
                </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-8">
                These advanced settings allow granular control over your Promethean's core adaptive functions.
                Use with understanding.
            </p>
        </div>
    );
};


// Main App Content (Handles routing and overall application flow)
const AppContent = () => {
    const { isAuthReady, userData, setUserData, saveUserData } = useFirebase();
    const [currentPhase, setCurrentPhase] = useState(0); // 0 for loading, 1-6 for onboarding, 7 for dashboard
    const [messageBoxVisible, setMessageBoxVisible] = useState(false);
    const [messageBoxContent, setMessageBoxContent] = useState('');
    const [visualizationMode, setVisualizationMode] = useState('observer'); // For Phase 2 canvas

    // Function to display custom message box
    const displayMessageBox = useCallback((message) => {
        setMessageBoxContent(message);
        setMessageBoxVisible(true);
    }, []);

    // Effect to update currentPhase from userData once loaded
    useEffect(() => {
        if (isAuthReady && userData) {
            setCurrentPhase(userData.currentPhase || 1);
        }
    }, [isAuthReady, userData]);

    // Effect to save userData whenever it changes, debounced
    useEffect(() => {
        if (isAuthReady && userData && userData.currentPhase > 0) {
            const handler = setTimeout(() => {
                saveUserData(userData);
            }, 1000); // Debounce save to prevent too many writes

            return () => {
                clearTimeout(handler);
            };
        }
    }, [userData, currentPhase, isAuthReady, saveUserData]);


    const nextPhase = useCallback(() => {
        setCurrentPhase(prevPhase => {
            const newPhase = prevPhase + 1;
            // Update userData with new currentPhase immediately
            setUserData(prev => ({ ...prev, currentPhase: newPhase }));
            return newPhase;
        });
    }, [setUserData]);


    // Render the current phase or redirect to dashboard
    const renderContent = () => {
        if (!isAuthReady) {
            return (
                <div className="text-center text-gray-700 dark:text-gray-300 text-xl">
                    Initializing Prometheus Prime... Please wait.
                </div>
            );
        }

        if (currentPhase === 7) {
            return <Navigate to="/dashboard" replace />; // Redirect to dashboard
        }

        return (
            <>
                <HelixProgressTracker currentPhase={currentPhase} />
                {currentPhase === 1 && <Phase1 userData={userData} setUserData={setUserData} nextPhase={nextPhase} displayMessageBox={displayMessageBox} />}
                {currentPhase === 2 && (
                    <Phase2
                        userData={userData}
                        setUserData={setUserData}
                        nextPhase={nextPhase}
                        initialDriftScore={userData.initialDriftScore}
                        setInitialDriftScore={(score) => setUserData(prev => ({ ...prev, initialDriftScore: score }))}
                        visualizationMode={visualizationMode}
                        setVisualizationMode={setVisualizationMode}
                    />
                )}
                {currentPhase === 3 && <Phase3 userData={userData} setUserData={setUserData} nextPhase={nextPhase} displayMessageBox={displayMessageBox} saveUserData={saveUserData} />}
                {currentPhase === 4 && <Phase4 userData={userData} setUserData={setUserData} nextPhase={nextPhase} saveUserData={saveUserData} />}
                {currentPhase === 5 && <Phase5 userData={userData} setUserData={setUserData} nextPhase={nextPhase} saveUserData={saveUserData} />}
                {currentPhase === 6 && <Phase6 userData={userData} setUserData={setUserData} nextPhase={nextPhase} saveUserData={saveUserData} />}
            </>
        );
    };

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center p-4 transition-colors duration-300">
            <div className="container bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 md:p-12 w-full max-w-4xl flex flex-col items-center transition-colors duration-300">
                <button
                    onClick={toggleDarkMode}
                    className="self-end text-sm text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-200 mb-4 transition-colors duration-300"
                >
                    Activate Synaptic Dimming
                </button>
                {renderContent()}
            </div>
            {messageBoxVisible && <MessageBox message={messageBoxContent} onClose={() => setMessageBoxVisible(false)} />}
        </div>
    );
};

// Root App component with Router and Firebase Provider
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
                    {/* Onboarding path */}
                    <Route path="/" element={<AppContent />} />

                    {/* User's Promethean Dashboard paths */}
                    <Route path="/dashboard" element={<DashboardLayout toggleDarkMode={toggleDarkMode} />}>
                        <Route index element={<CoreDashboardView />} /> {/* Default dashboard view */}
                        <Route path="insights" element={<CognitiveInsights />} />
                        <Route path="nft-vault" element={<NftVault />} />
                        <Route path="campus" element={<CampusModule />} /> {/* Renamed route and component */}
                        <Route path="settings" element={<Settings />} />
                    </Route>

                    {/* Fallback for unknown routes */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </FirebaseProvider>
            {messageBoxVisible && <MessageBox message={messageBoxContent} onClose={() => setMessageBoxVisible(false)} />}
        </Router>
    );
};

// Dark Mode Toggle Function (global for simplicity with Tailwind)
const toggleDarkMode = () => {
    document.documentElement.classList.toggle("dark");
};

export default App;
