
import io
import os


class GenBase():
    """
    This class does generation of the contents and digests files.
    """

    def __init__(self, myspec):
        self.settings = myspec

    def gen_contents_file(self, path):
        contents = path + ".CONTENTS"
        if os.path.exists(contents):
            os.remove(contents)

        contents_map = self.settings["contents_map"]
        if os.path.exists(path):
            with io.open(contents, "w", encoding='utf-8') as myf:
                contents = contents_map.contents(path, '',
                                                 verbose=self.settings["VERBOSE"])
                if contents:
                    myf.write(contents)

    def gen_digest_file(self, path):
        digests = path + ".DIGESTS"
        if os.path.exists(digests):
            os.remove(digests)
        if "digests" in self.settings:
            hash_map = self.settings["hash_map"]
            if os.path.exists(path):
                with io.open(digests, "w", encoding='utf-8') as myf:
                    for f in [path, path + '.CONTENTS']:
                        if os.path.exists(f):
                            for i in self.settings["digests"].split():
                                digest = hash_map.generate_hash(f, hash_=i)
                                myf.write(digest)
