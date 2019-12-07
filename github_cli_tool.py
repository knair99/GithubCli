import sys
from github_cli import GithubCli

ERROR_NONE = 0
ERROR_INVALID_ARGUMENTS = -1
ERROR_INSUFFICIENT_ARGUMENTS = -2


def print_usage():
    """
    Print usage for the program
    """
    print('Usage:')
    print('  github_cli -org <organization_name> -mode <number_of_repos>')
    print('Modes:')
    print('  -h, --help,      \t\t Show this help')
    print('  -s, --stars,     \t\t Show top repositories by number of stars')
    print('  -f, --forks,     \t\t Show top repositories by number of forks')
    print('  -pr, --pull_requests,\t\t Show top repositories by number of pull requests (PR)')
    print('  -cp, --contribution,\t\t Show top repositories by contribution percentage (CP)')
    print('Examples:')
    print('  github_cli -org netflix -s 10 \t To get the top 10 repos by number of stars')
    print('  github_cli - org netflix - f 5 \t To get the top 5 repos by number of forks')
    print('  github_cli -org netflix -pr 5 \t To get the top 5 repos by number of pull requests')
    print('  github_cli -org netflix -cp 5 \t To get the top 5 repos by contribution percentage')


def printline(results):
    if not results:
        return

    print('--------------')
    print('RESULTS:')
    for result in results:
        result = 'Repo: ' + str(result[1]) + ' ID: ' + \
            str(result[2]) + ' : ' + \
            ' Count: ' + str(result[0])
        print(result)
    print('--------------')


def raise_error(ERROR_CODE):
    print_usage()
    exit(ERROR_CODE)


def main():
    """
    This is the entry point to the command line tool, when installed correctly on the system.Alternatively, you may run the tool by just doing `python github_cli_tool <command>`. Refer README.md for more details
    """
    gcli = GithubCli()
    args = sys.argv[1:]
    if not args or args[0] in ['-h', '--h', 'h', '-help', '--help', 'help']:
        raise_error(ERROR_NONE)

    # Check to see there are a minimum number of arguments
    if len(args) < 4:
        raise_error(ERROR_INSUFFICIENT_ARGUMENTS)

    # We want to insist that the organization is specified
    if '-org' not in args:
        raise_error(ERROR_INVALID_ARGUMENTS)

    # Extract organization, type of operation and number of repos from command line
    organization, option, number_of_repos = None, None, 0
    try:
        _, organization, option, number_of_repos = args
        try:
            number_of_repos = int(number_of_repos)
        except ValueError:
            raise_error(ERROR_INVALID_ARGUMENTS)
    except:
        raise_error(ERROR_INSUFFICIENT_ARGUMENTS)

    # Determine the kind of ranking desired, and run approp operation
    if option not in ['-s', '-f', '-pr', '-cp']:
        raise_error(ERROR_INVALID_ARGUMENTS)
    else:
        if option == '-s':
            printline(gcli.get_top_repos_by_stars(
                organization, number_of_repos))
        elif option == '-f':
            printline(gcli.get_top_repos_by_forks(
                organization, number_of_repos))
        elif option == '-pr':
            printline(gcli.get_top_repos_by_pull_requests(
                organization, number_of_repos))
        elif option == '-cp':
            printline(gcli.get_top_repos_by_contribution_percentage(
                organization, number_of_repos))


if __name__ == '__main__':
    main()
