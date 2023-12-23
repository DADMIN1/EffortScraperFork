import pathlib
from collections import namedtuple
# you can convert a namedtuple to a dict by calling the '._asdict()' member-function # Pycharm hates it though.
# their 'repr' method is also useful; it prints the values passed to the
# object's constructor (showing the parameter names)
# note that 'field_names' can specified with a single comma-seperated string
# https://docs.python.org/3/library/collections.html#collections.namedtuple


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
    # getting trolled so hard here
    # it's a list of tuples
    # DOES NOT UNPACK = [match_subfolders[index] for index in range(len(match_subfolders))]
    # for some reason it needs a tuple if it's not all, and vice versa
    unpacked = [path for index in range(len(match_subfolders)) for path in match_subfolders[index]]  if fext == "ALL" \
        else [path for index in range(len(match_subfolders)) for path in (match_subfolders[index],)]
    results = [file for path in unpacked for file in path.glob(derglob)]
    return results


# TODO: finish this
def CreateTestfiles(): pass
    #for stuff in subfolders


if __name__ == "__main__":
    printdefaultflags()
    result = [
        GlobSearch(opt=SearchFlags.Filetypes(derivepath=True, extension="json")),
        GlobSearch(opt=SearchFlags.Filetypes(derivepath=True, extension="csv")),
        GlobSearch(opt=SearchFlags.Filetypes(derivepath=False)),
    ] #clean_names = [path if path.is_file() else str(path)+ '/' for path in result]
    #clean_names = [path.name if path.is_file() else str(path)+ '/' for path in result]
    for filelist in result:
        for foldername in filter(lambda x: x.is_dir(), filelist):
            print('\n', foldername.absolute())
            for filename in filter(lambda x: x.is_file() and (x.parent == foldername), filelist):
                print(filename.name)
    print('\n')

    TestFileSearch()
