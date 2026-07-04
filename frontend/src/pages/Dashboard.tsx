import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/client';

interface ResourceCounts {
  tasks: number;
}

const Dashboard: React.FC = () => {
  const [counts, setCounts] = useState<ResourceCounts | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCounts = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get('/api/health');
        setCounts({ tasks: response.data.tasks_count });
      } catch (err) {
        setError('Failed to fetch resource counts.');
      } finally {
        setLoading(false);
      }
    };

    fetchCounts();
  }, []);

  const handleQuickAction = (action: string) => {
    if (action === 'addTask') {
      navigate('/tasks/new');
    } else if (action === 'viewTasks') {
      navigate('/tasks');
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>
      {loading && <p className="text-gray-600">Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && counts && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            <div className="bg-white shadow rounded-lg p-4">
              <h2 className="text-lg font-semibold text-gray-700">Tasks</h2>
              <p className="text-2xl font-bold text-gray-900">{counts.tasks}</p>
            </div>
          </div>
          <div className="bg-white shadow rounded-lg p-4 mb-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Quick Actions</h2>
            <div className="flex space-x-4">
              <button
                onClick={() => handleQuickAction('addTask')}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Add Task
              </button>
              <button
                onClick={() => handleQuickAction('viewTasks')}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              >
                View Tasks
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;