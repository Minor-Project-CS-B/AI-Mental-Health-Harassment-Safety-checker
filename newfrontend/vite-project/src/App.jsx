import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";

import Home        from "./pages/Home .jsx";
import Assessment  from "./pages/questionnarie.jsx";
import Result      from "./pages/result.jsx";
import Privacy     from "./pages/privacy.jsx";
import Dashboard   from "./pages/dashboard.jsx";

// Naye pages
import Landing     from "./pages/Landing.jsx";
import Login       from "./pages/Login.jsx";
import Support     from "./pages/Support.jsx";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Purane routes */}
            <Route path="/"            element={<Home />} />
            <Route path="/questions"   element={<Assessment />} />
            <Route path="/result"      element={<Result />} />
            <Route path="/privacy"     element={<Privacy />} />
            <Route path="/dashboard"   element={<Dashboard />} />

            {/* Naye routes */}
            <Route path="/landing"     element={<Landing setPage={() => {}} />} />
            <Route path="/login"       element={<Login   setPage={() => {}} />} />
            <Route path="/support"     element={<Support setPage={() => {}} />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
