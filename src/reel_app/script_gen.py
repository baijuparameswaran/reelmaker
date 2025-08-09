from typing import List
import os
import textwrap
from .models import Scene, ScriptResult

# Very naive fallback script generator

def simple_script_from_idea(idea: str) -> str:
    idea = idea.strip().rstrip('.')
    return textwrap.dedent(f"""\
    Title: {idea.title()}
    Intro: In this quick reel, we'll explore {idea} in simple terms.
    Point 1: First, understand the core concept: {idea} matters because ...
    Point 2: Next, a practical example helps: imagine ...
    Point 3: A common misconception is ... but actually ...
    Tip: Remember this takeaway so you can apply {idea} today.
    Outro: Follow for more fast explainers like this one.
    """).strip()


def split_script_into_scenes(script: str, target_total: float = 45.0) -> List[Scene]:
    # Split by lines ignoring the Title line
    lines = [l.strip() for l in script.splitlines() if l.strip()]
    content_lines = [l for l in lines if not l.lower().startswith('title:')]
    # Heuristic duration: 2.2 words/sec
    words_total = sum(len(l.split()) for l in content_lines)
    seconds_per_word = target_total / max(words_total, 1)
    scenes: List[Scene] = []
    for i, line in enumerate(content_lines):
        w = len(line.split())
        dur = round(w * seconds_per_word, 2)
        scenes.append(Scene(index=i, text=line, duration=dur))
    return scenes


def rich_script_from_idea(idea: str) -> str:
    topic = idea.strip().rstrip('.')
    title = topic.title()
    # Heuristic expansion: structured sections with short, on-screen-friendly lines
    sections = [
        f"Title: {title}",
        f"Hook: In under a minute, here's {topic} explained simply.",
        f"What it is: {topic} is a concept/technique that helps you achieve specific goals more effectively.",
        f"Core idea: Think of {topic} as a set of principles that guide how it works in practice.",
        f"How it works (1): Break it into 3 parts: the inputs, the process, and the outcome.",
        f"How it works (2): Inputs are the key ingredients you start with.",
        f"How it works (3): The process transforms those inputs step-by-step.",
        f"How it works (4): The outcome is the result you can measure or observe.",
        f"Example: Imagine applying {topic} to a real scenario—start simple and build up.",
        f"Why it matters (1): It saves time or reduces errors in common tasks.",
        f"Why it matters (2): It unlocks possibilities that are hard to do manually.",
        f"Why it matters (3): It scales—small efforts compound into big wins.",
        f"Get started (Step 1): Identify one small use-case for {topic}.",
        f"Get started (Step 2): Follow a proven checklist or tutorial.",
        f"Get started (Step 3): Measure results and iterate.",
        f"Common pitfall: Trying to do everything at once—start tiny.",
        f"Pro tip: Keep feedback loops short—learn, adjust, repeat.",
        f"Recap: {topic}: what it is, how it works, why it matters, and a 3-step start.",
        f"Outro: Save this for later and share if you found it useful.",
    ]
    return "\n".join(sections)


def generate_script_and_scenes(idea: str) -> ScriptResult:
    # Future: If OPENAI_API_KEY present, call OpenAI; else fallback.
    
    if os.getenv('OPENAI_API_KEY'):
        try:
            # Placeholder: still use simple until integrated.
            #script = simple_script_from_idea(idea)
            from openai import OpenAI  # type: ignore
            print(f"WEEENNTTT to OPENAOOOOOIII")
            client = OpenAI()
            prompt = (
                "You are a concise scriptwriter for short vertical video reels. "
                "Write a clear, engaging script in English about the user's idea. "
                "Return 12-18 short lines (each under ~18 words), one idea per line, covering: "
                "hook, definition, core concepts (3-4 lines), example, why it matters (2-3), getting started (3), pitfalls/tips (2-3), recap, outro. "
                "Do not add numbering unless it is part of the text; keep each line self-contained.\n\n"
                f"User idea: {idea}\n\n"
                )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You write short, structured reel scripts."},
                         {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=600,
            )
            text = resp.choices[0].message.content.strip() if resp.choices else ""
            # Normalize to lines
            lines = [l.strip("- •\t ") for l in text.splitlines() if l.strip()]
            # Ensure first line is a Title: ...
            if not (lines and lines[0].lower().startswith("title:")):
                lines = [f"Title: {idea.strip().rstrip('.').title()}"] + lines
            script = "\n".join(lines)
        except Exception:
            # Fallback to rich heuristic if OpenAI not available or fails
            script = rich_script_from_idea(idea)
            #script = simple_script_from_idea(idea)
    scenes = split_script_into_scenes(script)
    return ScriptResult(script=script, scenes=scenes)
