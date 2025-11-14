import React from 'react';
import logo from './logo.svg';
import PeopleHelped from "./Components/PeopleHelped";
import PeopleHelpedOverall from "./Components/PeopleOverall";
import Dashboard from "./Components/Dashboard";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./Pages/Home"
import IT from "./Pages/IT"
import LoginPage from "./Pages/LoginPage";
import './App.css';

function App() {
  return (
      <Router>
          <Routes>
              <Route path="/acasa" element={<Home />} />
              <Route path="/dev" element={<IT/>}/>
              <Route path="/" element={<LoginPage/>}/>
          </Routes>
      </Router>
  );
}

export default App;
