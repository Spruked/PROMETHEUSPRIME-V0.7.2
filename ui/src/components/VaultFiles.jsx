import React, { useState, useEffect } from 'react';
import './VaultFiles.css';

const VaultFiles = () => {
  const [vaultFiles, setVaultFiles] = useState([]);
  const [selectedVault, setSelectedVault] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch list of vault files
  const fetchVaultFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/vault-files');
      const data = await response.json();
      setVaultFiles(data.vault_files || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch vault files');
      console.error('Error fetching vault files:', err);
    }
    setLoading(false);
  };

  // Fetch specific vault content
  const fetchVaultContent = async (vaultId) => {
    try {
      const response = await fetch(`http://localhost:5000/vault-files/${vaultId}`);
      const data = await response.json();
      setSelectedVault(data);
    } catch (err) {
      setError('Failed to fetch vault content');
      console.error('Error fetching vault content:', err);
    }
  };

  // Download vault file
  const downloadVault = (vaultId) => {
    const link = document.createElement('a');
    link.href = `http://localhost:5000/vault-files/${vaultId}/download`;
    link.download = `${vaultId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  useEffect(() => {
    fetchVaultFiles();
  }, []);

  return (
    <div className="vault-files-container">
      <div className="vault-files-header">
        <h3>🗂️ Vault Files</h3>
        <button onClick={fetchVaultFiles} disabled={loading}>
          {loading ? '🔄 Loading...' : '🔄 Refresh'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      <div className="vault-files-grid">
        <div className="vault-files-list">
          <h4>📁 Available Vaults ({vaultFiles.length})</h4>
          {vaultFiles.length === 0 ? (
            <div className="no-vaults">No vault files found</div>
          ) : (
            <ul className="vault-list">
              {vaultFiles.map((vaultId) => (
                <li key={vaultId} className="vault-item">
                  <span className="vault-id">{vaultId}</span>
                  <div className="vault-actions">
                    <button 
                      onClick={() => fetchVaultContent(vaultId)}
                      className="view-btn"
                    >
                      👁️ View
                    </button>
                    <button 
                      onClick={() => downloadVault(vaultId)}
                      className="download-btn"
                    >
                      ⬇️ Download
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="vault-content">
          <h4>📄 Vault Content</h4>
          {selectedVault ? (
            <div className="vault-details">
              <pre className="vault-json">
                {JSON.stringify(selectedVault, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="no-selection">
              Select a vault to view its content
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VaultFiles;
