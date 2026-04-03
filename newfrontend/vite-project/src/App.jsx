
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home .jsx";
import Assessment from "./pages/questionnarie.jsx";
import Result from "./pages/result.jsx";
import Privacy from "./pages/privacy.jsx";

function App() {
  return (
    <BrowserRouter>


      <Routes>

        <Route path="/" element={<Home />} />

        <Route path="/questions" element={<Assessment />} />

        <Route path="/result" element={<Result />} />

        <Route path="/privacy" element={<Privacy />} />

      </Routes>

    </BrowserRouter>
  );
}

export default App;
