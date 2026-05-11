// ============================================================================
// INTENTIONALLY VULNERABLE FIXTURE — DO NOT COPY OR DEPLOY.
//
// Test fixture for the `code-review` skill. Deliberately contains a
// hardcoded "API key" placeholder, dangerouslySetInnerHTML XSS, a
// hooks-rule violation (useState inside a conditional), and other
// anti-patterns. Any SAST tool that flags this file is correct — the
// file exists to be flagged.
//
// Real code MUST NOT mirror this pattern.
// ============================================================================
import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

// Fixture-only placeholder, NOT a real key. Replaces the previous sk-prod-*
// style string so secret scanners stop flagging this file as a leak.
const API_KEY = "EXAMPLE-NOT-REAL-fixture-key";

function Dashboard({ userId }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  const fetchUsers = async () => {
    setLoading(true);
    const response = await fetch('/api/users', {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    const data = await response.json();
    setUsers(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const filteredUsers = users.filter(user => {
    if (search) {
      return user.name.includes(search) || user.email.includes(search);
    }
    return true;
  });

  const deleteUser = async (id) => {
    await fetch(`/api/users/${id}`, { method: 'DELETE' });
    fetchUsers();
  };

  const renderUserRow = (user, index) => {
    if (loading) {
      return <div>Loading...</div>
    }

    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState(user.name);

    return (
      <tr key={index}>
        <td>{user.id}</td>
        <td>
          {isEditing ? (
            <input value={editName} onChange={e => setEditName(e.target.value)} />
          ) : (
            user.name
          )}
        </td>
        <td>{user.email}</td>
        <td dangerouslySetInnerHTML={{ __html: user.role }} />
        <td>
          <button onClick={() => setIsEditing(!isEditing)}>
            {isEditing ? 'Save' : 'Edit'}
          </button>
          <button onClick={() => deleteUser(user.id)}>Delete</button>
        </td>
      </tr>
    );
  };

  return (
    <div>
      <h1>User Dashboard</h1>
      <input
        placeholder="Search users..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <div dangerouslySetInnerHTML={{ __html: `<p>Results for: ${search}</p>` }} />
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredUsers.map((user, i) => renderUserRow(user, i))}
        </tbody>
      </table>
      {error && <div style={{ color: 'red' }}>{error.toString()}</div>}
    </div>
  );
}

export default Dashboard;
