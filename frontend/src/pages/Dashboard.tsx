type DashboardProps = {
  onLogout: () => void;
};

function Dashboard({ onLogout }: DashboardProps) {
  return (
    <main style={{ padding: "32px", fontFamily: "system-ui" }}>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>AI Documentation Chat</h1>
        <button type="button" onClick={onLogout}>
          Sign out
        </button>
      </header>

      <p>You're signed in. Your document chat dashboard will go here.</p>
    </main>
  );
}

export default Dashboard;
