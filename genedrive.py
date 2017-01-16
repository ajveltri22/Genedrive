from random import choice as choice
from random import gauss as gauss
from random import random as random
from random import sample as sample
from string import ascii_uppercase as generation_ID

class Parameters():
    def __init__(self):
        self.generations = 100           #number of generations to run
        self.pop_size = 100              #total population size
        self.num_introduced = 1          #number of organisms introduced
        self.inherit_chance = 0.5        #chance of inheritance of gene drive from heterozygous individual
        self.inherit_from_mother = True
        self.inherit_from_father = True
        self.mate_chance_average = 1.0 #chance of female to mate in generation
        self.mate_chance_stdev = 0
        self.male_reproduction_penalty = 0.1
        self.female_reproduction_penalty = 0.1
        self.max_lifespan = 5                #number of generations an individual lives
        self.litter_size = 1             #number of offspring per mating event


class Population():
    def __init__(self, parameters):
        self.parameters = parameters

        self.members = {}
        self.male_list = []
        self.female_list = []
        self.ancestry = {}
        self.num_pairs_per_mating = []
        self.male_number = 0
        self.female_number = 0
        self.current_generation = 0
        self.create_generation_A()
        self.update_sex_numbers()

    def create_generation_A(self): #TODO there's a problem here, because if inheritance is turned off from mother or father, this won't distinguish when it decides who gets the gene drive. Neeed to assign gene drive at individual level?
        for i in range(1,self.parameters.pop_size+1):
            if self.parameters.num_introduced > 0:
                self.members[generation_ID[self.current_generation]+str(i)] = \
                    Individual(self.parameters, self.parameters.inherit_chance, gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev))
                self.parameters.num_introduced -= 1
            else:
                self.members[generation_ID[self.current_generation]+str(i)] = \
                    Individual(self.parameters, 0, gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev))

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
            if random() <= self.members[i[0]].mate_chance*self.members[i[1]].mate_chance:
                avg_mate_chance = (self.members[i[0]].mate_chance+self.members[i[1]])/2

                #TODO figure out heterozygosity and how gene is inherited:
                if self.members[i[0]].has_gene and self.members[i[1]].has_gene and self.parameters.inherit_from_father and self.parameters.inherit_from_mother:
                    self.members[generation_ID[self.current_generation]+
                             str(len(self.members)+1)] = Individual(self.parameters, True, gauss(avg_mate_chance, self.parameters.mate_chance_stdev))
                elif self.members[i[0]].has_gene and self.parameters.inherit_from_mother:

                    self.members[generation_ID[self.current_generation]+
                             str(len(self.members)+1)] = Individual(self.parameters, True, gauss(avg_mate_chance, self.parameters.mate_chance_stdev))

            else:
                pass




class Individual(): #TODO: figure out how mate selection and reproduction chances need to be calculated
    def __init__(self, parameters, pass_gene_chance, mate_chance):
        self.parameters = parameters
        self.sex = choice(["M","F"])
        self.age = 0
        self.pass_gene_chance = pass_gene_chance
        self.mate_chance = mate_chance
        '''
        if not self.ancestors:
            self.mate_chance = gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev)
        else:
            avg_mate_chance = (members[self.ancestors[-1][0]].mate_chance+members[self.ancestors[-1][1]].mate_chance)/2
            self.mate_chance = gauss(avg_mate_chance, self.parameters.mate_chance_stdev)
        '''


def main():
    population = Population(Parameters())
    population.mate()
    print population.update_sex_numbers()

main()
