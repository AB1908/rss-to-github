from datetime import datetime
from feedparser import FeedParserDict, parse
from github import Github
from github.ContentFile import ContentFile
from github.Repository import Repository
from github.GithubException import UnknownObjectException
from markdownify import markdownify as md

FEED_URL = "https://www.obsidianroundup.org/blog/rss/"
USER_NAME = "AB1908"
# COMMUNITY_REPO = "obsidian-community/obsidian-hub"
REPO_NAME = "obsidian-hub"
COMMUNITY_REPO = f"{USER_NAME}/{REPO_NAME}"
ROUNDUP_FOLDER_PATH = "01 - Community/Obsidian Roundup"
ROUNDUP_BRANCH = "roundup"
LABELS = "scripted update"

def date_conversion(parsed_feed_datetime: FeedParserDict) -> datetime:
    """Converts published_parsed attribute of a feed item into a pythonic datetime object"""
    return datetime(year=parsed_feed_datetime.tm_year, month=parsed_feed_datetime.tm_mon, day=parsed_feed_datetime.tm_mday, hour=parsed_feed_datetime.tm_hour, minute=parsed_feed_datetime.tm_min, second=parsed_feed_datetime.tm_sec)

def datetime_from_parsed_feed_datetime(entry: FeedParserDict) -> str:
    """Returns ISO formatted string for feed published timestamp"""
    pythonic_datetime = date_conversion(entry.published_parsed)
    return pythonic_datetime.isoformat()

def date_from_parsed_feed_datetime(entry: FeedParserDict) -> str:
    """Returns ISO formatted string for feed published date"""
    pythonic_datetime = date_conversion(entry.published_parsed)
    return pythonic_datetime.strftime("%Y-%m-%d")

def does_previous_exist_in_hub():
    pass

def is_roundup_post(entry: FeedParserDict) -> bool:
    if entry.title.startswith('🌠'):
        return True
    else:
        return False

def convert_feed_html(html_content: str) -> str:
    return md(html_content)

def get_normalized_file_name(entry: FeedParserDict) -> str:
    return f"{date_from_parsed_feed_datetime(entry)} {entry.title[2:]}.md"

def generate_file_with_hub_yaml(entry: FeedParserDict) -> str:
    frontmatter: str = f"---\nlink: {entry.link}\nauthor: {entry.author}\npublished: {datetime_from_parsed_feed_datetime(entry)}\npublish: true\n---\n\n"
    return frontmatter+convert_feed_html(entry.content[0].value)

def merge_main_into_branch(repo: Repository):
    repo.merge(base=ROUNDUP_BRANCH, head="main")

def add_file_to_repo(entry: FeedParserDict, repo: Repository):
    file_contents:str = generate_file_with_hub_yaml(entry)
    # TODO: Handle 422s for when the file exists already
    return repo.create_file(f"{ROUNDUP_FOLDER_PATH}/{get_normalized_file_name(entry)}", "feat: add new feed item", file_contents, branch=ROUNDUP_BRANCH)# ["commit"]

def open_pr_against_main(entry: FeedParserDict, repo: Repository):
    # todo: assign labels, add correct PR body
    # needs to be done via issues endpoint apparently
    title = f"Add roundup post for {date_from_parsed_feed_datetime(entry)}"
    body = f"Title: {entry.title}\nBody: {entry.link}"
    pr = repo.create_pull(title=title, body=body, base=repo.default_branch, head=ROUNDUP_BRANCH, maintainer_can_modify=True)
    pr.add_to_labels(LABELS)

def entries_not_synced(synced_list: list[ContentFile], sync_pending_list: list[FeedParserDict]):
    # The last file is a folder note and not the last synced item
    last_repo_item_name = synced_list[-2].name
    pending_file_names = [get_normalized_file_name(entry) for entry in sync_pending_list]
    return sync_pending_list[0:pending_file_names.index(last_repo_item_name)]
    
def branch_exists(repo: Repository) -> bool:
    return True if ROUNDUP_BRANCH in [i.name for i in repo.get_branches()] else False

def create_branch(repo: Repository) -> None:
    try:
        main_head_sha = repo.get_branch(repo.default_branch).commit.sha
        repo.create_git_ref(f"refs/heads/{ROUNDUP_BRANCH}", main_head_sha)
        return
    except UnknownObjectException:
        # https://stackoverflow.com/a/67560638/13285428
        # I had no idea 404s were because of scopes
        print("Check your scopes")
    
def is_authenticated(g: Github) -> bool:
    try:
        return True if g.get_user().login == USER_NAME else False
    except: 
        # TODO: Check for 401 bad creds
        return False

def main():
    d = parse(FEED_URL)
    g = Github(API_KEY)
    if not is_authenticated(g):
        # TODO: Add log message for incorrect auth
        return
    obsidian_hub_repo = g.get_repo(COMMUNITY_REPO)
    list_of_roundup_files = obsidian_hub_repo.get_contents(ROUNDUP_FOLDER_PATH)
    if not branch_exists(obsidian_hub_repo):
        create_branch(obsidian_hub_repo)
    merge_main_into_branch(obsidian_hub_repo)
    # TODO: handle how multiple files are PRed
    for entry in entries_not_synced(list_of_roundup_files, d.entries):
        if is_roundup_post(entry):
            # print(get_normalized_file_name(entry))
            add_file_to_repo(entry, obsidian_hub_repo)
    open_pr_against_main(entry, obsidian_hub_repo)

if __name__ == "__main__":
    main()