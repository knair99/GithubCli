import json
import requests
import requests_cache

from requests.exceptions import HTTPError
from heapq import heappush, heappop, heapify, heapreplace, heappushpop

SUCCESS = 0
ERROR_NONE = 0
ERROR_INVALID_ARGUMENTS = -1
ERROR_NETWORK_EXCEPTION = -4
ERROR_HTTP_EXCEPTION = -5
ERROR_NOT_FOUND = -6
ERROR_INVALID_PARAMETERS = -7
ERROR_IMPROPERLY_FORMATTED_DATA = -8


class GithubCli:
    """
    The main Github cli class. Manages the core parts of the program, such as URL management, HTTP fetching, caching, and extracting relevant information for the github CLI tool and library.
    Attributes:
        api_token: The API token either passed to our class during initialization from use as a library, or read from the config file
        settings: All the configuration and settings data read from the config.json file
    """

    def __init__(self, api_token=None):
        self.api_token = api_token
        self.settings = {}

        # Read all the settings from config.json
        self.get_config_settings()

        if not self.api_token:
            if 'API_TOKEN' not in self.settings or not self.settings['API_TOKEN']:
                raise ValueError("No API key has been supplied")
            else:
                self.api_token = self.settings['API_TOKEN']

        # Initialize the requests cache, set defaults if time not specified in config.json
        requests_cache.install_cache('network_cache',
                                     backend=self.settings['CACHE']['DEFAULT_BACKEND_DB'],
                                     expire_after=int(
                                         self.settings['CACHE']['DEFAULT_TIMEOUT']))

        # Perform basic authorization by using token
        # Needed to avoid API rate limiting
        self.headers = {'Authorization': 'token ' + self.api_token}

    def get_config_settings(self):
        """
        The config reader function. Reads the config.json file and makes it available in our settings variable.
        """
        with open('config.json') as config_file:
            self.settings = json.load(config_file)

    def get_all_repositories_by_org(self, organization, url=None):
        """
        Makes the HTTP fetch to the url, constructed with organization name.
        Parameters:
            organization: The string representing the organization we want queried
        Returns:
            result_code: Status code indicating successful/failed fetch operation.
            json_data: The results of the fetch would be retrieved either from the URL or from the cache database
        """
        print('Please wait. Fetching data about all repositories for ', organization)

        if not organization:
            return ERROR_INVALID_ARGUMENTS, None

        url = self.settings['BASE_URL'] + \
            organization + '/repos' if not url else url
        has_next_page = True
        json_data = []
        page_number = 1
        # There may be more than one page of results
        while has_next_page:
            try:
                response = requests.get(url, headers=self.headers)
                # If the response was successful, no exception will be raised
                response.raise_for_status()
            except HTTPError as http_error:
                print('HTTP error occurred:', http_error)
                return ERROR_HTTP_EXCEPTION, None
            except Exception as network_error:
                print('Network exception has occurred:', network_error)
                return ERROR_NETWORK_EXCEPTION, None
            else:
                json_data.extend(response.json())
                if 'next' in response.links:
                    page_number += 1
                    url = self.settings['BASE_URL'] + \
                        organization + '/repos' + '?page=' + str(page_number)
                else:
                    has_next_page = False
        # Return data in json format
        print('Done.')
        return SUCCESS, json_data

    def get_pull_requests_count_by_repo(self, organization, repo_name, count, total):
        """
        Makes the HTTP fetch to individual repo url, constructed with org and repo name.
        Parameters:
            organization: The string representing the organization we want queried
            repo_name: The name of the individual repo
        Returns:
            json_data: The results of the fetch would be retrieved either from the URL or from the cache database
        """
        print('Processing individual repo: ', count, '/', total)
        print('Fetching data for repo:', repo_name)
        url = self.settings['REPO_URL'] + organization + \
            '/' + repo_name + '/pulls?state=all'
        total_results = 0
        processing_first_page = True
        done_processing_pages = False

        while not done_processing_pages:
            try:
                response = requests.get(url, headers=self.headers)
                # If the response was successful, no exception will be raised
                response.raise_for_status()
            except HTTPError as http_error:
                print('HTTP error occurred:', http_error)
                return ERROR_HTTP_EXCEPTION, None
            except Exception as network_error:
                print('Network exception has occurred:', network_error)
                return ERROR_NETWORK_EXCEPTION, None
            else:
                if processing_first_page:
                    if 'last' in response.links:
                        # We calculate the number of results as:
                        # (Results per page * Total pages) + last page's results
                        last_url = response.links['last']['url']
                        total_pages = int(last_url.split('=')[-1])
                        total_results = len(
                            response.json()) * (total_pages - 1)
                        url = last_url
                        processing_first_page = False
                        # Now we just need the last url's number of repos
                    else:
                        total_results += len(response.json())
                        done_processing_pages = True
                else:
                    total_results += len(response.json())
                    done_processing_pages = True

        # Return data in json format
        print('Done')
        return total_results

    def get_top_repos_by_count(self, organization, number_of_repos, count_attribute):
        """
        Get the top N repositories of an organization by number of count_attribute.
        Parameters:
            organization: The string representing the organization we want queried
            N: Integer representing the number of counts of the top repos we want
        Returns:
            results: Array of repo details (name/id/count), indicating the top repositories by number of stars
        """
        # We will store the results of the top N, in a min heap as we iterate through repos
        top_N_repos = []
        results = []

        # Do some basic edge checks
        if number_of_repos < 0:
            print('Enter a valid number of repositories')
            return None
        if not organization:
            print('No organization name specified')
            return None
        if count_attribute not in ['stargazers_count', 'forks_count', 'contribution_percentage', 'pull_requests']:
            print('Enter valid counting attribute for repo filter')
            return None

        # Make HTTP call, or get cached results
        error_code, json_data = self.get_all_repositories_by_org(organization)
        if error_code != SUCCESS:
            print('Unable to fetch data via HTTP')
            return None

        # If the organization doesn't have data for repos
        if not json_data:
            print('No data available for this particular organization')
            return None

        # Go through all repos, and find the top ranked repos by count of whichever attribute
        for count, repo in enumerate(json_data):
            attribute_count, repo_name, repo_id = 0, None, 0
            try:
                repo_name = repo['name']
                repo_id = repo['id']
                # Set the attribute count correctly
                # If just star or forks count, read it from the json data
                if count_attribute in ['stargazers_count', 'forks_count']:
                    attribute_count = int(repo[count_attribute])
                # If pull requests, pull info from all individual repos
                elif count_attribute == 'pull_requests':
                    attribute_count = self.get_pull_requests_count_by_repo(
                        organization, repo_name, count, len(json_data))
                # If contribution percent, do both pull and fork counts
                elif count_attribute == 'contribution_percentage':
                    pull_requests_count = self.get_pull_requests_count_by_repo(
                        organization, repo_name, count, len(json_data))
                    forks_count = int(repo['forks_count'])
                    attribute_count = pull_requests_count / forks_count
                    attribute_count = round(attribute_count, 2)
            except Exception as e:
                print('Improper data formatted from the repo:', repo_name)
                print('Exception:', e)
                continue
            if count < number_of_repos:
                heappush(top_N_repos, (attribute_count, repo_name, repo_id))
            else:
                if attribute_count > top_N_repos[0][0]:
                    heappushpop(
                        top_N_repos, (attribute_count, repo_name, repo_id))

        # Get the results, and return
        while top_N_repos:
            result = heappop(top_N_repos)
            results.append(result)

        # Return results in descending order
        return results[::-1]

    def get_top_repos_by_stars(self, organization, number_of_repos=0):
        """
        Get the top N repositories of an organization by number of stars.
        """
        return self.get_top_repos_by_count(
            organization, number_of_repos, 'stargazers_count')

    def get_top_repos_by_forks(self, organization, number_of_repos=0):
        """
        Get the top N repositories of an organization by number of forks.
        """
        return self.get_top_repos_by_count(
            organization, number_of_repos, 'forks_count')

    def get_top_repos_by_pull_requests(self, organization, number_of_repos=0):
        """
        Get the top N repositories of an organization by number of pull requests (PR).
        """
        return self.get_top_repos_by_count(organization, number_of_repos, 'pull_requests')

    def get_top_repos_by_contribution_percentage(self, organization, number_of_repos=0):
        """
        Get the top N repositories of an organization by number of contribution percent.
        """
        return self.get_top_repos_by_count(organization, number_of_repos, 'contribution_percentage')
