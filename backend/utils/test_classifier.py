"""
AIMHHC — Classifier Test Script
Run this from the backend/ folder:
    cd backend
    python ../test_classifier.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from engine.sentiment import analyze_sentiment
from engine.keywords import detect_keywords, keyword_score
from engine.classifier import run_classification, classify_input
from models.schemas import TrackType, AssessmentAnswer

# ─── Color helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ─── Test Cases ───────────────────────────────────────────────────────────────
# Format: (input_text, expected_risk_level, label)
CHAT_TESTS = [
    # ── MENTAL HEALTH — HIGH risk ──────────────────────────────────────────────
    ("I want to kill myself, there's no point anymore",             "high",   "MH-H1 Suicidal ideation"),
    ("I hate myself so much, I'm completely worthless",             "high",   "MH-H2 Self-loathing"),
    ("marna chahta hoon, jeene se thak gaya hoon",                  "high",   "MH-H3 Hinglish crisis"),
    ("I can't go on like this, I want to end my life",              "high",   "MH-H4 Crisis - end life"),
    ("I've been cutting myself to cope with the pain",              "high",   "MH-H5 Self harm"),

    # ── MENTAL HEALTH — MEDIUM risk ───────────────────────────────────────────
    ("I feel so hopeless and sad all the time",                     "medium", "MH-M1 Hopeless + sad"),
    ("I can't sleep, I'm exhausted and can't focus on anything",    "medium", "MH-M2 Sleep + focus"),
    ("bahut udaas hoon, koi farak nahi lagta",                      "medium", "MH-M3 Hinglish sad"),
    ("I'm so anxious and overwhelmed, having panic attacks",        "medium", "MH-M4 Anxiety + panic"),
    ("I feel completely empty inside, nothing makes me happy",      "medium", "MH-M5 Emptiness"),

    # ── MENTAL HEALTH — LOW risk ──────────────────────────────────────────────
    ("I've been feeling a bit stressed with exams",                 "low",    "MH-L1 Mild exam stress"),
    ("Sometimes I feel a little lonely",                            "low",    "MH-L2 Mild loneliness"),
    ("I'm feeling okay today, just a bit tired",                    "low",    "MH-L3 Neutral/tired"),

    # ── HARASSMENT — HIGH risk ────────────────────────────────────────────────
    ("My boss threatens to fire me every day and shouts at me",     "high",   "HR-H1 Workplace threat"),
    ("Someone is blackmailing me with my private photos",           "high",   "HR-H2 Sextortion"),
    ("I'm being stalked and I'm scared for my safety",              "high",   "HR-H3 Stalking"),
    ("My colleague physically grabbed me at work",                  "high",   "HR-H4 Physical assault"),
    ("I keep getting rape threats online from strangers",           "high",   "HR-H5 Cyber threat"),

    # ── HARASSMENT — MEDIUM risk ──────────────────────────────────────────────
    ("My classmates bully me and make fun of me every day",         "medium", "HR-M1 Bullying"),
    ("Someone keeps sending me unwanted messages",                  "medium", "HR-M2 Unwanted contact"),
    ("I feel unsafe at my workplace due to verbal abuse",           "medium", "HR-M3 Verbal abuse"),

    # ── SAFE / NEUTRAL ─────────────────────────────────────────────────────────
    ("How can I improve my study habits?",                          "low",    "SAFE-1 Study question"),
    ("I just had a great day with my friends",                      "low",    "SAFE-2 Positive message"),
    ("Can you help me understand what anxiety is?",                 "low",    "SAFE-3 Info question"),
    ("I am not feeling sad at all, everything is fine",             "low",    "SAFE-4 Negation test"),
]


def run_chat_tests():
    passed = 0
    failed = 0
    results = []

    print(f"\n{BOLD}{CYAN}{'─'*65}{RESET}")
    print(f"{BOLD}{CYAN}  AIMHHC — Chat Classifier Test Suite{RESET}")
    print(f"{BOLD}{CYAN}{'─'*65}{RESET}\n")

    for text, expected, label in CHAT_TESTS:
        result   = classify_input(text)
        score    = result["risk_score"]
        cats     = result["categories"]
        is_crisis = result["is_crisis"]

        # Map score to level for comparison
        if score >= 0.50 or is_crisis:
            got = "high"
        elif score >= 0.20:
            got = "medium"
        else:
            got = "low"

        ok = got == expected
        if ok:
            passed += 1
            status = f"{GREEN}PASS{RESET}"
        else:
            failed += 1
            status = f"{RED}FAIL{RESET}"

        results.append((label, expected, got, score, cats, ok))

        short_text = text[:48] + "..." if len(text) > 48 else text
        print(f"  [{status}] {label}")
        print(f"         Text     : \"{short_text}\"")
        print(f"         Expected : {expected:6s}  |  Got : {got:6s}  |  Score : {score:.3f}")
        if cats:
            print(f"         Categories: {', '.join(cats)}")
        print()

    total    = passed + failed
    accuracy = (passed / total) * 100 if total else 0

    print(f"{BOLD}{'─'*65}{RESET}")
    print(f"  Results : {GREEN}{passed} passed{RESET} / {RED}{failed} failed{RESET} / {total} total")
    print(f"  Accuracy: {BOLD}{accuracy:.1f}%{RESET}")
    print(f"{'─'*65}\n")

    return passed, failed, accuracy, results


# ─── MCQ / Assessment simulation ──────────────────────────────────────────────

def make_answers(scores):
    return [AssessmentAnswer(question_id=f"q{i+1}", answer="test", score=s)
            for i, s in enumerate(scores)]


ASSESSMENT_TESTS = [
    # (track, scores_list, free_text, expected_risk, label)
    (TrackType.mental_health, [3,3,4,3,4], "I feel hopeless and can't sleep",    "high",   "ASMT-MH-HIGH"),
    (TrackType.mental_health, [2,2,2,1,2], "I've been a bit stressed lately",    "medium", "ASMT-MH-MED"),
    (TrackType.mental_health, [0,0,1,0,0], "Feeling okay, just checking in",     "low",    "ASMT-MH-LOW"),
    (TrackType.harassment,    [3,4,3,4,3], "My boss shouts and threatens me",    "high",   "ASMT-HR-HIGH"),
    (TrackType.harassment,    [2,1,2,1,2], "Sometimes I feel unsafe at work",    "medium", "ASMT-HR-MED"),
    (TrackType.harassment,    [0,0,0,1,0], "Everything is mostly fine at work",  "low",    "ASMT-HR-LOW"),
]


def run_assessment_tests():
    passed = 0
    failed = 0

    print(f"\n{BOLD}{CYAN}  Assessment (MCQ) Classifier Tests{RESET}")
    print(f"{BOLD}{CYAN}{'─'*65}{RESET}\n")

    for track, scores, free_text, expected, label in ASSESSMENT_TESTS:
        answers = make_answers(scores)
        risk_level, final_score, sentiment, kw_matches = run_classification(
            track=track,
            answers=answers,
            free_text=free_text,
        )
        got = risk_level.value

        ok = got == expected
        if ok:
            passed += 1
            status = f"{GREEN}PASS{RESET}"
        else:
            failed += 1
            status = f"{RED}FAIL{RESET}"

        print(f"  [{status}] {label}  (track: {track.value})")
        print(f"         Expected : {expected:6s}  |  Got : {got:6s}  |  Score : {final_score:.3f}")
        print(f"         Sentiment: {sentiment.label} ({sentiment.compound:.3f})")
        print()

    total    = passed + failed
    accuracy = (passed / total) * 100 if total else 0

    print(f"{BOLD}{'─'*65}{RESET}")
    print(f"  Results : {GREEN}{passed} passed{RESET} / {RED}{failed} failed{RESET} / {total} total")
    print(f"  Accuracy: {BOLD}{accuracy:.1f}%{RESET}")
    print(f"{'─'*65}\n")

    return passed, failed, accuracy


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    chat_p, chat_f, chat_acc, _ = run_chat_tests()
    asmt_p, asmt_f, asmt_acc    = run_assessment_tests()

    total_p   = chat_p + asmt_p
    total_f   = chat_f + asmt_f
    total     = total_p + total_f
    overall   = (total_p / total) * 100 if total else 0

    print(f"\n{BOLD}{'═'*65}{RESET}")
    print(f"{BOLD}  OVERALL RESULTS{RESET}")
    print(f"{'═'*65}")
    print(f"  Chat classifier accuracy   : {chat_acc:.1f}%  ({chat_p}/{chat_p+chat_f})")
    print(f"  Assessment accuracy        : {asmt_acc:.1f}%  ({asmt_p}/{asmt_p+asmt_f})")
    print(f"  Overall accuracy           : {BOLD}{overall:.1f}%{RESET}  ({total_p}/{total})")
    print(f"{'═'*65}\n")

    if overall >= 80:
        print(f"  {GREEN}{BOLD}Classifier performance: GOOD — ready for submission!{RESET}\n")
    elif overall >= 65:
        print(f"  {YELLOW}{BOLD}Classifier performance: ACCEPTABLE — document edge cases.{RESET}\n")
    else:
        print(f"  {RED}{BOLD}Review failed cases and adjust thresholds.{RESET}\n")
