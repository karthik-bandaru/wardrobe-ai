import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav>
      <div>
        <Link to="/">👕 Wardrobe AI</Link>
      </div>

      <div>
        <Link to="/">Home</Link>
        <Link to="/wardrobe">My Wardrobe</Link>
        <Link to="/recommendations">Recommendations</Link>
        <Link to="/chatbot">AI Chat</Link>
      </div>
    </nav>
  );
}

export default Navbar;