from __future__ import division
from random import choice as choice
from random import gauss as gauss
from random import random as random
from random import sample as sample
from string import ascii_uppercase as generation_ID

#TODO: fix generations over 26 to use correct identifiers
#TODO: initial gene drive assignment doesn't work if inherit_chance is 1 or 0
#TODO: Add age tracking and death of individuals
#TODO: implement litter_size in mating

class Parameters():
    def __init__(self):
        self.generations = 1           #number of generations to run
        self.pop_size = 100              #total population size
        self.num_introduced = 5          #number of organisms introduced
        self.inherit_chance = 1        #chance of inheritance of gene drive from heterozygous individual
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
        self.heterozygous_carrier_list = []
        self.homozygous_carrier_list = []
        self.ancestry = {}
        self.num_pairs_per_mating = []
        self.male_number = 0
        self.female_number = 0
        self.current_generation = 0
        self.create_generation_A()

        #self.update_sex_numbers()

    def create_generation_A(self):
        for i in range(self.parameters.pop_size):
            identifier = generation_ID[self.current_generation]+str(i+1)
            if self.parameters.num_introduced > 0:
                if self.parameters.inherit_from_mother and self.parameters.inherit_from_father:
                    self.members[identifier] = \
                        self.Individual(self.parameters, self.parameters.inherit_chance, gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev))
                    self.parameters.num_introduced -= 1
                elif self.parameters.inherit_from_mother and not self.parameters.inherit_from_father:
                    self.members[identifier] = \
                        self.Individual(self.parameters, self.parameters.inherit_chance,
                                   gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev), "F")
                    self.parameters.num_introduced -= 1
                elif self.parameters.inherit_from_father and not self.parameters.inherit_from_mother:
                    self.members[identifier] = \
                        self.Individual(self.parameters, self.parameters.inherit_chance,
                                   gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev), "M")
                    self.parameters.num_introduced -= 1
                else:
                    raise Exception("Inheritance must be turned on for at least one parent if num_introduced is nonzero.")
            else:
                self.members[identifier] = \
                    self.Individual(self.parameters, 0, gauss(self.parameters.mate_chance_average, self.parameters.mate_chance_stdev))

            if self.members[identifier].sex == "M":
                self.male_list.append(identifier)
                self.male_number += 1
            elif self.members[identifier].sex == "F":
                self.female_list.append(identifier)
                self.female_number += 1

            if 1 > self.members[identifier].pass_gene_chance > 0:
                self.heterozygous_carrier_list.append(identifier)
            elif self.members[identifier].pass_gene_chance == 1:
                self.homozygous_carrier_list.append(identifier)

    '''
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
    '''
    
    def mate(self):

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
            if random() <= self.members[i[0]].mate_chance*self.members[i[1]].mate_chance: #if True, pair mates
                avg_mate_chance = (self.members[i[0]].mate_chance+self.members[i[1]].mate_chance)/2
                offspring_identifier = generation_ID[self.current_generation] + str(len(self.members) + 1)
                mother_pass_chance = self.members[i[0]].pass_gene_chance
                father_pass_chance = self.members[i[1]].pass_gene_chance
                frandom = random()
                mrandom = random()
                
                if self.parameters.inherit_from_father and self.parameters.inherit_from_mother:
                    if mrandom > mother_pass_chance and frandom > father_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters, 0,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                    elif mrandom <= mother_pass_chance and frandom <= father_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters, 1,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                    elif mrandom <= mother_pass_chance or frandom <= father_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters, self.parameters.inherit_chance,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                elif self.parameters.inherit_from_father and not self.parameters.inherit_from_mother:
                    if frandom > father_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters, 0,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                    elif frandom <= father_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters,
                                                                              self.parameters.inherit_chance,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                elif self.parameters.inherit_from_mother and not self.parameters.inherit_from_father:
                    if mrandom > mother_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters, 0,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                    elif mrandom <= mother_pass_chance:
                        self.members[offspring_identifier] = self.Individual(self.parameters,
                                                                              self.parameters.inherit_chance,
                                                                              gauss(avg_mate_chance,
                                                                                    self.parameters.mate_chance_stdev))
                self.ancestry[offspring_identifier] = i
                if self.members[offspring_identifier].sex == "M":
                    self.male_list.append(offspring_identifier)
                    self.male_number += 1
                elif self.members[offspring_identifier].sex == "F":
                    self.female_list.append(offspring_identifier)
                    self.female_number += 1

                if 1 > self.members[offspring_identifier].pass_gene_chance > 0:
                    self.heterozygous_carrier_list.append(offspring_identifier)
                elif self.members[offspring_identifier].pass_gene_chance == 1:
                    self.homozygous_carrier_list.append(offspring_identifier)
            else:
                pass

    def get_carrier_percentage(self):
        heterozygous_percentage = len(self.heterozygous_carrier_list)/len(self.members)
        homozygous_percentage = len(self.homozygous_carrier_list)/len(self.members)
        all_carrier_percentage = heterozygous_percentage + homozygous_percentage

        return all_carrier_percentage

    class Individual():
        def __init__(self, parameters, pass_gene_chance, mate_chance, sex=None):
            self.parameters = parameters
            if not sex:
                self.sex = choice(["M","F"])
            else: self.sex = sex
            self.age = 0
            self.pass_gene_chance = pass_gene_chance
            self.mate_chance = mate_chance



def main():
    parameters = Parameters()
    population = Population(parameters)
    print population.get_carrier_percentage()

    for i in range(parameters.generations):
        population.mate()
    print population.get_carrier_percentage()



main()
