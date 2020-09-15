import shutil
import os
import git
import json

MAX_DEPTH = 3
IGNORE_GIT_REPOSITORIES = True

#rules = [{"target" : "type", "arg" : "image", "action" : {"func" : "action_print"}}]
# rules = [{"target" : "in_name", "arg" : "zombie", "action" : {"func" : "action_print"}}]
# rules = [{"target" : "ext", "arg" : "jpg", "action" : {"func" : "action_print"}}]
rules = [{"target" : "postfix", "arg" : "Face", "action" : {"func" : "action_print"}}]

class FileManager(object):

    def __init__(self, rules):
        self.rules = rules

        with open("extensions.json", 'r') as myfile:
            data=myfile.read()

        self.extensions = json.loads(data)
    
    def moveFile(self, from_path, to_path):
        shutil.move(from_path, to_path)

    def file_is_correctly_located(self, path):
        pass

    def is_git_repository(self, full_path):
        try:
            _ = git.Repo(full_path).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False

    def _sanatize_file_extension(self, ext):
        if not ext:
            return ""
        legal_characters = {"."}

        if ext[0] == ".":
            ext = ext[1:]

        ext = ''.join(e for e in ext if e.isalnum() or e in legal_characters)
        
        return ext.lower()

    def iterate_directory(self, path):
        for file in os.listdir(path):
            filename, extention = os.path.splitext(file)
            fullpath = f'{path}{file}' if path[:-1] == "/" else f'{path}/{file}'
            
            yield filename, self._sanatize_file_extension(extention), fullpath
    
    def run(self, path):
        iterator = self.iterate_directory(path)

        for name, ext, path in iterator:
            self.action(name, ext, path)

    def action(self, name, ext, path):
        for rule in self.rules:
            target = rule["target"]
            
            # type
            if target == "type":
                if rule["arg"] in self.extensions:
                    if ext in self.extensions[rule["arg"]]:
                        action = getattr(self, rule["action"]["func"])
                        action(name, ext, path)

                        continue

            # extension
            if target == "ext":
                if rule["arg"] == ext:
                    action = getattr(self, rule["action"]["func"])
                    action(name, ext, path)

                    continue

            # prefix of name
            if target == "prefix":
                l = len(rule["arg"])
                if name[0:l] == rule["arg"]:
                    action = getattr(self, rule["action"]["func"])
                    action(name, ext, path)

                continue

            # postfix of name
            if target == "postfix":
                l = len(rule["arg"])
                if name[-l:] == rule["arg"]:
                    action = getattr(self, rule["action"]["func"])
                    action(name, ext, path)

                continue

            # in name
            if target == "in_name":
                if (name.lower().find(rule["arg"].lower()) != -1):
                    action = getattr(self, rule["action"]["func"])
                    action(name, ext, path)

                continue


    def action_print(self, name, ext, path):
        print(path)
    
    
    # def iterate_directory(self, path, depth):
    #     known_types = set({})
    #     directories = {0: [path]}
    #     repositories = []

    #     for i in range(0, depth):
    #         directories[i+1] = []
    #         for directory in directories[i]:
    #             directory = directory if directory[:-1] == "/" else directory + "/"
    #             for file in os.listdir(directory):
    #                 # print(file)
    #                 fullpath = f'{directory}{file}'
                    
    #                 filename, file_extension = os.path.splitext(file)
    #                 is_directory = os.path.isdir(fullpath)


    #                 if file_extension and not is_directory:
    #                     file_extension = self._sanatize_file_extension(file_extension)

    #                 if file_extension not in known_types and os.path.isfile(fullpath) and not is_directory:
    #                     known_types.add(file_extension)
                    
                    
    #                 elif is_directory:
    #                     if IGNORE_GIT_REPOSITORIES and self.is_git_repository(fullpath):
    #                         repositories.append(fullpath)
    #                     else:
    #                         directories[i+1].append(fullpath)


    #         # if file_extension not in known_types and os.path.isfile(f"{directory}{filename}"):
    #         #     known_types.add(file_extension)
    #         #     print("extension: " + file_extension)
    #         # elif os.path.isdir(f"{directory}{filename}"):
    #         #     print("directory: " + file_extension)

    #     print(directories)
    #     # print(repositories)

if __name__ == "__main__":
    fm = FileManager(rules)

    fm.run("/media/ulvfoerlev/DATA/Users/OccultEyes/Documents")

    # for name, ext, path in fm.iterate_directory("/media/ulvfoerlev/DATA/Users/OccultEyes/Documents"):
    #     print(f"{name}, {ext}, {path}")

#     .blp

# os.path.isdir(fpath)
# os.path.isfile(fpath)