"""
Static onboarding question bank.
These 10 questions run on first login to build the user's initial profile.
They are general (not track-specific) and help the AI understand the user's baseline.
"""

ONBOARDING_QUESTIONS = [
    {
        "id":      "ob1",
        "text":    "How would you describe your overall mood over the past week?",
        "options": ["Very good", "Mostly okay", "Mixed", "Mostly low", "Very low"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😊", "🙂", "😐", "😔", "😢"],
    },
    {
        "id":      "ob2",
        "text":    "How well have you been sleeping recently?",
        "options": ["Very well", "Mostly fine", "Somewhat disturbed", "Poorly", "Hardly at all"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😴", "🙂", "😐", "😔", "😩"],
    },
    {
        "id":      "ob3",
        "text":    "How often have you felt overwhelmed or under pressure lately?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Almost always"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😊", "🙂", "😐", "😟", "😩"],
    },
    {
        "id":      "ob4",
        "text":    "Do you feel supported by the people around you (friends, family, colleagues)?",
        "options": ["Very supported", "Mostly yes", "Somewhat", "Not really", "Not at all"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["🤗", "🙂", "😐", "😔", "😞"],
    },
    {
        "id":      "ob5",
        "text":    "Have you experienced any stressful events in the past month?",
        "options": ["No major stress", "Minor stress", "Moderate stress", "Significant stress", "Severe stress"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😊", "🙂", "😐", "😟", "😰"],
    },
    {
        "id":      "ob6",
        "text":    "How is your energy and motivation on most days?",
        "options": ["High", "Moderate", "Low", "Very low", "Non-existent"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["⚡", "🙂", "😐", "😔", "😩"],
    },
    {
        "id":      "ob7",
        "text":    "Have you felt unsafe or threatened in any situation recently?",
        "options": ["No, I feel safe", "Mildly uncomfortable", "Sometimes unsafe", "Often unsafe", "Constantly unsafe"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😊", "🙂", "😐", "😟", "😱"],
    },
    {
        "id":      "ob8",
        "text":    "How often do you worry about things outside your control?",
        "options": ["Rarely", "Occasionally", "Sometimes", "Often", "Almost constantly"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😊", "🙂", "😐", "😰", "😱"],
    },
    {
        "id":      "ob9",
        "text":    "Have you been able to enjoy activities you usually like?",
        "options": ["Yes, fully", "Mostly yes", "Somewhat", "Barely", "Not at all"],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["😊", "🙂", "😐", "😔", "😢"],
    },
    {
        "id":      "ob10",
        "text":    "What brings you to SafeSpace today?",
        "options": [
            "Just curious / exploring",
            "Managing stress or anxiety",
            "Feeling low or depressed",
            "Dealing with a difficult relationship or situation",
            "I have experienced harassment or feel unsafe",
        ],
        "scores":  [0, 1, 2, 3, 4],
        "emoji":   ["🔍", "😰", "😔", "😟", "🚨"],
    },
]