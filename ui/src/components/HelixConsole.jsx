import React, { useState, useEffect } from 'react';
import './HelixConsole.css';

const HelixConsole = () => {
  const [input, setInput] = useState('');
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  // Check Helix system status on component mount
  useEffect(() => {
    checkHelixStatus();
  }, []);

  const checkHelixStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/helix/status');
      const data = await response.json();
      setSystemStatus(data);
      setConnectionStatus(data.available ? 'connected' : 'unavailable');
    } catch (error) {
      console.error('Failed to check Helix status:', error);
      setConnectionStatus('error');
    }
  };

  const processInput = async () => {
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    const currentInput = input;
    setInput('');

    try {
      const response = await fetch('http://localhost:5000/helix/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: currentInput }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        const newResponse = {
          id: Date.now(),
          input: currentInput,
          response: data.helix_response,
          timestamp: new Date().toISOString(),
        };
        
        setResponses(prev => [newResponse, ...prev]);
        
        // Update system status after processing
        checkHelixStatus();
      } else {
        throw new Error(data.error || 'Processing failed');
      }
    } catch (error) {
      console.error('Helix processing error:', error);
      const errorResponse = {
        id: Date.now(),
        input: currentInput,
        error: error.message,
        timestamp: new Date().toISOString(),
      };
      setResponses(prev => [errorResponse, ...prev]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      processInput();
    }
  };

  const formatEmotionalState = (state) => {
    const emotionColors = {
      neutral: '#6b7280',
      curious: '#3b82f6',
      focused: '#059669',
      reflective: '#7c3aed',
      transcendent: '#dc2626',
      regretful: '#d97706',
      euphoric: '#ec4899',
      contemplative: '#0891b2'
    };
    
    return (
      <span 
        className="emotional-state"
        style={{ color: emotionColors[state] || '#6b7280' }}
      >
        {state}
      </span>
    );
  };

  const renderResponse = (item) => {
    if (item.error) {
      return (
        <div key={item.id} className="response-item error">
          <div className="input-text">🧠 {item.input}</div>
          <div className="error-text">❌ Error: {item.error}</div>
          <div className="timestamp">{new Date(item.timestamp).toLocaleTimeString()}</div>
        </div>
      );
    }

    const { response } = item;
    const echo = response.echo;
    const decision = response.decision;
    const currentState = response.current_state;
    const feedback = response.transcendental_feedback;

    return (
      <div key={item.id} className="response-item">
        <div className="input-text">🧠 {item.input}</div>
        
        <div className="helix-response">
          <div className="response-section">
            <h4>🎭 Cognitive State</h4>
            <div className="state-grid">
              <div>Emotional State: {formatEmotionalState(currentState.emotional_state)}</div>
              <div>Action: <span className="action">{decision.action}</span></div>
              <div>Confidence: <span className="metric">{(decision.confidence * 100).toFixed(1)}%</span></div>
              <div>Reflection Depth: <span className="metric">{echo.reflection_depth}</span></div>
            </div>
          </div>

          <div className="response-section">
            <h4>✨ Transcendence Metrics</h4>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">Transcendence Score:</span>
                <div className="metric-bar">
                  <div 
                    className="metric-fill transcendence"
                    style={{ width: `${echo.transcendence_score * 100}%` }}
                  ></div>
                  <span className="metric-value">{(echo.transcendence_score * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="metric-item">
                <span className="metric-label">Resonance Level:</span>
                <div className="metric-bar">
                  <div 
                    className="metric-fill resonance"
                    style={{ width: `${echo.resonance_level * 100}%` }}
                  ></div>
                  <span className="metric-value">{(echo.resonance_level * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="metric-item">
                <span className="metric-label">Regret Factor:</span>
                <div className="metric-bar">
                  <div 
                    className="metric-fill regret"
                    style={{ width: `${echo.regret_factor * 100}%` }}
                  ></div>
                  <span className="metric-value">{(echo.regret_factor * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {feedback.transcendence_opportunities.length > 0 && (
            <div className="response-section">
              <h4>🚀 Transcendence Opportunities</h4>
              <ul className="opportunity-list">
                {feedback.transcendence_opportunities.map((opp, idx) => (
                  <li key={idx} className="opportunity">{opp}</li>
                ))}
              </ul>
            </div>
          )}

          {feedback.regret_warnings.length > 0 && (
            <div className="response-section">
              <h4>⚠️ Regret Warnings</h4>
              <ul className="warning-list">
                {feedback.regret_warnings.map((warning, idx) => (
                  <li key={idx} className="warning">{warning}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="response-section">
            <h4>📚 Codex Activity</h4>
            <div className="codex-info">
              <div>Relevant Patterns: {response.relevant_patterns.length}</div>
              <div>Processing Time: {(response.processing_time * 1000).toFixed(2)}ms</div>
              {response.resonance_pulse.transcendence_events > 0 && (
                <div className="transcendence-event">
                  🌟 Transcendence Events: {response.resonance_pulse.transcendence_events}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="timestamp">{new Date(item.timestamp).toLocaleTimeString()}</div>
      </div>
    );
  };

  return (
    <div className="helix-console">
      <div className="console-header">
        <h2>🔥 HelixEchoCore Console</h2>
        <div className="status-indicators">
          <div className={`connection-status ${connectionStatus}`}>
            {connectionStatus === 'connected' && '🟢 Connected'}
            {connectionStatus === 'unavailable' && '🔴 Unavailable'}
            {connectionStatus === 'error' && '⚠️ Error'}
            {connectionStatus === 'disconnected' && '⚫ Disconnected'}
          </div>
        </div>
      </div>

      {systemStatus && systemStatus.available && (
        <div className="system-status">
          <h3>🧠 System Status</h3>
          <div className="status-grid">
            <div>Session: {systemStatus.status.session_id.slice(0, 8)}</div>
            <div>Echo Memories: {systemStatus.status.helix_core.echo_memories_count}</div>
            <div>Codex Entries: {systemStatus.status.prometheus_codex.total_entries}</div>
            <div>Transcendence Level: {(systemStatus.status.helix_core.transcendence_level * 100).toFixed(1)}%</div>
            <div>Current Emotion: {formatEmotionalState(systemStatus.status.helix_core.emotional_state)}</div>
            <div>Avg Resonance: {(systemStatus.status.prometheus_codex.avg_resonance * 100).toFixed(1)}%</div>
          </div>
        </div>
      )}

      <div className="input-section">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter your thoughts for HelixEcho to process... (Press Enter to submit, Shift+Enter for new line)"
          disabled={isProcessing || connectionStatus !== 'connected'}
          rows={3}
        />
        <button 
          onClick={processInput}
          disabled={!input.trim() || isProcessing || connectionStatus !== 'connected'}
          className="process-button"
        >
          {isProcessing ? '🧠 Processing...' : '🔮 Process Thought'}
        </button>
      </div>

      <div className="responses-container">
        {responses.map(renderResponse)}
        {responses.length === 0 && (
          <div className="empty-state">
            <p>Welcome to the HelixEchoCore consciousness interface.</p>
            <p>Enter a thought, question, or reflection to begin your journey into cognitive transcendence.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HelixConsole;
