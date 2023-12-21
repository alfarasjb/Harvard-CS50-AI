import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S PP Conj S | S PP | S Conj S Adv | S Conj VP 
NP -> N | Det N | Det AdjP N | NP PP 
VP -> V | V NP | AdvP VP | AdvP V NP NP AdvP PP AdvP | V AdvP
AdjP -> Adj | AdjP Adj | AdvP Adj 
AdvP -> Adv | AdvP Adv | AdjP Adv 
PP -> P NP 
"""


grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    """
    Return -> LIST
    """

    processed = nltk.tokenize.wordpunct_tokenize(sentence)
    processed_sentence = [p.lower() for p in processed if p.isalpha()]
    return processed_sentence

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    
    if len(list(tree.subtrees())) == 1:
        return [tree]
    chunks = list()
    for s in tree.subtrees():
        # if label is not NP, continue 
        # if label is NP and NP not in children, continue 
        if s == tree: 
            continue
        num_children = len(list(s.subtrees()))
        
        if s.label() != 'NP':
            if num_children == 1:
                continue 
                
            if num_children > 1:
                c = np_chunk(s)
                #[chunks.append(g) for g in c]

        elif s.label() == 'NP':
            np_valid = False
            if num_children > 1:  
                # check all children, height must be 1 
                for child in s.subtrees():
                    child_subtree = len(list(child.subtrees()))
                    if child == s:
                        continue
                    # valid if height == 2 or len child subtree == 1
                    if child_subtree > 1:
                        break

                    np_valid = True 

                if np_valid: 
                    chunks.append(s)
        

    return chunks
   
if __name__ == "__main__":
    main()
