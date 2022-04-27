import os
import git
import json
import pathlib
import shutil


class Author:
    name: str
    email: str


with open('config.json') as config_file:
    config = json.load(config_file)

repository_list = config['repository_list']
find_and_replace_list = config['find_and_replace_list']
# file_list = config['file_list']
commit_message = config['commit_message']
base_branch = config['base_branch']
repositories_directory = config['repositories_directory']
repository_author = Author
repository_author.name = config['repository_author_name']
repository_author.email = config['repository_author_email']
ssh_key = config['ssh_key']

for repository in repository_list:
    ticket_id = repository[0]
    service_repo = repository[1]
    print(service_repo, ticket_id)
    path_to_repository = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      repositories_directory + ticket_id)

    #  Delete the previous repo:
    if os.path.isdir(path_to_repository):
        shutil.rmtree(path_to_repository)
    cloned_repository = git.Repo.clone_from(service_repo, path_to_repository, branch=base_branch,
                                            env={"GIT_SSH_COMMAND": 'ssh -i ' + ssh_key})
    new_branch = cloned_repository.create_head(ticket_id)
    new_branch.checkout()
    file_list = []
    for root, dirs, files in os.walk("repositories/{}".format(ticket_id)):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            _, file_extension = os.path.splitext(file)
            if file_extension in [".tpl", ".sh", ".py", ".yaml", ".yml", ".js", ".md", ".java", ".env", ".properties", ".txt", ".j2"]:
                file_list.append(os.path.join(root, file))
    for checked_file in file_list:
        path_to_repository_file = os.path.join(
            "/Users/shabhish/Documents/rainier-github/bulk-find-and-replace-in-git-repositories", checked_file)
        repo_file = pathlib.Path(path_to_repository_file)
        print(repo_file, repo_file.exists())
        if repo_file.exists():
            for texts in find_and_replace_list:
                text_to_find = texts[0]
                text_to_replace = texts[1]
                try:
                    with open(path_to_repository_file, 'r') as f:
                        current_file_data = f.read()

                    if text_to_find in current_file_data:
                        new_file_data = current_file_data.replace(
                            text_to_find, text_to_replace)

                        with open(path_to_repository_file, 'w') as f:
                            f.write(new_file_data)
                except Exception as e:
                    pass
            cloned_repository.index.add(path_to_repository_file)
        else:
            print("Ignoring "+path_to_repository_file+". Not found")
    print("***************************")
    print(cloned_repository.index.commit(
        commit_message.format(ticket_id), author=repository_author))
    origin = cloned_repository.remote(name='origin')
    print(origin.push(new_branch))
    print("Pushed to new repo")
    print("***************************")
