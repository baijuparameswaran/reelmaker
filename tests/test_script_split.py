from reel_app.script_gen import split_script_into_scenes, simple_script_from_idea

def test_split_not_empty():
    idea = "test concept"
    script = simple_script_from_idea(idea)
    scenes = split_script_into_scenes(script)
    assert scenes, "Scenes should not be empty"
    assert all(s.duration > 0 for s in scenes)
    # Ensure title line excluded
    assert all('Title:' not in s.text for s in scenes)
