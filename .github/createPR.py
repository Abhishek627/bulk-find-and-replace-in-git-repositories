from github import Github, GithubException, InputGitTreeElement
import json
from os import environ as env

result_list = []
GITHUB_BASE_URL = "https://github.com/"


def delete_branch(githubObj, repo, branch="new_branch", ):
    github_repo = githubObj.get_repo(repo)
    print("Branch to be deleted {} for repo {}:".format(branch, repo))
    try:
        target_object = github_repo.get_branch(branch)
    except:
        print("Branch {} is not present/ already deleted, skip".format(branch))
        return
    target_head = github_repo.get_git_ref("heads/" + branch)
    print("Remove protection for old branch ", branch)
    target_head.delete()
    print("Branch {} deleted for {}".format(branch, repo))


def active_pr_present(github_repo, source_branch="new_branch", target_branch="main"):
    # Source branch is one from which we're creating PR.
    # Target branch is one we are raising PR on.
    print("Check if active PR is present for", source_branch)
    list_pr = github_repo.get_pulls(state='open', base=target_branch)
    for pr in list_pr:
        if pr.head.ref == source_branch:
            print("Active PR already present ")
            return pr
    return None


def create_pr(github_repo, source_branch="new_branch", target_branch="main"):
    # Source branch is one from which we're creating PR.
    # Target branch is one we are raising PR on.
    pr_obj = None
    compare_branch = github_repo.compare(source_branch, target_branch)
    if len(compare_branch.files) > 0:
        print("Creating temp PR from {} branch - {}".format(source_branch, target_branch))
        pr_obj = github_repo.create_pull(title="From {} to {} update ".format(
            source_branch, target_branch), body="main to branch update", head=source_branch, base=target_branch)
    else:
        print("No Change in file contents for {}".format(github_repo))
    return pr_obj


def iterate_repo(githubObj, repo_name, target_branch, source_branch):
    github_repo = githubObj.get_repo(repo_name)
    print("=============================")
    pr_obj = active_pr_present(github_repo, target_branch, source_branch)
    if pr_obj is None:
        try:
            print("Creating PR for ", target_branch, source_branch)
            pr_obj = create_pr(github_repo, target_branch, source_branch)
            print(pr_obj.html_url)
            result_list.append(pr_obj.html_url)
        except Exception as e:
            print("Couldn't create PR for {}".format(repo_name))
    else:
        print("PR already present for {}: {}".format(repo_name, pr_obj.html_url))
        result_list.append(pr_obj.html_url)


def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    githubObj = Github(base_url="https://%s/api/v3" % (GITHUB_BASE_URL),
                       login_or_token=env.get('GITHUB_USERNAME', None), password=env.get('GITHUB_PASSWORD', None),
                       timeout=30, retry=2)

    repository_list = config['repository_list']
    for repo in repository_list:
        repo_name = repo[1].replace(
            "git@", "https//").replace(".git", "")

        iterate_repo(githubObj, repo_name, repo[0])
        # delete_branch(githubObj, repo_name, repo[0])


if __name__ == '__main__':
    env['GITHUB_USERNAME'] = 'git-username'
    env['GITHUB_PASSWORD'] = 'git-password'
    main()
    print("\n *************************************** \n")
    print("\n *************************************** \n")
    for pr in result_list:
        print(pr)
    print("\n *************************************** \n")
    print("\n *************************************** \n")
