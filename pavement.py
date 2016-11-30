# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#

import os
import fnmatch
import zipfile

from paver.easy import *



options(
    plugin = Bunch(
        name = 'mapstory',
        ext_libs = path('mapstory/ext-libs'),
        ext_src = path('mapstory/ext-src'),
        source_dir = path('mapstory'),
        package_dir = path('.'),
        tests = ['test', 'tests'],
        excludes = [
            'ext-src',
            '.git',
            '*.pyc',
        ],
        skip_exclude = [],
    ),

    sphinx = Bunch(
        docroot = path('docs'),
        sourcedir = path('docs/source'),
        builddir = path('docs/build')
    )
)



@task
@cmdopts([
    ('clean', 'c', 'clean out dependencies first'),
])
def setup(options):
    '''install dependencies'''
    clean = getattr(options, 'clean', False)
    ext_libs = options.plugin.ext_libs
    ext_src = options.plugin.ext_src
    if clean:
        ext_libs.rmtree()
    ext_libs.makedirs()
    runtime, test = read_requirements()

    try:
        import pip
    except:
        error('FATAL: Unable to import pip, please install it first!')
        sys.exit(1)

    os.environ['PYTHONPATH']=ext_libs.abspath()
    for req in runtime + test:
        if "#egg" in req:
            urlspec, req = req.split('#egg=')
            localpath = ext_src / req
            if os.path.exists(localpath):
                cwd = os.getcwd()
                os.chdir(localpath)
                sh("git pull")
                os.chdir(cwd)
            else:
                sh('git clone  %s %s' % (urlspec, localpath))
            req = localpath

        pip.main(['install',
                  '-t',
                  ext_libs.abspath(),
                  req])


def read_requirements():
    '''return a list of runtime and list of test requirements'''
    lines = open('requirements.txt').readlines()
    lines = [ l for l in [ l.strip() for l in lines] if l ]
    divider = '# test requirements'
    try:
        idx = lines.index(divider)
    except ValueError:
        raise BuildFailure('expected to find "%s" in requirements.txt' % divider)
    not_comments = lambda s,e: [ l for l in lines[s:e] if l[0] != '#']
    return not_comments(0, idx), not_comments(idx+1, None)


@task
def install(options):
    '''install plugin to qgis'''
    plugin_name = options.plugin.name
    src = path(__file__).dirname() / plugin_name
    dst = path('~').expanduser() / '.qgis2' / 'python' / 'plugins' / plugin_name
    src = src.abspath()
    dst = dst.abspath()
    if not hasattr(os, 'symlink'):
        dst.rmtree()
        src.copytree(dst)
    elif not dst.exists():
        src.symlink(dst)


@task
@cmdopts([
    ('tests', 't', 'Package tests with plugin'),
])
def package(options):
    """Create plugin package
    """
    builddocs(options)
    package_file = options.plugin.package_dir / ('%s.zip' % options.plugin.name)
    with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        if not hasattr(options.package, 'tests'):
            options.plugin.excludes.extend(options.plugin.tests)
        _make_zip(zf, options)
    return package_file


@task
def builddocs(options):
    sh("git submodule init")
    sh("git submodule update")
    cwd = os.getcwd()
    os.chdir(options.sphinx.docroot)
    sh("make html")
    os.chdir(cwd)


def _make_zip(zipFile, options):
    excludes = set(options.plugin.excludes)
    skips = options.plugin.skip_exclude

    src_dir = options.plugin.source_dir
    exclude = lambda p: any([path(p).fnmatch(e) for e in excludes])
    def filter_excludes(root, items):
        if not items:
            return []
        # to prevent descending into dirs, modify the list in place
        for item in list(items):  # copy list or iteration values change
            itempath = path(os.path.relpath(root)) / item
            if exclude(item) and item not in skips:
                debug('Excluding %s' % itempath)
                items.remove(item)
        return items

    for root, dirs, files in os.walk(src_dir):
        for f in filter_excludes(root, files):
            relpath = os.path.relpath(root)
            zipFile.write(path(root) / f, path(relpath) / f)
        filter_excludes(root, dirs)

    for root, dirs, files in os.walk(options.sphinx.builddir):
        for f in files:
            relpath = os.path.join(options.plugin.name, "docs", os.path.relpath(root, options.sphinx.builddir))
            zipFile.write(path(root) / f, path(relpath) / f)
