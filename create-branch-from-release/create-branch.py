import os
import csv
import requests
import pandas as pd

# Constants
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
BRANCH_NAME = os.environ.get("BRANCH_NAME", "default-branch")
CREATE_BRANCH = True
CREATE_RELEASE = True

# Function to create a branch from a tag
def create_branch(repo, tag):
    # Get the SHA of the tag
    """
    Create a new branch from a tag in a GitHub repository.

    Parameters
    ----------
    repo : str
        The name of the GitHub repository to create the branch in.
    tag : str
        The name of the tag to create the branch from.

    Returns
    -------
    None
    """
    tag_url = f"{GITHUB_API_URL}/repos/{repo}/git/refs/tags/{tag}"
    response = requests.get(tag_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code != 200:
        print(f"Error fetching tag {tag} for repo {repo}: {response.json()}")
        return
    
    tag_sha = response.json()['object']['sha']
    
    # Create a new branch from the tag SHA
    branch_url = f"{GITHUB_API_URL}/repos/{repo}/git/refs"
    branch_data = {
        "ref": f"refs/heads/{BRANCH_NAME}",
        "sha": tag_sha
    }
    
    response = requests.post(branch_url, json=branch_data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 201:
        print(f"Branch '{BRANCH_NAME}' created successfully in repo '{repo}'.")
    else:
        print(f"Error creating branch in repo {repo}: {response.json()}")

# Function to create a release
def create_release(repo, tag, release_name, release_description):
    """
    Create a new release in a GitHub repository.

    Parameters
    ----------
    repo : str
        The name of the GitHub repository to create the release in.
    tag : str
        The name of the tag to create the release from.
    release_name : str
        The name of the release.
    release_description : str
        The description of the release.

    Returns
    -------
    None
    """
    release_url = f"{GITHUB_API_URL}/repos/{repo}/releases"
    release_data = {
        "tag_name": tag,
        "name": release_name,
        "body": release_description,
        "draft": False,
        "prerelease": False
    }
    
    response = requests.post(release_url, json=release_data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 201:
        print(f"Release '{release_name}' created successfully in repo '{repo}'.")
    else:
        print(f"Error creating release in repo {repo}: {response.json()}")

# Main function to process CSV and perform actions
def main(csv_file):
    """
    Main function to process a CSV file and perform actions.

    The CSV file is expected to have columns 'repo_name', 'tag', 'release_name', and 'release_description'.

    For each row, the function will create a branch from the tag in the specified repository and create a release
    with the specified name and description.

    Parameters
    ----------
    csv_file : str
        The path to the CSV file to process.

    Returns
    -------
    None
    """

    df = pd.read_csv(csv_file)
    
    for index, row in df.iterrows():
        repo = row['repo_name']
        tag = row['tag']
        release_name = row['release_name']
        release_description = row['release_description']
        
        if CREATE_BRANCH:
            create_branch(repo, tag)
        
        if CREATE_RELEASE:
            create_release(repo, tag, release_name, release_description)

if __name__ == "__main__":
    csv_file_path = "create-branch.csv"  # Change this to your CSV file path
    main(csv_file_path)
