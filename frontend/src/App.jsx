import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import Wardrobe from "./pages/Wardrobe";
import Recommendations from "./pages/Recommendations";
import Chatbot from "./pages/Chatbot";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <div className="text-center mt-10">
        <h1 className="text-4xl font-bold">
          Wardrobe AI
        </h1>

        <p className="text-gray-600 mt-3">
          AI Dress Colour Matching Assistant
        </p>
      </div>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/wardrobe" element={<Wardrobe />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;