// App.js

import React, { useState } from 'react';
import Generator from './components/Generator';
import SignIn from './components/SignIn';
import { AuthContext } from './components/AuthContext';
import api from './api';
import CircularProgress from '@mui/material/CircularProgress';


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [loading, setLoading] = useState(true);

  const signIn = async (username, password) => {
    try {
      const response = await api.post('/api/auth', {
        username,
        password,
      });

      if (response.status === 200) {
        setIsAuthenticated(true);
        setErrorMessage(null); // Clear any previous error messages
      } else {
        setErrorMessage("Incorrect username or password"); // Set error message
      }
    } catch (error) {
      setErrorMessage("Incorrect username or password"); // Set error message
    }
  };

  React.useEffect(() => {
    const checkAuthenticationStatus = async () => {
      try {
        const response = await api.get('/api/is_authenticated');
        if (response.status === 200) {
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        setIsAuthenticated(false);
      }
      setLoading(false);  // Set loading to false after completing the request
    };
    checkAuthenticationStatus();
  }, []);  // Empty dependency array means this effect runs once on component mount

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'  // Full viewport height
      }}>
        <CircularProgress />
      </div>
    );
  } else {
    return (
      <div className="App">
        <AuthContext.Provider value={{ signIn, errorMessage }}> {/* Pass errorMessage to context */}
          {isAuthenticated ? <Generator /> : <SignIn />}
        </AuthContext.Provider>
      </div>
    );
  }
}

export default App;
