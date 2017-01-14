import sys
from random import choice as choice
from random import sample as sample
from string import ascii_uppercase as generation_ID

class Parameters():
    def __init__(self):
        self.generations = 100           #number of generations to run
        self.pop_size = 100              #total population size
        self.num_introduced = 1          #number of organisms introduced
        self.inherit_chance = 0.5        #chance of inheritance of gene drive
        self.inherit_from_mother = True
        self.inherit_from_father = True
        self.male_mate_chance = 1.0      #chance of a male to mate in a generation
        self.female_mate_chance = 1.0    #chance of female to mate in generation
        self.male_reproduction_penalty = 0.1
        self.male_mate_finding_penalty = 0.0
        self.female_reproduction_penalty = 0.1
        self.female_mate_finding_penalty = 0.0
        self.max_lifespan = 5                #number of generations an individual lives
        self.litter_size = 1             #number of offspring per mating event


class Population():
    def __init__(self, parameters):
        self.parameters = parameters

        self.members = {}
        self.male_list = []
        self.female_list = []
        self.num_pairs_per_mating = []
        self.male_number = 0
        self.female_number = 0
        self.current_generation = 0
        self.create_generation_A()
        self.update_sex_numbers()

    def create_generation_A(self):
        for i in range(1,self.parameters.pop_size+1):
            if self.parameters.num_introduced > 0:
                self.members[generation_ID[self.current_generation]+str(i)] = \
                    Individual(self.parameters, True)
                self.parameters.num_introduced -= 1
            else:
                self.members[generation_ID[self.current_generation]+str(i)] = \
                    Individual(self.parameters, False)

    def update_sex_numbers(self):
        self.male_number = 0
        self.female_number = 0
        self.male_list = []
        self.female_list = []
        for i in self.members:
            if self.members[i].sex == "M":
                self.male_list.append(i)
                self.male_number += 1
            else:
                self.female_list.append(i)
                self.female_number += 1
        return self.male_number, self.female_number
    
    
    def mate(self): #TODO: ancestor tracking and mate chance

        if len(self.male_list) >= len(self.female_list):
            self.num_pairs_per_mating.append(len(self.female_list))
        else:
            self.num_pairs_per_mating.append(len(self.male_list))
        moms = sample(self.female_list, self.num_pairs_per_mating[self.current_generation])
        dads = sample(self.male_list, self.num_pairs_per_mating[self.current_generation])
        pairs = []
        self.current_generation += 1
        for i in range(len(moms)):
            pairs.append([moms[i], dads[i]])
        for i in pairs:
            if self.members[i[0]].has_gene or self.members[i[1]].has_gene:
                self.members[generation_ID[self.current_generation]+
                             str(len(self.members)+1)] = Individual(self.parameters, True, )
            else:
                self.members[generation_ID[self.current_generation]+
                             str(len(self.members)+1)] = Individual(self.parameters, False)


        self.current_generation += 1

class Individual(): #TODO: figure out how mate selection and reproduction chances need to be calculated
    def __init__(self, parameters, has_gene, ancestors=[]):
        self.sex = choice(["M","F"])
        self.age = 0
        self.has_gene = has_gene
        self.ancestors = ancestors
        '''
        if not self.has_gene:
            if self.sex == "M":
                self.mate_chance = male_mate_chance
            else:
                self.mate_chance = female_mate_chance
        else:
            if self.sex == "M":
                self.mate_chance = male_mate_chance - fitness_reduction
            else:
                self.mate_chance = female_mate_chance - fitness_reduction
        '''

def main():
    population = Population(Parameters())
    population.mate()
    print population.update_sex_numbers()

main()
