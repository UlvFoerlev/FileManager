
#Actions
# unzip_to - unzips the archive into target named folder ✓
# unzip - unzips an archive in the folder it is it ✓
# move - moves the file to a prenamed folder ✓
# delete - deletes the file ✓
# rename ✓

#targets 
# type - by file type ✓
# ext - by file extention ✓
# in_name - looks for substring in name ✓
# prefix - looks for substring at start of name ✓
# postfix - looks for substring at start of name ✓


# TODO:
#   And or targets


rules = [{"target" : "type", "args" : "image", "action" : {"func" : "action_print"}}]

class Rule:
    def __init__(self):
        pass


class ExtensionType(Rule):
    
    def __eq__(self, other):
        return other == "image"

class Extension(Rule):
    pass

class Substring(Rule):
    pass

class Prefix(Rule):
    pass

class PostFix(Rule):
    pass

class Targets(list):
    def where(self, eval):
        print(eval)


if __name__ == "__main__":
    t = Targets().where(ExtensionType=="image")