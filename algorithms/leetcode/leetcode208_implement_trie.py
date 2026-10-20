"""

A trie (pronounced as "try") or prefix tree is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. There are various applications of this data structure, such as autocomplete and spellchecker.

Implement the Trie class:

Trie() Initializes the trie object.
void insert(String word) Inserts the string word into the trie.
boolean search(String word) Returns true if the string word is in the trie (i.e., was inserted before), and false otherwise.
boolean startsWith(String prefix) Returns true if there is a previously inserted string word that has the prefix prefix, and false otherwise.


"""

class Trie:
    def __init__(self):
        self.children = defaultdict(Trie)
        self.isWord = False

    def insert(self, word):
        for c in word:
            self = self.children[c]
        self.isWord = True

    def search(self, word):
        for c in word:
            if c not in self.childern:
                return False
            self = self.childern[c]
        return self.isWord 

    def startsWith(self, prefix):
        for c in prefix:
            if c not in self.childern:
                return False
            self = self.childern[c]
        return True
