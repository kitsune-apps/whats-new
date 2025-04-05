#!/usr/bin/env python3

import argparse
import os
import subprocess
import re
from packaging import version
from anthropic import Anthropic
import sys


def run_git_command(repo_path, args):
    """
    Execute a git command in the specified repository path.

    Args:
        repo_path (str): Path to the git repository
        args (list): List of git command arguments

    Returns:
        str: Output of the git command

    Raises:
        Exception: If git command fails
    """
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"Git error: {result.stderr}")
    return result.stdout.strip()


def get_all_semver_tags(repo_path):
    """
    Get all semantic version tags from a git repository.

    Finds all tags matching semantic versioning format (e.g. 1.2.3 or v1.2.3)
    and returns them sorted by version number.

    Args:
        repo_path (str): Path to the git repository

    Returns:
        list: Sorted list of semantic version tags without 'v' prefix
    """
    raw_tags = run_git_command(repo_path, ["tag"]).splitlines()
    semver_tags = []
    for tag in raw_tags:
        # Match tags that are semantic versions with optional v prefix
        match = re.match(r"^v?(\d+\.\d+\.\d+)$", tag)
        if match:
            semver_tags.append(match.group(1))
    semver_tags.sort(key=version.parse)
    return semver_tags


def find_previous_version(all_versions, current_version):
    """
    Find the version that precedes the current version in the version list.

    Args:
        all_versions (list): Sorted list of all versions
        current_version (str): The version to find the predecessor for

    Returns:
        str: Previous version or None if current_version is the first version
    """
    current_idx = all_versions.index(current_version)
    if current_idx > 0:
        return all_versions[current_idx - 1]
    return None


def get_commits_between_versions(repo_path, from_version, to_version):
    """
    Get commit messages between two versions.

    Args:
        repo_path (str): Path to the git repository
        from_version (str): Starting version
        to_version (str): Ending version

    Returns:
        list: List of commit messages between the versions
    """
    log = run_git_command(
        repo_path, ["log", f"{from_version}..{to_version}", "--pretty=format:%s"]
    )
    commits = log.splitlines()
    return commits


def format_whats_new_with_claude(commits, current_version):
    """
    Generate a formatted "What's New" summary using Claude AI.

    Uses Anthropic's Claude AI to create a well-organized, user-friendly
    summary of changes from commit messages. Falls back to basic formatting
    if the AI service fails.

    Args:
        commits (list): List of commit messages
        current_version (str): Current version number

    Returns:
        str: Formatted "What's New" text
    """
    if not commits:
        return "No changes found."

    try:
        # Initialize Anthropic client
        anthropic = Anthropic()

        # Format commit list with bullet points
        commit_list = "\n".join(f"• {msg}" for msg in commits)

        # Construct prompt for Claude
        prompt = f"""Here are the commit messages for version {current_version}:

{commit_list}

Create a clear, well-organized "What's New" summary in plain text format (no markdown). Group related changes together and make it user-friendly. Focus on important changes and improvements. Remove technical jargon and internal references. Use bullet points with • character. Keep the tone professional but approachable."""

        # Get AI-generated summary
        message = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            system="You are a technical writer creating clear and concise release notes in plain text format.",
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    except Exception as e:
        # Fall back to basic formatting if AI fails
        return "What's New:\n\n" + "\n".join(f"• {msg}" for msg in commits)


def main():
    """
    Main function to generate What's New from git history.

    Parses command line arguments, validates versions, and generates
    a formatted summary of changes between versions.
    """
    parser = argparse.ArgumentParser(
        description="Generate 'What's New' from Git history using Claude AI."
    )
    parser.add_argument("repo_path", help="Path to the Git repository")
    parser.add_argument("version", help="Current release version (e.g., 1.2.3)")
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    current_version = args.version

    # Get and validate versions
    all_versions = get_all_semver_tags(repo_path)
    if current_version not in all_versions:
        raise ValueError(f"Version {current_version} not found in tags.")

    prev_version = find_previous_version(all_versions, current_version)
    if not prev_version:
        raise ValueError("No previous version found.")

    # Generate and print summary
    commits = get_commits_between_versions(repo_path, prev_version, current_version)
    summary = format_whats_new_with_claude(commits, current_version)
    print(summary)


if __name__ == "__main__":
    main()
