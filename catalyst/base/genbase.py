
import hashlib
import io
import os
import gzip

class GenBase():
    """
    Generates CONTENTS and DIGESTS files.
    """

    def __init__(self, myspec):
        self.settings = myspec

    def generate_hash(self, filepath, name):
        h = hashlib.new(name)

        with open(filepath, 'rb') as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                h.update(data)

        filename = os.path.split(filepath)[1]

        if self.settings['digest_format'] == 'bsd':
            return f'# {name.upper()} HASH\n{name.upper()} ({filename}) = {h.hexdigest()}\n'
        else:
            return f'# {name.upper()} HASH\n{h.hexdigest()}  {filename}\n'

    def gen_contents_file(self, path):
        c = self.settings['contents_map']

        with gzip.open(path + '.CONTENTS.gz', 'wt', encoding='utf-8') as file:
            file.write(c.contents(path, '', verbose=self.settings['VERBOSE']))

    def gen_digest_file(self, path):
        if 'digests' not in self.settings:
            return

        with io.open(path + '.DIGESTS', 'w', encoding='utf-8') as file:
            for f in [path, path + '.CONTENTS.gz']:
                for i in self.settings['digests']:
                    file.write(self.generate_hash(f, name=i))
