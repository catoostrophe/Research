from deltaNFG.Util.git_util import Git_Util


def get_commits(subject, temp_loc):
    """
    Get list of commits sorted by date
    :param subject: repository name
    :param temp_loc: location of temp folder
    :return: list of commit SHAs sorted by date
    """

    git_handler = Git_Util(temp_dir=temp_loc)

    with git_handler as gh:
        temp = gh.move_git_repo_to_tmp(subject)
        candidates = gh.get_all_commit_hashes_authors_dates_messages(temp)

    sorted_commits_by_date = sorted(candidates, key=lambda i: i[2])
    return [commit[0] for commit in sorted_commits_by_date]
