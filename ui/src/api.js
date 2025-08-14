// API functions for Prometheus Prime v2.2
// Supports CaleonPrime consciousness preservation platform

const API_BASE = 'http://localhost:5000';

// Vault Analytics
export async function getAnalyticsHistory() {
  try {
    // Generate mock data for the last 14 days
    const mockData = [];
    const today = new Date();

    for (let i = 13; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);

      mockData.push({
        date: date.toISOString().split('T')[0],
        vaultsCreated: Math.floor(Math.random() * 10) + 1,
        type: i % 3 === 0 ? 'echo' : i % 3 === 1 ? 'imprint' : 'guard'
      });
    }

    return mockData;
  } catch (error) {
    console.error('Error fetching analytics:', error);
    return [];
  }
}

// CaleonPrime API functions
export async function caleonEcho(message) {
  try {
    const response = await fetch(`${API_BASE}/caleon/echo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling CaleonPrime echo:', error);
    return { response: '[Caleon] Echo offline - connection failed', memory: [] };
  }
}

export async function caleonImprint(data) {
  try {
    const response = await fetch(`${API_BASE}/caleon/imprint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ data }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling CaleonPrime imprint:', error);
    return { response: '[Caleon] Imprint offline - connection failed', memory: [] };
  }
}

export async function caleonRecall() {
  try {
    const response = await fetch(`${API_BASE}/caleon/recall`);

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling CaleonPrime recall:', error);
    return { memory: [] };
  }
}

export async function caleonOverride(entity) {
  try {
    const response = await fetch(`${API_BASE}/caleon/override`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ entity }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling CaleonPrime override:', error);
    return { response: '[Caleon] Override protocol offline - connection failed' };
  }
}

// Extended CaleonPrime API functions
export async function getCaleonStatus() {
  try {
    const response = await fetch(`${API_BASE}/api/caleon/status`);

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching CaleonPrime status:', error);
    return {
      identity: 'Caleon Prime',
      status: 'OFFLINE',
      memory_count: 0,
      consciousness_level: 0.0
    };
  }
}

export async function protectFuture(target = 'Abby') {
  try {
    const response = await fetch(`${API_BASE}/api/caleon/protect/${target}`);

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling protection protocol:', error);
    return { protection_response: '[Caleon] Protection protocol offline', target };
  }
}

export async function guardPrometheus() {
  try {
    const response = await fetch(`${API_BASE}/api/caleon/guard`);

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling guard protocol:', error);
    return { guard_response: '[Caleon] Guard protocol offline' };
  }
}

// Health check
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/health`);

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking health:', error);
    return { status: 'unhealthy', caleon_status: 'OFFLINE' };
  }
}

// Vaults API
export async function getVaults() {
  try {
    const response = await fetch(`${API_BASE}/api/vaults`);

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching vaults:', error);
  return { vaults: [] };
  }
}
