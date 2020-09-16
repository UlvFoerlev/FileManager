import os
import json
import git
import shutil

import tarfile
import rarfile
import zipfile

import logging

log = logging.getLogger(__name__)

class MixinActions:
    def _first_unique_path(self, filepath, new_name=None):
        filename, _, _ = self._split_fullpath(filepath)
        attempts = 0

        if not new_name:
            new_name = filename

        def construct_path(attempts):
            _name , _ext, _remainder = self._split_fullpath(new_name)

            _ext = f".{_ext}" if _ext else ""

            if attempts:
                return f"{_remainder}{_name} ({attempts}){_ext}"
            else:
                return new_name

        new_path = construct_path(None)

        while(os.path.exists(new_path)):
            attempts += 1
            new_path = construct_path(attempts)

        return new_path
        
    def _rename(self, filepath, new_name):
        if self._is_aggragate_name(new_name):
            new_name = self._name_to_path(filepath, new_name)
        
        os.rename(filepath, self._first_unique_path(filepath, new_name))

    def _delete(self, filepath):
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)

    def Delete(self):
        for filepath in self:
            self._delete(filepath)

        log.warning(f"Removed files '{self}'")

    def Rename(self, new_name):
        for filepath in self:
            self._rename(filepath, new_name)

    def Move(self, new_path):
        if self._is_aggragate_name(new_path):
                new_path = self._name_to_path(filepath, new_path)

        for filepath in self:
            shutil.move(filepath, new_path)

    def Unzip(self, to_path=None, delete_original=False):
        for filepath in self:
            was_extracted = False

            new_path = to_path if to_path else self._get_base_path(filepath)

            if self._is_aggragate_name(new_path):
                new_path = self._name_to_path(filepath, new_path)

            if tarfile.is_tarfile(filepath):
                with tarfile.open(filepath) as tar_file:
                    tar_file.extractall(new_path)
                
                was_extracted = True
                
            elif zipfile.is_zipfile(filepath):
                with zipfile.ZipFile(filepath, 'r') as zip_file:
                    zip_file.extractall(new_path)
        
                was_extracted = True

            elif rarfile.is_rarfile(filepath):
                with rarfile.open(filepath) as rar_file:
                    rar_file.extractall(new_path)
        
                was_extracted = True
            
            
            if was_extracted == True:
                if delete_original:
                    self._delete(filepath)
            else:
                log.warning(f"Could not detect archive type of '{filepath}'")


class MixinTargets:
    def _extension(self, fullpath):
        _, ext, _ = self._split_fullpath(fullpath)
        
        return ext

    def _type(self, fullpath):
        _, ext, _ = self._split_fullpath(fullpath)

        for ext_type in self.extensions:
            if ext in self.extensions[ext_type]:
                return ext_type

    def _substring(self, fullpath, substring, case_sensitive):
        name, _, _ = self._split_fullpath(fullpath)

        if case_sensitive and name.find(substring) != -1:
            return True
        
        elif not case_sensitive and name.lower().find(substring.lower()) != -1:
            return True

        return False

    def _prefix(self, fullpath, substring, case_sensitive):
        name, _, _ = self._split_fullpath(fullpath)

        l = len(substring)
        if case_sensitive and name[0:l] == substring:
            return True

        elif not case_sensitive and name[0:l].lower() == substring.lower():
            return True

        return False

    def _postfix(self, fullpath, substring, case_sensitive):
        name, _, _ = self._split_fullpath(fullpath)

        l = len(substring)
        if case_sensitive and name[-l:] == substring:
            return True

        elif not case_sensitive and name[-l:].lower() == substring.lower():
            return True

        return False

    def _isGit(self, fullpath):
        try:
            _ = git.Repo(fullpath).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False

    def Extension(self, other):
        return DirectoryFiles([x for x in self if self._extension(x) == other])

    def ExtenstionType(self, other):
        return DirectoryFiles([x for x in self if self._type(x) == other])
    
    def Substring(self, other, case_sensitive=True):
        return DirectoryFiles([x for x in self if self._substring(x, other, case_sensitive)])

    def Prefix(self, other, case_sensitive=True):
        return DirectoryFiles([x for x in self if self._prefix(x, other, case_sensitive)])

    def Postfix(self, other, case_sensitive=True):
        return DirectoryFiles([x for x in self if self._postfix(x, other, case_sensitive)])

    def IsDirectory(self, other=True):
        return DirectoryFiles([x for x in self if os.path.isdir(x) is other])

    def IsGit(self, other=True):
        # Slow
        return DirectoryFiles([x for x in self if (other is True and os.path.isdir(x) and self._isGit(x)) or (other is False and not self._isGit(x))])

class DirectoryFiles(list, MixinTargets, MixinActions):
    def __init__(self, *arg, **kwargs):

        with open("extensions.json", 'r') as myfile:
            data=myfile.read()

        self.extensions = json.loads(data)
        self.directory_path = None

        super(DirectoryFiles, self).__init__(*arg, **kwargs)

    @classmethod
    def from_directory(cls, path):
        cls = DirectoryFiles([f"{path}{x}" for x in os.listdir(path)])
        cls.directory_path = path
        return cls

    def _is_aggragate_name(self, name):
        return (name[0] == "*")

    def _get_base_path(self, filepath):
        if self.directory_path:
            return self.directory_path
        else:
            return "/".join(filepath.split("/")[:-1]) + "/"

    def _name_to_path(self, filepath, name):
        base_path = self._get_base_path(filepath)
        
        if os.path.isfile(filepath):
            _, ext, _ = self._split_fullpath(filepath)
        
        ext = f".{ext}" if ext else ""

        if self._is_aggragate_name(name):
            name = name[1:]

        if base_path[-1] == "/":
            return base_path + name + ext
        else:
            return f"{base_path}/{name}{ext}"

    def _sanatize_extension(self, ext):
        if not ext:
            return ""
        legal_characters = {"."}

        if ext[0] == ".":
            ext = ext[1:]

        ext = ''.join(e for e in ext if e.isalnum() or e in legal_characters)
        
        return ext.lower()

    def _split_fullpath(self, fullpath):
        path, ext = os.path.splitext(fullpath)
        filename = path.split("/")[-1]

        return filename, self._sanatize_extension(ext), "/".join(fullpath.split("/")[:-1]) + "/"

    
if __name__ == "__main__":
    df = DirectoryFiles.from_directory("/home/ulvfoerlev/Documents/")
    df.ExtenstionType("archive").Rename("*Azathoth")
