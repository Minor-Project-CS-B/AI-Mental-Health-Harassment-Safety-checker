import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Home .jsx";
import Login from "./pages/login.jsx";
import Register from "./pages/register.jsx";
import Onboarding from "./pages/onboarding.jsx";
import Dashboard from "./pages/dashboard";
import Chat from "./pages/chat";
import Assessment from "./pages/questionnarie";
import Help from "./pages/help.jsx";



function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Landing />} />

        <Route path="/register" element={<Register />} />

        <Route path="/login" element={< Login />} />

        <Route path="/onboarding" element={<  Onboarding />} />

        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/assessment" element={<Assessment />} />

        <Route path="/chat" element={<Chat />} />

        <Route path="/help" element={<Help />} />

       

      </Routes>
    </BrowserRouter>
  );
}

export default App;