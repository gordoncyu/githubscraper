from datetime import datetime, timedelta, timezone
from itertools import chain
import json
import os

from github.Issue import Issue
from github.IssueComment import IssueComment
from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment
from github.RepositoryDiscussion import RepositoryDiscussion
def mkdirp (name: str, mode: int = 511):
    os.makedirs(name, mode, True)

import time
from typing import Any, Callable, Optional, TypeVar
from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from dataclasses import dataclass
from returns.result import Failure, Result, Success, safe
from returns.maybe import Maybe, Some, Nothing, _Nothing
from sumtypes import sumtype
from pampy import match, _

from toolz.curried import pipe, map, reduce, excepts
from toolz import excepts

T = TypeVar("T")
def nonesafe(f: Callable[[], T]) -> Maybe[T]:
    try:
        return Some(f())
    except AttributeError as e:
        if "'NoneType' object" in str(e):
            return Nothing
        raise e

from dotenv import load_dotenv
load_dotenv()

g = Github(os.getenv("GITHUB_API_KEY"))

g.get_user().name

#|%%--%%| <aTRolNJBdo|ZxzLzQBzQC>

languages: list[str] = [
    "Python",
    "Java",
    "Go",
    "JavaScript",
    "C++",
    "TypeScript",
    "PHP",
    "Ruby",
    "C",
    "C#",
    "Nix",
    "Shell",
    "Rust",
    "Scala",
    "Kotlin",
    "Swift",
    "Dart",
    "Groovy",
    "Perl",
    "Lua",
    "DM",
    "SystemVerilog",
    "Objective-C",
    "Elixir",
    "CodeQL",
    "OCaml",
    "Haskell",
    "PowerShell",
    "Erlang",
    "Emacs Lisp",
    "Julia",
    "Clojure",
    "R",
    "CoffeeScript",
    "F#",
    "Verilog",
    "WebAssembly",
    "MLIR",
    "Bicep",
    "Fortran",
    "Cython",
    "GAP",
    "MATLAB",
    "Puppet",
    "Sass",
    "JetBrains MPS",
    "Smalltalk",
    "Vala",
    "Haxe",
    "Pascal",
]

#|%%--%%| <ZxzLzQBzQC|Hji763MLh3>

# print(reduce(
#     lambda acc, language: acc + 
#     f"{language}: {
#         'yes' if excepts(
#             IndexError, 
#             lambda: g.search_repositories(f'language:{language}')[0],
#             lambda _: False
#             ) else 'no'}\n",
#         languages,
#         ""))

#|%%--%%| <Hji763MLh3|ST1E4GYNEo>

class LRI:
    language: str
    rl: PaginatedList[Repository]
    _search_init_args: Maybe[tuple]
    _ind: int
    current: Maybe[Repository] = Nothing
    _exhausted: bool

    def __init__(self, language: str, search_init_and_rl_maybe: Maybe[tuple[tuple[Any], PaginatedList[Repository]]] = Nothing, ind_maybe: Maybe[int] = Nothing, exhausted_maybe: Maybe[bool] = Nothing):
        self.language = language

        self._search_init_args, self.rl = search_init_and_rl_maybe.value_or((Nothing, g.search_repositories(f"language:{language}", "stars", "desc"))) # pyright: ignore

        self._ind = ind_maybe.value_or(-1)

        self._exhausted = exhausted_maybe.value_or(False)

    def next(self) -> Result[Repository, StopIteration]:
        if self._exhausted:
            return Failure(StopIteration)

        self._ind += 1

        # match (self._ind, self.current):
        #     case (-1, Nothing):
        #         self._ind = 0
        #     case (n, Some(Repository())):
        #         self._ind = n + 1
        #     case (n, Nothing):
        #         pass

        nxt = excepts(
                IndexError, 
                lambda: Success(self.rl[self._ind]), 
                lambda _: Failure(StopIteration)
                )()

        # match nxt:
        #     case Success(repo): 
        #         self.current = Some(repo)
        #     case Failure(_):
        #         pass

        self.current, self._exhausted = match(nxt, # pyright: ignore
                             Success, lambda repo_w: (Some(repo_w.unwrap()), False),
                             Failure, (Nothing, True),
                             )

        return nxt

    def jsonable(self) -> object:
        return {
                "language": self.language,
                "ind": self._ind,
                "search_init_args": self._search_init_args.value_or(None),
                "exhausted": self._exhausted,
                }

    @staticmethod
    def from_jsonable(info: str):
        return LRI(info["language"], Maybe.from_optional(info["search_init_args"]), Some(info["ind"]), Some(info["exhausted"])) # pyright: ignore

lris: list[LRI]

scraped_per_lang: dict[str,int]

scraped_repos: set[str]

RESUME_FROM_PROGRESS = True

if RESUME_FROM_PROGRESS and os.path.exists("./progress.json"):
    print("Resuming from progress.json")
    with open("./progress.json") as f:
        scraped_repos_list, scraped_per_lang, jsonables = json.loads(f.read())
        scraped_repos = set(scraped_repos_list)
        lris = [LRI.from_jsonable(jsonable) for jsonable in jsonables]

else:
    lris = [
        LRI(language=language) for language in languages
        ]

    scraped_per_lang = {language: 0 for language in languages}

    scraped_repos = set()

start_language: Maybe[str] = Nothing

if RESUME_FROM_PROGRESS:
    min_count = min(scraped_per_lang.values())
    for lang, count in scraped_per_lang.items():
        if count == min_count:
            start_language = Some(lang)
            break

def print_rlim():
    rlim = g.get_rate_limit()
    print(f"{rlim.core}, ttr: {rlim.core.reset - datetime.now(timezone.utc)}")

try:
    while True:

        for lri in lris:
            match start_language:
                case Some(lri.language): start_language = Nothing
                case Some(other_lang): continue
                case nothing: pass

            print(f"Scanning language: {lri.language}")

            print_rlim()
            while True:
                repo_maybe: Maybe[Repository] = Nothing
                match lri.next():
                    case Success(nxt):
                        repo_maybe = Some(nxt)
                    case Failure(StopIteration):
                        break

                if repo_maybe.unwrap().full_name in scraped_repos:
                    continue

                break

            match repo_maybe:
                case Some(v): 
                    repo = v
                    print(f"Scanning repo {repo.full_name}")
                case Nothing:
                    print("Language exhausted")
                    continue

            repo_path = f"./scraped/{repo.full_name}"

            issues = repo.get_issues(
                    state="all",
                    sort="created",
                    direction="asc",
                    )
            pulls = repo.get_pulls(
                    state="all",
                    sort="created",
                    direction="asc",
                    )

            pull_count = pulls.totalCount
            issue_count = issues.totalCount - pull_count

            mkdirp(repo_path)
            with open(f"{repo_path}/main.json", "w") as f:
                f.write(json.dumps({
                    "full_name": repo.full_name,
                    "id": repo.id,
                    "url": repo.url,
                    "language": repo.language,
                    "languages": repo.get_languages(),
                    "issue_count": issue_count,
                    "pull_count": pull_count,
                    }))

            def json_starter(starter: Issue | PullRequest):
                out = {
                    "id": starter.id,
                    "url": starter.url,
                    "user": (starter.user.id, starter.user.login),
                    "title": starter.title,
                    "body": starter.body,
                    "created_at": starter.created_at.timestamp(),
                    "last_modified": starter.last_modified,
                    }

                if isinstance(starter, Issue) or isinstance(starter, PullRequest):
                    out["number"] = starter.number
                    out["state"] = starter.state

                return json.dumps(out)

            def json_comment(comment: IssueComment | PullRequestComment):
                return json.dumps({
                    "id": comment.id,
                    "url": comment.url,
                    "user": (comment.user.id, comment.user.login),
                    "body": comment.body,
                    "created_at": comment.created_at.timestamp(),
                    "last_modified": comment.last_modified,
                    })

            for issue in issues:
                if issue == None:
                    continue

                if issue.pull_request != None:
                    # print(f"Skipping pr {issue.title}")
                    continue

                issue_path = f"{repo_path}/issues/{str(issue.id)}"

                mkdirp(issue_path)

                print(f"Scanning isssue {issue.title}")

                with open(f"{issue_path}/main.json", "w") as f:
                    f.write(json_starter(issue))

                for comment in issue.get_comments():
                    def op():
                        print(f"Saving isssue comment {''.join(map(lambda c: "\\n" if c == "\n" else c, comment.body[:100]))}") # pyright: ignore
                        with open(f"{issue_path}/{str(comment.id)}.json", "w") as f:
                            f.write(json_comment(comment))
                    nonesafe(op)
                    # Doing this is stupid. But it's only because python is stupid and gave me this error:
                    """
    Saving pull review comment PR from (smartip-io:patch-2) updated as requested.
    Traceback (most recent call last):
      File "/home/gordo/school/474/proj/scrape_convos.py", line 317, in <module>
        f.write(json_comment(comment))
                ^^^^^^^^^^^^^^^^^^^^^
      File "/home/gordo/school/474/proj/scrape_convos.py", line 255, in json_comment
        "user": (comment.user.id, comment.user.login),
                 ^^^^^^^^^^^^^^^
    AttributeError: 'NoneType' object has no attribute 'id'
    """ # WTF DO YOU MEAN USER IS NOT OPTIONAL IT SHOULD NEVER BE NONE. I SHOULDN'T HAVE TO NULL-CHECK EVERY SINGLE ATTRIBUTE ACCESS

            # for discussion in repo.get_discussions( # requires graphql, too lazy to do, most repos don't have discussions anyway
            #         answered=None,
            #         category_id=None,
            #         states=None,
            #         ):

            for pull in pulls:
                if pull == None:
                    continue

                pull_path = f"{repo_path}/pulls/{str(pull.id)}"

                mkdirp(pull_path)

                print(f"Scanning pull {pull.title}")

                with open(f"{pull_path}/main.json", "w") as f:
                    f.write(json_starter(pull))

                for comment in pull.get_issue_comments():
                    def op():
                        print(f"Saving pull comment {''.join(map(lambda c: "\\n" if c == "\n" else c, comment.body[:100]))}") # pyright: ignore
                        with open(f"{pull_path}/{str(comment.id)}.json", "w") as f:
                            f.write(json_comment(comment))
                    nonesafe(op)

                for comment in pull.get_review_comments(
                            sort="created",
                            direction="asc",
                        ):
                    def op():
                        print(f"Saving pull review comment {''.join(map(lambda c: "\\n" if c == "\n" else c, comment.body[:100]))}") # pyright: ignore
                        with open(f"{pull_path}/{str(comment.id)}_review.json", "w") as f:
                            f.write(json_comment(comment))
                    nonesafe(op)

            with open(f"{repo_path}/done", "a"):
                pass

            scraped_per_lang[lri.language] += 1
            scraped_repos.add(repo.full_name)

            with open("./progress.json", "w") as f:
                f.write(json.dumps([list(scraped_repos), scraped_per_lang, [item.jsonable() for item in lris]]))
except Exception as e:
    print_rlim()
    import yagmail

    yag = yagmail.SMTP(os.getenv("YAGMAIL_USER"), os.getenv("YAGMAIL_PASSWORD"))
    yag.send(os.getenv("YAGMAIL_USER"), "scraper died", f"github scraper died: {str(e)}")

    raise e
