import pathlib
from collections import namedtuple
# you can convert a namedtuple to a dict by calling the '._asdict()' member-function # Pycharm hates it though.
# their 'repr' method is also useful; it prints the values passed to the
# object's constructor (showing the parameter names)
# note that 'field_names' can specified with a single comma-seperated string
# https://docs.python.org/3/library/collections.html#collections.namedtuple

import more_itertools as itertool

class SearchFlags:
    Excludes = namedtuple(
        typename='ExcludeFlags',
        field_names=['files', 'folders', 'hidden'],
        defaults=[False, False, True],
        rename=True,  # automatically rename invalid field_names with positionals (_1, _2, etc)
    )
    Filetypes = namedtuple(
        typename='FiletypeFlags',
        # derivepath; searches only the subfolder matching the file-extension
        field_names=['path', 'recursive', 'derivepath', 'extension'],
        defaults=[pathlib.Path.cwd(), True, True, 'csv'],  # no dot on the extension
        rename=True,
    )
    def __init__(self, excludes=None, filetypes=None):
        if excludes: self.Excludes = self.Excludes(*excludes)
        if filetypes:
            self.Filetypes = self.Filetypes(*filetypes)
            if str(self.Filetypes.extension).startswith('.'):
                self.Filetypes._replace(extension=self.Filetypes.extension[1:])

    def __repr__(self):
        return str('\n\t'.join(('SearchFlags:', repr(self.Excludes), repr(self.Filetypes))))

#toplevel_dirs = ("CSV", "JSON")
subfolders = {
    "CSV": ["source", "saved"],
    "JSON": [],
    "TESTS": [],
    #"ALL": ["*"],  # This should work, I think
}
toplevel_dirs = subfolders.keys()

DefaultExcludes = SearchFlags.Excludes(files=False, folders=True, hidden=True)
DefaultFiletypes = SearchFlags.Filetypes(pathlib.Path.cwd(), True, True, 'csv')
DefaultSearchFlags = SearchFlags(DefaultExcludes, DefaultFiletypes)

def printdefaultflags():
    print(DefaultSearchFlags)
    print(DefaultSearchFlags.Excludes)
    print(DefaultSearchFlags.Filetypes)


def SearchFiles(sflags=SearchFlags.Excludes(False, False, True), path=pathlib.Path.cwd()):
    workinglist = path.iterdir()
    filterdict = {
        'files'  : lambda fpath: not fpath.is_file(),
        'folders': lambda fpath: not fpath.is_dir(),
        'hidden' : lambda fpath: not fpath.stem.startswith('.'),
    }
    for field, filterdef in filterdict.items():
        lfilter = lambda infunct: lambda wrklist: filter(infunct, wrklist)  # lmao
        workinglist = lfilter(filterdef)(workinglist) if getattr(sflags.Excludes, field) else workinglist
    return list(workinglist)


# epic one-liners
def TestFileSearch():
    # TODO: add a testfolder and check that it filters things correctly
    #testpaths = []
    testinputs = [
        (bx, by, bz)
        for bx in (False, True)
        for by in (False, True)
        for bz in (False, True)
    ]
    results = [
        [ fp.stem for fp in SearchFiles(SearchFlags(excludes=excludeflags)) ]
        for excludeflags in testinputs
    ]
    print(results)
    return results


def CheckRequiredFolders(topdirs=toplevel_dirs, cwDir=pathlib.Path.cwd()):
    for toplevel, nested in [(pathlib.Path(cwDir/tdir), subfolders[tdir]) for tdir in topdirs]:
        if not toplevel.exists(): toplevel.mkdir()
        for subpath in [pathlib.Path(toplevel/name) for name in nested]:
            if not subpath.exists(): subpath.mkdir()
            # handle more deeply-nested paths somehow

# alternative collapse function if you don't have itertools
def altcollapse(*args):
    return [result for mid in args for
            result in (altcollapse(*mid)
                       if isinstance(mid, (tuple, list)) else (mid,))]


# chooses a folder to search
# TODO: make the path-searching logic not ridiculous
def GlobSearch(glob="*", path="", opt=DefaultFiletypes):
    fallback = path if len(path) else "ALL" if not opt.derivepath else opt.path
    fext = str(opt.extension).upper() if opt.derivepath else fallback
    subdirs = subfolders[fext] if fext in toplevel_dirs else toplevel_dirs
    # TODO: on non-match, manually search 'path' if it's given
    match_subfolders = [
        (pathlib.Path(toplevel),
        *(pathlib.Path(f"{toplevel}/{child}") for child in children))
        for toplevel, children in subfolders.items()
    ] if fext == "ALL" else [pathlib.Path(fext), *(pathlib.Path(f"{fext}/{child}") for child in subdirs)]
    derglob = f'*.{fext.lower()}' if fext != "ALL" else "*"
    # return altcollapse(match_subfolders)
    return [file for path in itertool.collapse(match_subfolders) for file in path.glob(derglob)]


# TODO: finish this
def CreateTestfiles(): pass
    #for stuff in subfolders

import pprint

if __name__ == "__main__":
    printdefaultflags()
    globresults = list(itertool.collapse([
        GlobSearch(opt=SearchFlags.Filetypes(derivepath=True, extension="json")),
        GlobSearch(opt=SearchFlags.Filetypes(derivepath=True, extension="csv")),
        GlobSearch(opt=SearchFlags.Filetypes(derivepath=False)),
    ]))
    # keys and values are stored as pathlib objects
    parents = dict.fromkeys([pathlib.Path(name) for name in toplevel_dirs if pathlib.Path(name).exists()])
    for key, value in parents.items():
        parents[key] = [] # python is retarded and gives every item a reference to a single list,
        # if you construct the dict with a list as a default value. so we have to do this manually.

    for folder in filter(lambda x: x.is_dir(), globresults):
        parents[folder.parent].append(folder)
        parents[folder] = []
    for file in filter(lambda x: x.is_file(), globresults):
        parents[file.parent].append(file)

    for folder, filelist in parents.items():
        print('\n','/',folder,'/')
        for path in filelist:
            print('  ', path.name)


    print('\n')
    pprint.pprint(parents)
    print('\n')

    print(altcollapse(globresults))
    print('\n')
    print(*itertool.collapse(globresults))
    print('\n')

    #print(result)
    print('\n')
    TestFileSearch()
