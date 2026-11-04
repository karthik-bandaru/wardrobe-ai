
import { useState } from "react";

function Wardrobe() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [recommendedItems, setRecommendedItems] = useState([]);
  const [error, setError] = useState("");
  const [recommendationError, setRecommendationError] = useState("");
  const [loading, setLoading] = useState(false);

  const [wardrobeItems, setWardrobeItems] = useState([]);
  const [saveMessage, setSaveMessage] = useState("");

  function handleFileChange(event) {
    setFile(event.target.files[0] || null);
    setResult(null);
    setRecommendations([]);
    setRecommendedItems([]);
    setError("");
    setRecommendationError("");
  }

  // Convert detected clothing labels into supported categories.
  function mapClothingType(type) {
    const value = (type || "")
      .toLowerCase()
      .replaceAll("_", " ")
      .trim();

    if (value.includes("dress")) return "dress";
    if (value.includes("kurta")) return "kurta";
    if (value.includes("jeans") || value.includes("denim")) {
      return "jeans";
    }
    if (
      value.includes("trouser") ||
      value.includes("pants")
    ) {
      return "trousers";
    }
    if (
      value.includes("t-shirt") ||
      value.includes("t shirt") ||
      value.includes("tshirt") ||
      value.includes("short sleeve") ||
      value.includes("sleeveless")
    ) {
      return "t-shirt";
    }
    if (
      value.includes("long sleeve outwear") ||
      value.includes("long sleeve outerwear") ||
      value.includes("shirt") ||
      value.includes("long sleeve top") ||
      value === "top"
    ) {
      return "shirt";
    }

    return null;
  }

  function handleAddToWardrobe() {
  if (!file || !result) {
    setSaveMessage("Please analyze a clothing image first.");
    return;
  }

  const reader = new FileReader();

  reader.onload = () => {
    const newItem = {
      id: crypto.randomUUID(),
      name: file.name,
      image: reader.result,
      clothingType: result.clothing_type,
      colour: result.colour,
      confidence: result.confidence,
      addedAt: new Date().toISOString(),
    };

    setWardrobeItems((previousItems) => [
      newItem,
      ...previousItems,
    ]);

    setSaveMessage("Clothing item added to your wardrobe!");
  };

  reader.onerror = () => {
    setSaveMessage("Unable to save this image. Please try again.");
  };

  reader.readAsDataURL(file);
}

  async function handleAnalyze() {
    if (!file) {
      setError("Please select a clothing image first.");
      return;
    }

    setLoading(true);
    setError("");
    setRecommendationError("");
    setResult(null);
    setRecommendations([]);
    setRecommendedItems([]);

    try {
      // 1. Analyze the uploaded image.
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:8000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to analyze this image."
        );
      }

      setResult(data);

      // 2. Automatically request recommendations.
      const clothingType = mapClothingType(data.clothing_type);

      if (!clothingType) {
        setRecommendationError(
          `Recommendations are not yet supported for "${data.clothing_type}". Your image analysis was successful.`
        );
        return;
      }

      const recommendationResponse = await fetch(
        "http://localhost:8000/recommend",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            clothing_type: clothingType,
            colour: data.colour,
          }),
        }
      );

      const recommendationData =
        await recommendationResponse.json();

      if (!recommendationResponse.ok) {
        throw new Error(
          "The recommendation service could not process your request."
        );
      }

      if (recommendationData.message) {
        setRecommendationError(recommendationData.message);
        return;
      }

      setRecommendations(
        recommendationData.recommendations || []
      );
      setRecommendedItems(
        recommendationData.recommended_items || []
      );
    } catch (err) {
      // Keep image-analysis errors separate from recommendation errors.
      if (!result) {
        setError(
          err.message || "Could not connect to the backend."
        );
      } else {
        setRecommendationError(
          err.message || "Could not generate recommendations."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="mb-2 text-3xl font-bold">
        My Wardrobe
      </h1>

      <p className="mb-6 text-gray-600">
        Upload a clothing image to identify its type and colour
        and automatically get matching outfit recommendations.
      </p>

      <div className="rounded-xl border p-6">
        <label className="mb-3 block font-medium">
          Choose a clothing image
        </label>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="mb-4 block w-full"
        />

        {file && (
          <p className="mb-4 text-sm text-gray-600">
            Selected: {file.name}
          </p>
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 text-white disabled:opacity-50"
        >
          {loading
            ? "Analyzing and finding matches..."
            : "Analyze & Get Recommendations"}
        </button>

        {error && (
          <p role="alert" className="mt-4 text-red-600">
            {error}
          </p>
        )}

        {result && (
          <div className="mt-6 rounded-lg bg-gray-100 p-4">
            <h2 className="mb-3 text-xl font-semibold">
              Analysis Results
            </h2>

            <p>
              <strong>Clothing type:</strong>{" "}
              {result.clothing_type}
            </p>

            <p>
              <strong>Confidence:</strong>{" "}
              {(result.confidence * 100).toFixed(2)}%
            </p>

            <p>
              <strong>Primary colour:</strong>{" "}
              {result.colour}
            </p>

            {result.dominant_colours?.length > 0 && (
              <div className="mt-3">
                <strong>Dominant colours:</strong>

                <div className="mt-2 flex flex-wrap gap-2">
                  {result.dominant_colours.map((colour) => (
                    <span
                      key={colour}
                      className="rounded-full border bg-white px-3 py-1 text-sm text-gray-800"
                    >
                      {colour}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {result && (
          <div className="mt-4">
            <button
              onClick={handleAddToWardrobe}
              className="rounded-lg bg-green-600 px-5 py-2 text-white hover:bg-green-700"
            >
              + Add to My Wardrobe
            </button>

            {saveMessage && (
              <p
                role="status"
                className="mt-2 text-sm text-green-700"
              >
                {saveMessage}
              </p>
            )}
          </div>
        )}
        {result && (
          <div className="mt-6">
            <h2 className="mb-3 text-xl font-semibold">
              Your Outfit Recommendations
            </h2>

            {recommendationError && (
              <p role="alert" className="text-amber-700">
                {recommendationError}
              </p>
            )}

            {recommendedItems.length > 0 && (
              <p className="mb-4 text-gray-600">
                Suggested clothing items:{" "}
                {recommendedItems.join(", ")}
              </p>
            )}

            {recommendations.length > 0 && (
              <div className="space-y-3">
                {recommendations.map((item, index) => (
                  <div
                    key={`${item.colour}-${index}`}
                    className="rounded-lg border p-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="font-semibold">
                        {index + 1}. {item.colour}
                      </h3>
                      <span className="font-medium">
                        {item.score}/100
                      </span>
                    </div>

                    <p className="mt-1 text-sm text-gray-600">
                      {item.reason}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-10 border-t pt-6">
        <h2 className="mb-4 text-2xl font-bold">
          My Clothing Collection ({wardrobeItems.length})
        </h2>

        {wardrobeItems.length === 0 ? (
          <p className="text-gray-600">
            No items added yet.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {wardrobeItems.map((item) => (
              <div
                key={item.id}
                className="rounded-xl border p-4 shadow-sm"
              >
                <img
                  src={item.image}
                  alt={item.clothingType}
                  className="h-48 w-full rounded-lg bg-gray-50 object-contain"
                />

                <h3 className="mt-3 font-semibold">
                  {item.clothingType}
                </h3>

                <p className="text-gray-600">
                  Colour: {item.colour}
                </p>

                <button
                  onClick={() => {
                    setWardrobeItems((items) =>
                      items.filter(
                        (existingItem) => existingItem.id !== item.id
                      )
                    );
                  }}
                  className="mt-3 rounded-lg border border-red-300 px-3 py-2 text-sm text-red-600"
                >
                  Remove item
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="mt-10">
        <h2 className="mb-4 text-2xl font-bold">
          My Clothing Collection ({wardrobeItems.length})
        </h2>

        {wardrobeItems.length === 0 ? (
          <p className="text-gray-600">
            No clothing items added yet. Analyze an image and
            click "Add to My Wardrobe" to get started.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {wardrobeItems.map((item) => (
              <div
                key={item.id}
                className="overflow-hidden rounded-xl border bg-white shadow-sm"
              >
                <img
                  src={item.image}
                  alt={item.clothingType}
                  className="h-52 w-full object-contain bg-gray-50"
                />

                <div className="p-4">
                  <h3 className="font-semibold">
                    {item.clothingType}
                  </h3>

                  <p className="text-gray-600">
                    Colour: {item.colour}
                  </p>

                  <p className="mt-1 truncate text-sm text-gray-500">
                    {item.name}
                  </p>

                  <button
                    onClick={() => {
                      setWardrobeItems((items) =>
                        items.filter(
                          (existingItem) =>
                            existingItem.id !== item.id
                        )
                      );
                    }}
                    className="mt-3 rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
                  >
                    Remove item
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
    
  );
  
  

}


export default Wardrobe;
