
# Supported clothing colours and their common shades.
# These names will be used by the matching engine.

COLOUR_FAMILIES = {
    "Blue": [
        "Blue", "Navy", "Navy Blue", "Sky Blue",
        "Light Blue", "Royal Blue", "Teal",
        "Denim Blue", "Steel Blue", "Powder Blue"
    ],
    "Red": [
        "Red", "Dark Red", "Maroon", "Burgundy",
        "Wine", "Brick Red"
    ],
    "Green": [
        "Green", "Olive", "Olive Green", "Mint Green",
        "Forest Green", "Sage Green", "Emerald Green",
        "Lime Green", "Pistachio Green"
    ],
    "Yellow": [
        "Yellow", "Mustard", "Golden Yellow",
        "Pale Yellow"
    ],
    "Orange": [
        "Orange", "Rust", "Peach", "Terracotta",
        "Burnt Orange"
    ],
    "Pink": [
        "Pink", "Rose Pink", "Blush Pink",
        "Dusty Rose", "Hot Pink", "Baby Pink"
    ],
    "Purple": [
        "Purple", "Lavender", "Lilac",
        "Plum", "Mauve"
    ],
    "Brown": [
        "Brown", "Tan", "Camel", "Chocolate",
        "Coffee Brown", "Mocha"
    ],
    "White": [
        "White", "Ivory", "Off White",
        "Off-White", "Snow White"
    ],
    "Beige": [
        "Beige", "Cream", "Sand", "Khaki",
        "Light Beige", "Champagne"
    ],
    "Grey": [
        "Grey", "Gray", "Charcoal",
        "Silver", "Light Grey", "Dark Grey",
        "Slate Grey"
    ],
    "Black": [
        "Black", "Jet Black"
    ],
}
def normalize_colour(colour):
    """Normalize common colour names and spelling variations."""

    if not isinstance(colour, str) or not colour.strip():
        return None

    cleaned_colour = " ".join(
        colour.strip().lower().replace("-", " ").split()
    )

    # Common alternative names and spellings.
    aliases = {
        "gray": "grey",
        "navy blue": "navy",
        "off white": "off white",
        "olive green": "olive green",
    }

    cleaned_colour = aliases.get(
        cleaned_colour,
        cleaned_colour
    )

    for family, shades in COLOUR_FAMILIES.items():
        for shade in shades:
            normalized_shade = " ".join(
                shade.lower().replace("-", " ").split()
            )

            # Return one consistent name for aliases.
            if cleaned_colour == normalized_shade:
                if cleaned_colour == "gray":
                    return "Grey"
                if cleaned_colour == "navy blue":
                    return "Navy"

                if cleaned_colour == "off white":
                    return "Off White"

                return shade.replace("Off-White", "Off White")

    return None


def get_matching_colours(colour):
    """
    Return suggested colours for a recognized colour.
    Matching rules will be expanded in the next step.
    """

    normalized_colour = normalize_colour(colour)

    if normalized_colour is None:
        return []

    # Temporary compatibility rules, retained from our first version.
    matches = {
        "Blue": ["White", "Beige", "Grey", "Black"],
        "Navy": ["White", "Beige", "Grey", "Brown"],
        "Sky Blue": ["White", "Beige", "Navy", "Grey"],
        "Royal Blue": ["White", "Grey", "Black", "Beige"],
        "Teal": ["White", "Beige", "Brown", "Navy"],
        "Black": ["White", "Grey", "Beige", "Blue"],
        "White": ["Blue", "Black", "Grey", "Brown"],
        "Grey": ["Black", "White", "Blue", "Burgundy"],
        "Brown": ["White", "Beige", "Blue", "Cream"],
        "Red": ["Black", "White", "Beige", "Navy"],
        "Green": ["White", "Beige", "Black", "Brown"],
        "Yellow": ["White", "Blue", "Grey", "Black"],
        "Orange": ["White", "Beige", "Navy", "Brown"],
        "Purple": ["White", "Grey", "Black", "Beige"],
        "Pink": ["White", "Grey", "Navy", "Black"],
        "Navy": ["White", "Beige", "Grey", "Brown"],
        "Beige": ["White", "Brown", "Blue", "Black"],
        "Cream": ["Brown", "Blue", "Green", "Black"],
        "Burgundy": ["White", "Grey", "Black", "Beige"],
    }

    # If a shade has no specific rule yet, use its family.
    family_for_colour = {
        shade: family
        for family, shades in COLOUR_FAMILIES.items()
        for shade in shades
    }

    family = family_for_colour[normalized_colour]

    if normalized_colour in matches:
        return matches[normalized_colour]

    family_defaults = {
        "Blue": ["White", "Beige", "Grey", "Black"],
        "Red": ["White", "Black", "Beige", "Navy"],
        "Green": ["White", "Beige", "Black", "Brown"],
        "Yellow": ["White", "Blue", "Grey", "Black"],
        "Orange": ["White", "Beige", "Navy", "Brown"],
        "Pink": ["White", "Grey", "Navy", "Black"],
        "Purple": ["White", "Grey", "Black", "Beige"],
        "Brown": ["White", "Beige", "Blue", "Black"],
        "White": ["Blue", "Black", "Grey", "Brown"],
        "Beige": ["White", "Brown", "Blue", "Black"],
        "Grey": ["Black", "White", "Blue", "Burgundy"],
        "Black": ["White", "Grey", "Beige", "Blue"],
    }

    return family_defaults[family]



def score_colour_match(base_colour, suggested_colour):
    """
    Give a basic compatibility score out of 100
    and explain the colour combination.
    """

    base = normalize_colour(base_colour)
    suggested = normalize_colour(suggested_colour)

    if base is None or suggested is None:
        return {
            "colour": suggested_colour,
            "score": 0,
            "reason": "One or both colours are not recognized."
        }

    if base == suggested:
        return {
            "colour": suggested,
            "score": 50,
            "reason": "The colours are the same; this can create a monochromatic outfit."
        }

    neutrals = {
        "White", "Ivory", "Off White",
        "Beige", "Cream", "Sand",
        "Grey", "Charcoal", "Silver",
        "Black"
    }

# Check whether a specific rule exists for this colour pair.
    pair_rules = COLOUR_PAIR_RULES.get(base, {})
    specific_rule = pair_rules.get(suggested)

    if specific_rule:
        score, reason = specific_rule

        return {
            "colour": suggested,
            "score": score,
            "reason": reason
        }
    
    if suggested in neutrals:
        return {
            "colour": suggested,
            "score": 90,
            "reason": f"{suggested} is a versatile neutral that pairs well with many colours."
        }

    if base in neutrals:
        return {
            "colour": suggested,
            "score": 85,
            "reason": f"{suggested} adds colour while {base} keeps the outfit versatile."
        }


    # Fall back to the existing matching-colour rules.
    matching_colours = get_matching_colours(base)

    if suggested in matching_colours:
        return {
            "colour": suggested,
            "score": 85,
            "reason": f"{suggested} is a suggested match for {base}."
        }


    return {
        "colour": suggested,
        "score": 60,
        "reason": f"{base} and {suggested} may work together depending on their shades and the outfit."
    }



# Specific colour combinations and their initial scores.
# These are styling rules, not scores learned by an AI model.

COLOUR_PAIR_RULES = {
    "Navy": {
        "White": (95, "A classic combination with clear contrast."),
        "Beige": (92, "A balanced, elegant neutral combination."),
        "Grey": (88, "A subtle and versatile combination."),
        "Orange": (88, "A stylish contrast between cool and warm colours."),
        "Brown": (82, "An earthy combination that works well with suitable shades."),
    },
    "Blue": {
        "White": (95, "A fresh, classic combination."),
        "Beige": (90, "A soft, balanced combination."),
        "Orange": (88, "A bold contrast between cool and warm colours."),
        "Grey": (88, "A versatile, understated combination."),
    },
    "Green": {
        "White": (92, "A clean, fresh combination."),
        "Beige": (92, "A natural, earthy combination."),
        "Brown": (88, "An earthy combination with a coordinated feel."),
        "Black": (85, "A strong contrast that can create a modern look."),
    },
    "Red": {
        "White": (92, "A crisp, high-contrast combination."),
        "Black": (90, "A bold, classic combination."),
        "Navy": (85, "A balanced combination of strong colours."),
        "Beige": (85, "A softer contrast that tones down the red."),
    },
    "Black": {
        "White": (95, "A timeless, high-contrast combination."),
        "Grey": (90, "A coordinated monochromatic combination."),
        "Beige": (90, "A neutral combination with softer contrast."),
        "Blue": (88, "A versatile combination."),
    },
    "White": {
        "Navy": (95, "A timeless combination with clear contrast."),
        "Blue": (95, "A fresh and versatile combination."),
        "Green": (92, "A clean, fresh combination."),
        "Red": (92, "A crisp, high-contrast combination."),
    },
    "Grey": {
        "White": (92, "White creates a clean, balanced contrast with grey."),
        "Black": (90, "Black and grey create a coordinated, modern look."),
        "Navy": (90, "Navy adds depth while grey keeps the outfit balanced."),
        "Beige": (88, "Beige adds warmth to a neutral grey outfit."),
        "Blue": (88, "Blue adds colour while complementing grey."),
        "Burgundy": (88, "Burgundy adds rich colour to a neutral grey outfit."),
        "Green": (85, "Green adds a natural pop of colour to grey."),
        "Brown": (85, "Brown adds warmth to a grey outfit."),
        "Pink": (85, "Pink softens the neutral look of grey."),
        "Purple": (85, "Purple adds a colourful accent to grey."),
        "Red": (85, "Red creates a bold accent against grey."),
        "Orange": (85, "Orange adds a warm contrast to grey."),
    },
    "Sage Green": {
        "White": (95, "White creates a fresh, clean contrast with muted sage green."),
        "Beige": (93, "Beige complements sage green with a soft, earthy palette."),
        "Brown": (90, "Brown reinforces the natural, earthy tones of sage green."),
        "Grey": (87, "Grey creates a subtle, understated combination with sage green."),
        "Navy": (84, "Navy adds depth and contrast to muted sage green."),
        "Black": (82, "Black creates a stronger contrast with sage green."),
    },

    "Dusty Rose": {
        "White": (95, "White creates a fresh contrast with the muted pink tone."),
        "Grey": (93, "Grey balances dusty rose with a soft, understated look."),
        "Beige": (92, "Beige complements dusty rose with warm, muted tones."),
        "Navy": (90, "Navy adds depth and contrast to dusty rose."),
        "Brown": (86, "Brown creates a warm, earthy combination with dusty rose."),
        "Black": (85, "Black adds a sharper contrast to dusty rose."),
    },

    "Khaki": {
        "White": (94, "White creates a clean contrast with khaki."),
        "Navy": (92, "Navy pairs well with khaki for a classic look."),
        "Black": (88, "Black creates a strong, versatile contrast with khaki."),
        "Brown": (86, "Brown creates a coordinated earthy palette with khaki."),
        "Blue": (90, "Blue adds colour while complementing neutral khaki."),
    },

    "Lavender": {
        "Grey": (93, "Grey complements lavender with a soft, balanced combination."),
        "White": (92, "White creates a light, fresh contrast with lavender."),
        "Navy": (90, "Navy adds depth to the soft lavender tone."),
        "Beige": (88, "Beige creates a gentle, warm neutral pairing with lavender."),
        "Black": (87, "Black provides a sharper contrast with lavender."),
    },
}


def rank_matching_colours(base_colour, candidate_colours=None):
    """
    Rank candidate colours from highest to lowest compatibility score.
    """

    if candidate_colours is None:
        candidate_colours = [
            "White",
            "Beige",
            "Grey",
            "Black",
            "Blue",
            "Orange",
            "Brown",
            "Green",
            "Red",
            "Pink",
            "Purple",
        ]

    results = []

    for colour in candidate_colours:
        result = score_colour_match(base_colour, colour)

        if result["score"] > 0:
            results.append(result)

    # Sort by score, highest first.
    results.sort(key=lambda item: item["score"], reverse=True)

    return results



def get_outfit_recommendations(clothing_type, base_colour):
    """
    Recommend outfit colours based on the clothing type and colour.
    """

    if not isinstance(clothing_type, str) or not clothing_type.strip():
        return {
            "clothing_type": clothing_type,
            "base_colour": base_colour,
            "message": "Please provide a valid clothing type.",
            "recommendations": []
        }

    clothing_type = clothing_type.strip().lower()

    clothing_categories = {
        "shirt": ["trousers", "jeans"],
        "t-shirt": ["trousers", "jeans"],
        "kurta": ["trousers"],
        "trousers": ["shirt", "t-shirt"],
        "jeans": ["shirt", "t-shirt"],
        "dress": ["shoes", "jacket", "accessories"],
    }

    if clothing_type not in clothing_categories:
        return {
            "clothing_type": clothing_type,
            "base_colour": base_colour,
            "message": "Unsupported clothing type.",
            "recommendations": []
        }

    # Choose candidate colours based on the clothing item.
    candidate_colours_by_type = {
        "shirt": [
            "White", "Beige", "Grey", "Black",
            "Navy", "Blue", "Brown", "Green",
            "Orange", "Pink", "Purple"
        ],
        "t-shirt": [
            "White", "Black", "Grey", "Blue",
            "Beige", "Green", "Navy", "Brown",
            "Red", "Orange", "Pink"
        ],
        "kurta": [
            "White", "Beige", "Grey", "Black",
            "Navy", "Blue", "Brown", "Green",
            "Maroon", "Pink"
        ],
        "trousers": [
            "White", "Beige", "Grey", "Black",
            "Navy", "Blue", "Brown", "Olive",
            "Khaki"
        ],
        "jeans": [
            "Blue", "Navy", "Black", "Grey",
            "White", "Beige", "Brown"
        ],
        "dress": [
            "Black", "Navy", "White", "Beige",
            "Grey", "Brown", "Blue", "Green",
            "Red", "Pink", "Purple"
        ],
    }

    normalized_base = normalize_colour(base_colour)

    if normalized_base is None:
        return {
            "clothing_type": clothing_type,
            "base_colour": base_colour,
            "message": "Unsupported colour. Please provide a recognized colour.",
            "recommendations": []
        }

    # Exclude the base colour from the default recommendations.
    candidates = [
        colour
        for colour in candidate_colours_by_type[clothing_type]
        if normalize_colour(colour) != normalized_base
    ]

    recommendations = rank_matching_colours(
        normalized_base,
        candidates
    )

    return {
        "clothing_type": clothing_type,
        "base_colour": normalized_base,
        "recommended_items": clothing_categories[clothing_type],
        "recommendations": recommendations
    }
