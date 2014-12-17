'''
Created on 28/10/2014

@author: aurelio
'''

import sys
from lxml import etree
import re


file = '/media/aurelio/tera2/wiki/es/eswiki-20140828-pages-meta-current.xml'

def _get_namespace(tag):
    namespace = re.match("^{(.*?)}", tag).group(1)
    if not namespace.startswith("http://www.mediawiki.org/xml/export-"):
        raise ValueError("%s not recognized as MediaWiki database dump"
                         % namespace)
    return namespace


def extract_pages(f):
    """Extract pages from Wikimedia database dump.

    Parameters
    ----------
    f : file-like or str
        Handle on Wikimedia article dump. May be any type supported by
        etree.iterparse.

    Returns
    -------
    pages : iterable over (int, string, string)
        Generates (page_id, title, content) triples.
        In Python 2.x, may produce either str or unicode strings.
    """
    elems = (elem for _, elem in etree.iterparse(f, events=["end"]))

    # We can't rely on the namespace for database dumps, since it's changed
    # it every time a small modification to the format is made. So, determine
    # those from the first element we find, which will be part of the metadata,
    # and construct element paths.
    elem = next(elems)
    namespace = _get_namespace(elem.tag)
    ns_mapping = {"ns": namespace}
    page_tag = "{%(ns)s}page" % ns_mapping
    text_path = "./{%(ns)s}revision/{%(ns)s}text" % ns_mapping
    id_path = "./{%(ns)s}id" % ns_mapping
    title_path = "./{%(ns)s}title" % ns_mapping

    for elem in elems:
        if elem.tag == page_tag:
            text = elem.find(text_path).text
            if text is None:
                continue
            yield (int(elem.find(id_path).text),
                   elem.find(title_path).text,
                   text)

            # Prune the element tree, as per
            # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
            # We do this only for <page>s, since we need to inspect the
            # ./revision/text element. That shouldn't matter since the pages
            # comprise the bulk of the file.
            elem.clear()
            if hasattr(elem, "getprevious"):
                # LXML only: unlink elem from its parent
                while elem.getprevious() is not None:
                    del elem.getparent()[0]


if __name__ == "__main__":
    # Test; will write article info + prefix of content to stdout
    """
    if len(sys.argv) > 1:
        print("usage: %s; will read from standard input" % sys.argv[0],
              file=sys.stderr)
        sys.exit(1)
    """
    inicio = 10000
    numin = 0
    limite = 300
    num = 0
    for pageid, title, text in extract_pages(file):
        numin +=1
        if numin > inicio:
            num+=1
            if num < limite:
                # pageid = pageid.encode('utf-8')
                # title = title.encode("utf-8")
                text = text[:200].replace("\n", "_")
                print("%d '%s' (%s)" % (pageid, title, text))