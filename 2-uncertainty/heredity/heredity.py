import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint = 1

    for p in people: 
        # iterate through people 
        # 1. identify parents, if has parents, calculate gene probility from parents (mutation, etc)
        # 2. get probability of number of genes 
        # 3. get probability of trait 
        # 4. multiply, and store for later. 
        # at the end of the iteration, multiply everything and return 
        
        mother, father = people[p]['mother'], people[p]['father']

        num_genes = 2 if p in two_genes else 1 if p in one_gene else 0

        if mother is not None and father is not None: 
            # calculate gene probability from parents
            # identify if parent has gene. 
            # identify if child has the gene, or none. 
            # need inheritance probability , 2 scenarios 

            gene_prob = get_inherited_gene(mother, father, one_gene, two_genes, num_genes)
        
        else: 
            # gene probability from PROBS
            
            gene_prob = PROBS["gene"][num_genes]

        trait_bool = True if p in have_trait else False
        traits_prob = PROBS['trait'][num_genes][trait_bool]

        combination = gene_prob * traits_prob 
        joint = joint * combination 

    return joint

    



def get_inherited_gene(mother, father, one_gene, two_genes, num_genes):
    """
    Helper function for determining inherited gene probability.
    """
    inherit_father = 0.99 if father in two_genes else 0.5 if father in one_gene else 0.01
    inherit_mother = 0.99 if mother in two_genes else 0.5 if mother in one_gene else 0.01
    prob_from_mother_only = inherit_mother * (1 - inherit_father)
    prob_from_father_only = inherit_father * (1 - inherit_mother)

    # if num genes = 2, inherit from both parents
    if num_genes == 2: 
        gene_prob = inherit_father * inherit_mother

    # if num genes = 1, inherit from either 
    elif num_genes == 1: 
        gene_prob = prob_from_father_only + prob_from_mother_only 
    
    # if num genes = 0, 1 - inherit prob 
    else: 
        # inverse of prob if 2 genes
        gene_prob = (1 - inherit_father) * (1 - inherit_mother)

    return gene_prob

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # iterate through probabilities dictionary, identify if one,two,or no genes, and if has trait 

    for prob in probabilities: 
        # identify gene prob by inheritance or not 
        # identify trait prob 
        num_genes = 2 if prob in two_genes else 1 if prob in one_gene else 0

        probabilities[prob]['gene'][num_genes] += p 
        probabilities[prob]['trait'][prob in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    

    for prob in probabilities:
        # get sum of each category, and percentage of each value vs the sum, and reassign. 

        genes = probabilities[prob]['gene']
        gene_sum = sum(list(genes.values()))
        
        for gene in genes.keys(): 

            percentage = genes[gene] / gene_sum
            probabilities[prob]['gene'][gene] = percentage 


        traits = probabilities[prob]['trait']
        trait_sum = sum(list(traits.values()))

        for t in traits.keys():

            percentage = traits[t] / trait_sum
            probabilities[prob]['trait'][t] = percentage
    
if __name__ == "__main__":
    main()
