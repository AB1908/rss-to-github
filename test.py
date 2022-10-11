from rss_to_github import *
from feedparser import parse

dummy_rss_file = "./feed.xml"
d = parse(dummy_rss_file)

def test_datetime_conversion():
    assert datetime_from_parsed_feed_datetime(d.entries[0]) == "2022-10-10T12:30:29"

def test_date_conversion():
    assert date_from_parsed_feed_datetime(d.entries[0]) == "2022-10-10"
    
def test_roundup_feed_item():
    assert is_roundup_post(d.entries[0]) == False
    assert is_roundup_post(d.entries[1]) == True
    
def test_hub_file_generation():
    test_content = f"""---\nlink: https://www.obsidianroundup.org/the-konik-method-for-making-notes/\nauthor: Eleanor Konik\npublished: 2022-10-10T12:30:29\npublish: true\n---\n\n🌠 Test XML encoded content"""
    test_content_with_converted_markdown = """---\nlink: https://www.obsidianroundup.org/obsidian-october/\nauthor: Eleanor Konik\npublished: 2022-09-24T12:30:10\npublish: true\n---\n\nIn The Community
----------------

* It's almost October, so it's time to gear up for this year's annual Obsidian October event. The theme is "Back to School" (best creation for college students, graduate students, and specific subject matter will earn bonus prizes) and they've expanded the categories to include: new plugin (or significant update), video, demo vault, or written content. Here's the 
 [daily progress and learnings](https://forum.obsidian.md/t/obsidian-october-2022-daily-progress-and-learnings/43767) thread, and the 
 [official hub page](https://publish.obsidian.md/hub/01+-+Community/Events/Obsidian+October+2022). There's more clarification in Discord. If anyone is looking to contribute to an existing plugin, the 
 [Hub has collected some issues of interest](https://publish.obsidian.md/hub/01+-+Community/Contributing+to+the+Community/Plugins+seeking+help).
"""
    assert generate_file_with_hub_yaml(d.entries[0]) == test_content
    assert generate_file_with_hub_yaml(d.entries[1]) == test_content_with_converted_markdown
