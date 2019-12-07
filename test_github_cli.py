from github_cli import GithubCli

import pytest

SUCCESS = 0
ERROR_NONE = 0
ERROR_INVALID_ARGUMENTS = -1
ERROR_INSUFFICIENT_ARGUMENTS = -2
ERROR_NETWORK_EXCEPTION = -4
ERROR_HTTP_EXCEPTION = -5
ERROR_NOT_FOUND = -6
ERROR_INVALID_PARAMETERS = -7
ERROR_IMPROPERLY_FORMATTED_DATA = -8

# def test_empty_settings():
#     """
#     Test no config file
#     """
#     with pytest.raises(FileNotFoundError) as e:
#         gcli = GithubCli()
#     assert 'config.json' in str(e.value)


# def test_empty_api_key():
#     """
#     Test no API_KEY supplied in config.json
#     """
#     with pytest.raises(ValueError) as e:
#         gcli = GithubCli()
#     assert 'No API key' in str(e.value)


def test_invalid_organization_name():
    """
    Test invalid org name
    """
    gcli = GithubCli()
    assert gcli.get_all_repositories_by_org(
        'nwe3tflix') == (ERROR_HTTP_EXCEPTION, None)


def test_null_organization_name():
    """
    Test no organization name supplied
    """
    gcli = GithubCli()
    assert gcli.get_all_repositories_by_org(
        '') == (ERROR_INVALID_ARGUMENTS, None)


def test_regular_organization_name():
    """
    Test regular organization name supplied
    """
    gcli = GithubCli()
    assert len(gcli.get_all_repositories_by_org('netflix')[1]) == 171


def test_invalid_URL():
    """
    Test invalid URL
    """
    gcli = GithubCli()
    assert gcli.get_all_repositories_by_org(
        'netflix', url='httpp://google.com') == (ERROR_NETWORK_EXCEPTION, None)


def test_empty_BASE_URL():
    """
    Test empty BASE URL
    """
    gcli = GithubCli()
    assert gcli.get_all_repositories_by_org(
        'netflix', url=' ') == (ERROR_NETWORK_EXCEPTION, None)


def test_top_repos_with_invalid_org():
    """
    Test top repost with invalid organization name in URL
    """
    gcli = GithubCli()
    assert gcli.get_top_repos_by_count(
        'neffrfrtflix', number_of_repos=10, count_attribute='forks_count') == None


def test_top_repos_with_invalid_count():
    """
    Test invalid count in top repos
    """
    gcli = GithubCli()
    assert gcli.get_top_repos_by_count(
        'netflix', number_of_repos=-1, count_attribute='forks_count') == None


def test_top_repos_with_invalid_count_attribute():
    """
    Test invalid count attribute in top repos
    """
    gcli = GithubCli()
    assert gcli.get_top_repos_by_count(
        'netflix', number_of_repos=1, count_attribute='commit_count') == None


def test_top_repos_with_valid_attributes():
    """
    Test valid attributes in top repos
    """
    gcli = GithubCli()
    assert len(gcli.get_top_repos_by_count(
        'netflix', number_of_repos=1, count_attribute='stargazers_count')) == 1


def test_top_repos_by_stars():
    """
    Test invalid count attribute in top repos
    """
    gcli = GithubCli()
    results = gcli.get_top_repos_by_count(
        'netflix', number_of_repos=2, count_attribute='stargazers_count')
    assert len(results) == 2
    assert results[0][0] >= results[1][0]


def test_top_repos_by_forks():
    """
    Test valid forks count attribute in top repos
    """
    gcli = GithubCli()
    results = gcli.get_top_repos_by_count(
        'netflix', number_of_repos=2, count_attribute='forks_count')
    assert len(results) == 2
    assert results[0][0] >= results[1][0]


def test_top_repos_by_pull_requests():
    """
    Test valid pull_requests count attribute in top repos
    """
    gcli = GithubCli()
    results = gcli.get_top_repos_by_count(
        'netflix', number_of_repos=2, count_attribute='pull_requests')
    assert len(results) == 2
    assert results[0][0] >= results[1][0]


def test_top_repos_by_contribution_percentage():
    """
    Test contribution_percentage count attribute in top repos
    """
    gcli = GithubCli()
    results = gcli.get_top_repos_by_count(
        'netflix', number_of_repos=2, count_attribute='contribution_percentage')
    assert len(results) == 2
    assert results[0][0] >= results[1][0]


pytest.main()
