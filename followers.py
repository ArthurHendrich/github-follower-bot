from random import uniform as rand_uniform
import requests
import argparse
import sys
from github import Github
import time


class Config:
    def __init__(self, access_token, userfile, verbose=False, silent=False):
        self.access_token = access_token
        self.target_usernames = []
        self.max_scan_users = 1000
        self.wait_time_follow_min = 30 
        self.wait_time_follow_max = 50
        self.wait_time_list_min = 60
        self.wait_time_list_max = 60
        self.scan_time_min = 60
        self.scan_time_max = 120
        self.verbose = verbose
        self.user_agent = "GitHub Follower Bot"
        self.seed = True
        self.seed_min_free = 0
        self.max_api_fails = 0
        self.lockout_wait_min = 5
        self.lockout_wait_max = 10
        self.seed_max_pages = 5

        with open(userfile, "r") as f:
            self.target_usernames = [line.strip() for line in f]


class GitHubBot:
    def __init__(self, config):
        self.g = Github(config.access_token, user_agent=config.user_agent)
        self.authenticated_user = self.g.get_user()
        self.headers = {
            "Authorization": f"token {config.access_token}",
            "Accept": "application/vnd.github+json",
        }

    def follow_users(self, target_usernames):
        total_followers = 0
        for target_username in target_usernames:
            target_user = self.g.get_user(target_username)
            total_followers += target_user.followers

        if total_followers == 0:
            print("Nenhum seguidor encontrado.")
            sys.exit()

        followers_scanned = 0

        for target_username in target_usernames:
            target_user = self.g.get_user(target_username)
            followers = target_user.get_followers()
            following = [user.login for user in self.authenticated_user.get_following()]

            for follower in followers[: config.max_scan_users]:
                if followers_scanned == total_followers:
                    print("Todos os seguidores já foram varridos. Encerrando.")
                    sys.exit()

                if follower.login not in following:
                    if config.verbose:
                        print(f"Seguindo {follower.login}")

                    # API REST
                    url = f"https://api.github.com/user/following/{follower.login}"
                    response = requests.put(url, headers=self.headers)

                    if response.status_code == 204:
                        if config.verbose >= 2:
                            print(f"Seguido com sucesso {follower.login}")
                    elif response.status_code == 404:
                        if config.verbose >= 2:
                            print(f"Usuário não encontrado {follower.login}")
                    elif response.status_code == 429:
                        if config.verbose >= 1:
                            print(f"Limite de requisições excedido {follower.login}")
                        time.sleep(rand_uniform(config.lockout_wait_min, config.lockout_wait_max))
                    else:
                        if config.verbose >= 1:
                            print(f"Erro ao seguir {follower.login}: {response.status_code}")
                    rand_uniform(config.wait_time_follow_min, config.wait_time_follow_max)
                else:
                    if config.verbose >= 1:
                        print(f"Já seguindo {follower.login}")

                followers_scanned += 1

    def unfollow_users(self):
        following = self.authenticated_user.get_following()

        for user in following:
            if config.verbose >= 1:
                print(f"Deixando de seguir {user.login}")
            self.authenticated_user.unfollow(user)
            rand_uniform(config.wait_time_follow_min, config.wait_time_follow_max)



if __name__ == "__main__":
    custom_usage = f"Usage: python3 {sys.argv[0]} [options] <target>\n\nOptions:\n  -t, --token TOKEN          Access Token (required)\n  -u, --userfile USERFILE      File with list of users to follow (required)\n  -v, --verbose               Verbose mode\n  -s, --silent                Silent mode (only output successful attempts)\n  -m, --mode {'follow','unfollow'} Mode: follow or unfollow (required)\n"

    parser = argparse.ArgumentParser(description="GitHub Follower Bot", usage=custom_usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--token", help="Access Token", required=True)
    parser.add_argument("-u", "--userfile", help="File with list of users to follow", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
    parser.add_argument("-s", "--silent", help="Silent mode (only output successful attempts)", action="store_true")
    parser.add_argument("-m", "--mode", help="Mode: follow or unfollow", choices=["follow", "unfollow"], required=True)

    try:
        args = parser.parse_args()
    except:
        exit(0)

    config = Config(args.token, args.userfile, args.verbose, args.silent)

    bot = GitHubBot(config)


    total_followers = 0
    for target_username in config.target_usernames:
        target_user = bot.g.get_user(target_username)
        total_followers += target_user.followers

    if total_followers == 0:
        print("Nenhum seguidor encontrado.")
        sys.exit()

    followers_scanned = 0

    if args.mode == "follow":
        if config.seed:
            if len(config.target_usernames) == 1:
                bot.follow_users(config.target_usernames)
            else:
                bot.follow_users(config.target_usernames[1:])

        while True:
            try:
                bot.follow_users(config.target_usernames)
                time.sleep(rand_uniform(config.scan_time_min, config.scan_time_max))
            except KeyboardInterrupt:
                break
            except Exception as e:
                if config.verbose >= 1:
                    print(f"Erro: {e}")
                if config.max_api_fails == 0:
                    continue
                time.sleep(rand_uniform(config.lockout_wait_min * 60, config.lockout_wait_max * 60))

    elif args.mode == "unfollow":
        bot.unfollow_users()

