import requests
import yaml

import click
import prettytable
import urllib.parse


class Checker(object):
    def __init__(self, openeuler_release, openstack_release, gitee_pat):
        self.openeuler_release = openeuler_release
        self.openstack_release = openstack_release
        self.gitee_pat = gitee_pat
        self.branch = self._get_pkg_branch()
        self.packages = self._get_packages()

    def _get_pkg_branch(self):
        releases_mapping = yaml.load(
            open('constants/releases-mapping.yml'), Loader=yaml.FullLoader)
        if self.openeuler_release not in releases_mapping:
            raise Exception("Specified openEuler %s not existed!" %
                            self.openeuler_release)
        for rl in releases_mapping[self.openeuler_release]:
            if rl['OpenStack-release'] == self.openstack_release:
                return rl['branch']
        else:
            raise Exception("Specified OpenStack release %s not existed in "
                            "openEuler %s!" % (self.openeuler_release,
                                               self.openstack_release))

    def _get_packages(self):
        pkgs_file = ('constants/' + self.openeuler_release + "-" +
                     self.openstack_release.lower() + '.yml')
        packages = yaml.load(open(pkgs_file), Loader=yaml.FullLoader)
        return packages

    def _match_pkg_name(self, pkg_name, target):
        pkg_name = pkg_name[7:] if pkg_name.startswith('python-') else pkg_name
        target = target[7:] if target.startswith('python-') else target
        pkg_name = pkg_name.lower().replace('-', '').replace('.', ''). \
            replace('_', '')
        target = target.lower().replace('-', '').replace('.', ''). \
            replace('_', '')
        return pkg_name in target

    def do_check(self):
        url_schema = ('https://gitee.com/api/v5/repos/src-openeuler/'
                      '%(repo_name)s/git/trees/%(branch)s'
                      '?access_token=%(gitee_pat)s')
        version_changed = []
        pkgs_missed = []
        for pkg, ver in self.packages.items():
            print("Checking package %s ..." % pkg)
            url = url_schema % {'repo_name': pkg, 'branch': self.branch,
                                'gitee_pat': self.gitee_pat}
            resp = requests.get(url)
            resp.raise_for_status()
            trees = resp.json()['tree']
            for tr in trees:
                if tr['path'].endswith('tar.gz') and self._match_pkg_name(
                        pkg, tr['path']):
                    if str(ver) not in tr['path']:
                        old_ver = tr['path'].rpartition('-')[-1].replace(
                            '.tar.gz', '')
                        version_changed.append([pkg, ver, old_ver])
            else:
                pkgs_missed.append([pkg, ver])

        return version_changed, pkgs_missed


@click.command()
@click.option('-os', '--openstack-release', help="Specify OpenStack release")
@click.option('-oo', '--openeuler-release', help="Specify openEuler release")
@click.option('-t', '--gitee-pat', help="Gitee personal access token")
def check(openstack_release, openeuler_release, gitee_pat):
    checker = Checker(openeuler_release, openstack_release, gitee_pat)
    version_changed, pkgs_missed = checker.do_check()
    click.secho("Following packages' version has been upgraded:", fg='red')
    table = prettytable.PrettyTable()
    table.field_names = ['Project', 'Old version', 'Upgraded version']
    for row in version_changed:
        table.add_row(row)
    print("::set-output name=unmatched_projects_row::%s" % version_changed)
    print("::set-output name=unmatched_projects_html::%s" % urllib.parse.quote(table.get_html_string()))
    print("::set-output name=unmatched_projects_csv::%s" % urllib.parse.quote(table.get_csv_string()))
    print("::set-output name=unmatched_projects_json::%s" % urllib.parse.quote(table.get_json_string()))
    print("::set-output name=unmatched_projects_string::%s" % urllib.parse.quote(table.get_string()))

    print(table)


if __name__ == '__main__':
    check()
