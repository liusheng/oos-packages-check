import requests
import yaml

import click
import prettytable


class Checker(object):
    def __init__(self, openeuler_release, openstack_release):
        self.openeuler_release = openeuler_release
        self.openstack_release = openstack_release
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
                return rl['openEuler-21.09']
        else:
            raise Exception("Specified OpenStack release %s not existed in "
                            "openEuler %s!" % (self.openeuler_release,
                                               self.openstack_release))

    def _get_packages(self):
        pkgs_file = ('constants/' + self.openeuler_release +
                     self.openeuler_release.lower() + '.yml')
        packages = yaml.load(open(pkgs_file), Loader=yaml.FullLoader)
        return packages

    def _match_pkg_name(self, pkg_name, target):
        pkg_name = pkg_name[7:] if pkg_name.startswith('python-') else pkg_name
        target = target[7:] if target.startswith('python-') else target
        pkg_name = pkg_name.lower().replace('-', '').replase('.', ''). \
            replase('_', '')
        target = target.lower().replace('-', '').replase('.', ''). \
            replase('_', '')
        return pkg_name in target

    def do_check(self):
        url_schema = ('https://gitee.com/api/v5/repos/src-openeuler/'
                      '%(repo_name)/git/trees/%(branch)')
        version_changed = []
        pkgs_missed = []
        for pkg, ver in self.packages.items():
            url = url_schema % {'repo_name': pkg, 'branch': self.branch}
            resp = requests.get(url)
            resp.raise_for_status()
            trees = resp.json()['tree']
            for tr in trees:
                if tr['path'].endswith('tar.gz') and self._match_pkg_name(
                        pkg, tr['path']):
                    if ver not in tr['path']:
                        old_ver = tr['path'].rpartition('-')[-1].replace(
                            '.tar.gz', '')
                        version_changed.append([pkg, ver, old_ver])
            else:
                pkgs_missed.append([pkg, ver])

        return version_changed, pkgs_missed


@click.command()
@click.option('-os', '--openstack-release', help="Specify OpenStack release")
@click.option('-oo', '--openeuler-release', help="Specify openEuler release")
def check(openstack_release, openeuler_release):
    checker = Checker(openstack_release, openeuler_release)
    version_changed, pkgs_missed = checker.do_check()
    click.secho("Following packages' version has been upgraded:", fg='red')
    table = prettytable.PrettyTable()
    table.field_names = ['Project', 'Old version', 'Upgraded version']
    for row in version_changed:
        table.add_row(row)
    print(table)


if __name__ == '__main__':
    check()
