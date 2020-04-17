
import hashlib
import io
import os


class GenBase():
    """
    This class does generation of the contents and digests files.
    """

    def __init__(self, myspec):
        self.settings = myspec

    @staticmethod
    def generate_hash(filepath, name):
        h = hashlib.new(name)

        with open(filepath, 'rb') as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                h.update(data)

        filename = os.path.split(filepath)[1]
        return f'# {name.upper()} HASH\n{h.hexdigest()}  {filename}\n'

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
            if os.path.exists(path):
                with io.open(digests, "w", encoding='utf-8') as myf:
                    for f in [path, path + '.CONTENTS']:
                        if os.path.exists(f):
                            for i in self.settings["digests"].split():
                                digest = self.generate_hash(f, name=i)
                                myf.write(digest)
