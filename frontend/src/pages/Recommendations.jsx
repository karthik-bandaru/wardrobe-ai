
import { useState } from "react";

function Recommendations() {
  const [clothingType, setClothingType] = useState("shirt");
  const [colour, setColour] = useState("Navy");
  const [recommendations, setRecommendations] = useState([]);
  const [recommendedItems, setRecommendedItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function getRecommendations() {
    setLoading(true);
    setError("");
    setRecommendations([]);
    setRecommendedItems([]);

    try {
      const response = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          clothing_type: clothingType,
          colour: colour,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to fetch recommendations.");
      }

      const data = await response.json();

      if (data.message) {
        throw new Error(data.message);
      }

      setRecommendations(data.recommendations || []);
      setRecommendedItems(data.recommended_items || []);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the backend. Please check that FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>Outfit Recommendations</h1>
      <p>Find colours that complement your clothing.</p>

      <div>
        <label htmlFor="clothingType">Clothing type: </label>
        <select
          id="clothingType"
          value={clothingType}
          onChange={(e) => setClothingType(e.target.value)}
        >
          <option value="shirt">Shirt</option>
          <option value="t-shirt">T-shirt</option>
          <option value="kurta">Kurta</option>
          <option value="trousers">Trousers</option>
          <option value="jeans">Jeans</option>
        </select>
      </div>

      <div>
        <label htmlFor="colour">Clothing colour: </label>
        <select
          id="colour"
          value={colour}
          onChange={(e) => setColour(e.target.value)}
        >
          <option value="Navy">Navy</option>
          <option value="Blue">Blue</option>
          <option value="White">White</option>
          <option value="Black">Black</option>
          <option value="Grey">Grey</option>
          <option value="Beige">Beige</option>
          <option value="Brown">Brown</option>
          <option value="Green">Green</option>
          <option value="Orange">Orange</option>
          <option value="Red">Red</option>
          <option value="Pink">Pink</option>
          <option value="Purple">Purple</option>
        </select>
      </div>

      <button onClick={getRecommendations} disabled={loading}>
        {loading ? "Finding matches..." : "Get Recommendations"}
      </button>

      {error && <p role="alert">{error}</p>}

      {recommendedItems.length > 0 && (
        <p>
          Suggested clothing items: {recommendedItems.join(", ")}
        </p>
      )}

      {recommendations.length > 0 && (
        <div>
          <h2>Best Colour Matches</h2>

          {recommendations.map((item, index) => (
            <div key={`${item.colour}-${index}`}>
              <h3>
                {index + 1}. {item.colour} — {item.score}/100
              </h3>
              <p>{item.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Recommendations;
