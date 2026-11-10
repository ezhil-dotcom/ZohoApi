import { useEffect, useState } from "react";

const API_BASE = "http://localhost:5022";

async function call(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || result.title);
  return result;
}

function App() {
  const [orgs, setOrgs] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWs, setSelectedWs] = useState(null);
  const [views, setViews] = useState([]);
  const [selectedView, setSelectedView] = useState(null);
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [tableName, setTableName] = useState("Bently_VJ");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pushing, setPushing] = useState(false);

  const run = async (fn) => {
    setLoading(true);
    setMessage("");
    try {
      await fn();
    } catch (e) {
      setIsError(true);
      setMessage("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const getOrgs = () =>
    run(async () => {
      const r = await call("/api/zoho/orgs");
      setOrgs(r.data?.orgs ?? []);
    });

  const getWorkspaces = (org) =>
    run(async () => {
      setSelectedOrg(org);
      setSelectedWs(null);
      setSelectedView(null);
      setWorkspaces([]);
      setViews([]);
      setRows([]);
      const r = await call(`/api/zoho/orgs/${org.orgId}/workspaces`);
      const d = r.data ?? {};
      setWorkspaces([...(d.ownedWorkspaces ?? []), ...(d.sharedWorkspaces ?? [])]);
    });

  const getViews = (ws) =>
    run(async () => {
      setSelectedWs(ws);
      setSelectedView(null);
      setViews([]);
      setRows([]);
      const r = await call(
        `/api/zoho/orgs/${selectedOrg.orgId}/workspaces/${ws.workspaceId}/views`
      );
      setViews(r.data?.views ?? []);
    });

  const getData = (view) =>
    run(async () => {
      setSelectedView(view);
      setRows([]);
      const r = await call(
        `/api/zoho/orgs/${selectedOrg.orgId}/workspaces/${selectedWs.workspaceId}/views/${view.viewId}/data`
      );
      setRows(r.data?.rows ?? []);
      setTotal(r.data?.total ?? 0);
    });

  // Push the selected view's data into SQL Server
  const pushToSql = async (view) => {
    
    const safeName = tableName.trim().replace(/[^A-Za-z0-9_]/g, "_");
    if (!safeName) {
      setIsError(true);
      setMessage("Error: enter a SQL table name first.");
      return;
    }

    setPushing(true);
    setIsError(false);
    setMessage(`Pushing "${view.viewName}" to SQL table ${safeName}... this can take a few seconds.`);
    try {
      const r = await call(
        `/api/zoho/orgs/${selectedOrg.orgId}/workspaces/${selectedWs.workspaceId}/views/${view.viewId}/push-to-sql?table_name=${encodeURIComponent(safeName)}`,
        { method: "POST" }
      );
      setIsError(false);
      setMessage("✔ " + r.message);
      alert("push data " + r.message)
    } catch (e) {
      setIsError(true);
       alert("push data error" + e.message)
      setMessage("Error: " + e.message);
    } finally {
      setPushing(false);
    }
  };

  useEffect(() => {
    getOrgs();
  }, []);

  const busy = loading || pushing;
  const columns = rows.length ? Object.keys(rows[0]) : [];
  const tableStyle = { borderCollapse: "collapse", marginTop: "10px" };
  const highlight = (on) => ({
    background: on ? "#e6f0ff" : "transparent",
    color: on ? "#000" : "inherit",
  });

  return (
    <div style={{ padding: "30px" }}>
      <h1>Zoho Analytics Integration</h1>

      <h2>Organizations</h2>
      <table border="1" cellPadding="8" style={tableStyle}>
        <thead>
          <tr><th>Organization ID</th><th>Name</th><th>Plan</th><th>Workspaces</th><th></th></tr>
        </thead>
        <tbody>
          {orgs.map((o) => (
            <tr key={o.orgId} style={highlight(selectedOrg?.orgId === o.orgId)}>
              <td>{o.orgId}</td><td>{o.orgName}</td><td>{o.planName}</td><td>{o.numberOfWorkspaces}</td>
              <td><button onClick={() => getWorkspaces(o)} disabled={busy}>View Workspaces</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedOrg && workspaces.length > 0 && (
        <>
          <h2>Workspaces in {selectedOrg.orgName}</h2>
          <table border="1" cellPadding="8" style={tableStyle}>
            <thead><tr><th>Workspace ID</th><th>Name</th><th></th></tr></thead>
            <tbody>
              {workspaces.map((w) => (
                <tr key={w.workspaceId} style={highlight(selectedWs?.workspaceId === w.workspaceId)}>
                  <td>{w.workspaceId}</td><td>{w.workspaceName}</td>
                  <td><button onClick={() => getViews(w)} disabled={busy}>View Tables</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {selectedWs && views.length > 0 && (
        <>
          <h2>Tables in {selectedWs.workspaceName}</h2>

          <label>
            SQL table name:{" "}
            <input
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              placeholder="Bently_VJ"
              disabled={busy}
            />
          </label>

          <table border="1" cellPadding="8" style={tableStyle}>
            <thead><tr><th>View ID</th><th>Name</th><th>Type</th><th></th><th></th></tr></thead>
            <tbody>
              {views.map((v) => (
                <tr key={v.viewId} style={highlight(selectedView?.viewId === v.viewId)}>
                  <td>{v.viewId}</td><td>{v.viewName}</td><td>{v.viewType}</td>
                  <td><button onClick={() => getData(v)} disabled={busy}>View Data</button></td>
                  <td><button onClick={() => pushToSql(v)} disabled={busy}>Push to SQL</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {loading && <p>Loading... (table exports can take a few seconds)</p>}
      {message && (
        <p style={{ color: isError ? "red" : "limegreen", fontWeight: "bold" }}>{message}</p>
      )}

      {rows.length > 0 && (
        <>
          <h2>{selectedView?.viewName}</h2>
          <p>Showing {rows.length} of {total} rows</p>
          <div style={{ overflowX: "auto" }}>
            <table border="1" cellPadding="6" style={tableStyle}>
              <thead><tr>{columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={i}>{columns.map((c) => <td key={c}>{String(row[c] ?? "")}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default App;