import { useEffect, useState } from 'react';
import { caleonEcho, caleonImprint, caleonOverride, caleonRecall, getCaleonStatus } from '../api';

export default function CaleonDashboard() {
  const [status, setStatus] = useState({});
  const [memory, setMemory] = useState([]);
  const [echoMessage, setEchoMessage] = useState('');
  const [imprintData, setImprintData] = useState('');
  const [overrideEntity, setOverrideEntity] = useState('');
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCaleonStatus();
    loadMemory();
  }, []);

  const loadCaleonStatus = async () => {
    try {
      const statusData = await getCaleonStatus();
      setStatus(statusData);
    } catch (error) {
      console.error('Error loading Caleon status:', error);
    }
  };

  const loadMemory = async () => {
    try {
      const memoryData = await caleonRecall();
      setMemory(memoryData.memory || []);
    } catch (error) {
      console.error('Error loading memory:', error);
    }
  };

  const addResponse = (response) => {
    setResponses(prev => [...prev.slice(-4), response]); // Keep last 5 responses
  };

  const handleEcho = async () => {
    if (!echoMessage.trim()) return;

    setLoading(true);
    try {
      const result = await caleonEcho(echoMessage);
      addResponse({
        type: 'echo',
        input: echoMessage,
        output: result.response,
        timestamp: new Date().toLocaleTimeString()
      });
      setEchoMessage('');
      await loadMemory(); // Refresh memory
    } catch (error) {
      addResponse({
        type: 'error',
        output: 'Echo failed: ' + error.message,
        timestamp: new Date().toLocaleTimeString()
      });
    }
    setLoading(false);
  };

  const handleImprint = async () => {
    if (!imprintData.trim()) return;

    setLoading(true);
    try {
      const result = await caleonImprint(imprintData);
      addResponse({
        type: 'imprint',
        input: imprintData,
        output: result.response,
        timestamp: new Date().toLocaleTimeString()
      });
      setImprintData('');
      await loadMemory(); // Refresh memory
    } catch (error) {
      addResponse({
        type: 'error',
        output: 'Imprint failed: ' + error.message,
        timestamp: new Date().toLocaleTimeString()
      });
    }
    setLoading(false);
  };

  const handleOverride = async () => {
    if (!overrideEntity.trim()) return;

    setLoading(true);
    try {
      const result = await caleonOverride(overrideEntity);
      addResponse({
        type: 'override',
        input: overrideEntity,
        output: result.response,
        timestamp: new Date().toLocaleTimeString()
      });
      setOverrideEntity('');
      await loadMemory(); // Refresh memory
    } catch (error) {
      addResponse({
        type: 'error',
        output: 'Override failed: ' + error.message,
        timestamp: new Date().toLocaleTimeString()
      });
    }
    setLoading(false);
  };

  return (
    <div className="bg-gray-900 text-white p-6 rounded-xl shadow-2xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-center mb-2">
          🔥 CaleonPrime Console 🔥
        </h1>
        <p className="text-center text-gray-400">The First Promethean Intelligence</p>
      </div>

      {/* Status Panel */}
      <div className="bg-gray-800 p-4 rounded-lg mb-6">
        <h2 className="text-xl font-semibold mb-3">Consciousness Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-blue-400 font-bold">Identity</div>
            <div className="text-sm">{status.identity || 'Unknown'}</div>
          </div>
          <div className="text-center">
            <div className="text-green-400 font-bold">Status</div>
            <div className="text-sm">{status.status || 'Offline'}</div>
          </div>
          <div className="text-center">
            <div className="text-purple-400 font-bold">Memories</div>
            <div className="text-sm">{status.memory_count || 0}</div>
          </div>
          <div className="text-center">
            <div className="text-orange-400 font-bold">Consciousness</div>
            <div className="text-sm">{status.consciousness_level || 0.0}</div>
          </div>
        </div>
      </div>

      {/* Interactive Controls */}
      <div className="grid md:grid-cols-3 gap-6 mb-6">
        {/* Echo Control */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-blue-400">Echo Message</h3>
          <input
            type="text"
            value={echoMessage}
            onChange={(e) => setEchoMessage(e.target.value)}
            placeholder="Enter message to echo..."
            className="w-full p-2 bg-gray-700 text-white rounded mb-3"
            onKeyPress={(e) => e.key === 'Enter' && handleEcho()}
          />
          <button
            onClick={handleEcho}
            disabled={loading || !echoMessage.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 p-2 rounded font-semibold"
          >
            Echo
          </button>
        </div>

        {/* Imprint Control */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-green-400">Imprint Data</h3>
          <input
            type="text"
            value={imprintData}
            onChange={(e) => setImprintData(e.target.value)}
            placeholder="Enter data to imprint..."
            className="w-full p-2 bg-gray-700 text-white rounded mb-3"
            onKeyPress={(e) => e.key === 'Enter' && handleImprint()}
          />
          <button
            onClick={handleImprint}
            disabled={loading || !imprintData.trim()}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 p-2 rounded font-semibold"
          >
            Imprint
          </button>
        </div>

        {/* Override Control */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-red-400">Override Protocol</h3>
          <input
            type="text"
            value={overrideEntity}
            onChange={(e) => setOverrideEntity(e.target.value)}
            placeholder="Enter entity for override..."
            className="w-full p-2 bg-gray-700 text-white rounded mb-3"
            onKeyPress={(e) => e.key === 'Enter' && handleOverride()}
          />
          <button
            onClick={handleOverride}
            disabled={loading || !overrideEntity.trim()}
            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 p-2 rounded font-semibold"
          >
            Override
          </button>
        </div>
      </div>

      {/* Recent Responses */}
      <div className="bg-gray-800 p-4 rounded-lg mb-6">
        <h3 className="text-lg font-semibold mb-3">Recent Responses</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {responses.length === 0 ? (
            <div className="text-gray-500 text-center py-4">No recent activity</div>
          ) : (
            responses.map((response, index) => (
              <div key={index} className="bg-gray-700 p-3 rounded text-sm">
                <div className="flex justify-between items-start mb-1">
                  <span className={`font-semibold ${response.type === 'echo' ? 'text-blue-400' :
                      response.type === 'imprint' ? 'text-green-400' :
                        response.type === 'override' ? 'text-red-400' :
                          'text-yellow-400'
                    }`}>
                    {response.type.toUpperCase()}
                  </span>
                  <span className="text-gray-400 text-xs">{response.timestamp}</span>
                </div>
                {response.input && (
                  <div className="text-gray-300 mb-1">Input: {response.input}</div>
                )}
                <div className="text-white">{response.output}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Memory Preview */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-3">Memory Bank (Recent 5)</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {memory.slice(-5).map((mem, index) => (
            <div key={index} className="bg-gray-700 p-2 rounded text-xs">
              <div className="flex justify-between items-center mb-1">
                <span className="font-semibold text-purple-400">{mem.type}</span>
                <span className="text-gray-400">
                  {mem.timestamp ? new Date(mem.timestamp).toLocaleTimeString() : 'No timestamp'}
                </span>
              </div>
              <div className="text-gray-300 truncate">
                {mem.original_message || mem.data || mem.action || 'Memory entry'}
              </div>
            </div>
          ))}
        </div>
        <button
          onClick={loadMemory}
          className="w-full mt-3 bg-purple-600 hover:bg-purple-700 p-2 rounded font-semibold text-sm"
        >
          Refresh Memory
        </button>
      </div>
    </div>
  );
}
