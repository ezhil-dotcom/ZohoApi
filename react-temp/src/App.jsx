import { useEffect, useState } from "react";

const API_BASE = "http://localhost:5022";

async function call(path) {
  const response = await fetch(`${API_BASE}${path}`);
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || result.title);
  return result;
}

function App() {
  const [orgs, setOrgs] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [workspaces, setWorkspaces] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const getOrgs = async () => {
    setLoading(true);
    setMessage("");
    try {
      const r = await call("/api/zoho/orgs");
      setOrgs(r.data?.orgs ?? []);
    } catch (e) {
      setMessage("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const getWorkspaces = async (org) => {
    setSelectedOrg(org);
    setWorkspaces([]);
    setLoading(true);
    setMessage("");
    try {
      const r = await call(`/api/zoho/orgs/${org.orgId}/workspaces/1744699000000069001/views/1744699000117545002/data`);
      setWorkspaces(r.data.workspaces);
      if (r.data.workspaces.length === 0) setMessage("No workspaces found for this organization.");
    } catch (e) {
      setMessage("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getOrgs();
  }, []);

  return (
    <div style={{ padding: "30px" }}>
      <h1>Zoho Analytics Integration</h1>

      <h2>Organizations</h2>
      <button onClick={getOrgs} disabled={loading}>Refresh Organizations</button>

      {orgs.length > 0 && (
        <table border="1" cellPadding="8" style={{ marginTop: "15px", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Organization ID</th>
              <th>Name</th>
              <th>Plan</th>
              <th>Workspaces</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {orgs.map((org) => (
              <tr
                key={org.orgId}
                style={{ background: selectedOrg?.orgId === org.orgId ? "#e6f0ff" : "transparent" }}
              >
                <td>{org.orgId}</td>
                <td>{org.orgName}</td>
                <td>{org.planName}</td>
                <td>{org.numberOfWorkspaces}</td>
                <td>
                  <button onClick={() => getWorkspaces(org)} disabled={loading}>
                    View Workspaces
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedOrg && (
        <>
          <h2 style={{ marginTop: "30px" }}>Workspaces in {selectedOrg.orgName}</h2>
          {workspaces.length > 0 && (
            <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th>Workspace ID</th>
                  <th>Workspace Name</th>
                  <th>Access</th>
                </tr>
              </thead>
              <tbody>
                {workspaces.map((w) => (
                  <tr key={w.workspaceId}>
                    <td>{w.workspaceId}</td>
                    <td>{w.workspaceName}</td>
                    <td>{w.access}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}

      {loading && <p>Loading...</p>}
      {message && <p style={{ color: message.startsWith("Error") ? "red" : "inherit" }}>{message}</p>}
    </div>
  );
}

export default App;