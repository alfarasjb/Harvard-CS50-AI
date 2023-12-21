import sys

from crossword import *

class QueueFrontier: 

    def __init__(self):
        self.arc_queue = list()

    def initialize_queue(self, data):
        self.arc_queue = data 

    def dequeue(self):
        """
        Removes firt element in the queue, and returns the element
        """
        element = self.arc_queue[0]
        self.arc_queue.remove(element)
        return element

    def enqueue(self, element):
        """
        Adds an arc to a queue
        """
        self.arc_queue.append(element)

    def size(self):
        """
        Returns the size of the queue
        """
        return len(self.arc_queue)
    
    def empty(self):
        """
        Returns true if queue is empty, false if otherwise
        """
        val = True if self.size() == 0 else False 
        return val

queue = QueueFrontier()  

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for d in self.domains: 
            invalid_words = list()
            for item in self.domains[d]:
                if len(item) == d.length:
                    continue 

                invalid_words.append(item)

            [self.domains[d].remove(w) for w in invalid_words]
        
    
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlaps = self.crossword.overlaps[x, y]

        if overlaps is None: 
            return False 
        
        i, j = overlaps 
        invalid_words = list()

        for x_val in self.domains[x]:
            for y_val in self.domains[y]:
                if x_val[i] == y_val[j]:
                    continue 

                if x_val not in invalid_words:
                    invalid_words.append(x_val)

        [self.domains[x].remove(w) for w in invalid_words]

        revised = True if len(invalid_words) > 0 else False 
        return revised
    
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if queue.empty() and arcs is not None:
            return True 
        
        domains_keys = list(self.domains) if arcs is None else arcs
        
        if arcs is None and queue.empty(): 
            initial_queue = list()
            for j in domains_keys:
                for k in domains_keys: 
                    if j == k:
                        continue 
                    arc = (j,k)
                    if arc in queue.arc_queue:
                        continue 

                    initial_queue.append(arc)

            queue.initialize_queue(initial_queue)

        else:
            ar =queue.dequeue()
            if arcs is not None and len(arcs) > 0:
                ar = arcs[0]
            x, y = ar

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False 
                for n in self.crossword.neighbors(x):
                    if n == y:
                        continue 
                    queue.enqueue((x,n))
                self.ac3(queue.arc_queue)        
            else: 
                return True
 


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for d in self.domains:
            if d not in assignment:
                return False 
            if assignment[d] is None: 
                return False 
        return True
                    

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        seen = list()

        for var, val in assignment.items():
            if val in seen: 
                # duplicate 
                return False

            seen.append(val)

            neighbors = self.crossword.neighbors(var)
            # no conflicting characters with neighbor 
            for n in neighbors: 
                i, j = self.crossword.overlaps[var, n]
                if n not in assignment:
                    continue 
                if val[i] == assignment[n][j]:
                    continue 
                return False
                
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
   
        var_neighbors = self.crossword.neighbors(var)
        var_elements = list(self.domains[var])
        var_domain = dict()

        var_domain_reference = list()

        for v in var_elements: 
            v_count = 0
            if v in assignment.values():
                continue
            for n in var_neighbors:

                neighbor_list = self.domains[n]
                if v in neighbor_list:
                    v_count += 1
            var_domain_reference.append(v)
            var_domain[v] = v_count


        sorted_vars = sorted(var_domain_reference, key = var_domain.__getitem__)
    
        return sorted_vars
            
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
   
        min_domain = list()
        keys = self.domains
        for u in keys:
            if u in assignment: 
                continue  
            num_elements = len(self.domains[u])
            num_neighbors = len(list(self.crossword.neighbors(u)))
    
            if len(min_domain) == 0 or num_elements < min_domain[-1][1]:
                min_domain = [(u, num_elements, num_neighbors)]
            
            elif num_elements == min_domain[-1][1]:
                min_domain.append((u, num_elements, num_neighbors))

        max_neighbors = 0
        best = None

        if len(min_domain) > 1: 
            for m in min_domain: 

                if max_neighbors == 0: 
                    max_neighbors = m[2]
                    best = m[0]
                    continue

                if m[2] > max_neighbors: 
                    max_neighbors = m[2]
                    best = m[0] 
                
        else:
            best = min_domain[0][0]

        return best

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment 
        
        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val 
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None: 
                    return result 
                
            assignment.pop(var)
        
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()


