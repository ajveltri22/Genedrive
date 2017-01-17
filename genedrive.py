from __future__ import division
from random import choice as choice
from random import gauss as gauss
from random import random as random
from random import sample as sample
from string import ascii_uppercase as generation_ID

#TODO: fix generations over 26 to use correct identifiers
#TODO: make sure Population.check_parameters() is exhaustive
#TODO: data output formatting

class Parameters():
    def __init__(self):
        self.generations = 25           #number of generations to run
        self.pop_size = 10              #total population size
        self.num_introduced = 5          #number of organisms introduced
        self.inherit_chance = .95          #chance of inheritance of gene drive from heterozygous individual
        self.inherit_from_mother = True
        self.inherit_from_father = True
        self.mate_chance_average = 1   #chance to mate in generation
        self.mate_chance_stdev = 0
        self.male_reproduction_penalty = 0.3
        self.female_reproduction_penalty = 0.3
        self.max_litter_size = 1             #number of offspring per mating event
        self.max_lifespan = 5  # number of generations an individual lives
        self.stochastic_death = True
        self.avg_age_of_death = 5
        self.stdev_age_of_death = 1


class Population():
    def __init__(self, parameters):
        self.parameters = parameters

        self.members = {}
        self.male_list = []
        self.female_list = []
        self.heterozygous_carrier_list = []
        self.homozygous_carrier_list = []
        self.ancestry = {}
        self.num_pairs_mating_by_generation = []
        self.dead_list = []
        self.male_number = 0
        self.female_number = 0
        self.current_generation = 0
        self.parameter_check()
        self.create_generation_A()


        #self.update_sex_numbers()

    def parameter_check(self):
        if self.parameters.pop_size <= 0 or type(self.parameters.pop_size) is not int:
            raise Exception("pop_size must be a positive integer.")
        if self.parameters.num_introduced < 0 or type(self.parameters.num_introduced) is not int:
            raise Exception("num_introduced must be a nonnegative integer or zero.")
        if type(self.parameters.inherit_from_father) != bool or type(self.parameters.inherit_from_mother) != bool:
            raise Exception("inherit_from_father and inherit_from_mother must be booleans.")
        if self.parameters.num_introduced > 0 and not (self.parameters.inherit_from_mother or self.parameters.inherit_from_father):
            raise Exception("Inheritance must be turned on for at least one parent if num_introduced is nonzero.")
        if self.parameters.inherit_chance < 0 or self.parameters.inherit_chance > 1:
            raise Exception("inherit_chance must be between 0 and 1 inclusive.")
        if self.parameters.mate_chance_average < 0:
            raise Exception("mate_chance_average must be zero or greater.")
        if self.parameters.mate_chance_stdev < 0:
            raise Exception("mate_chance_stdev must be zero or greater.")
        if self.parameters.male_reproduction_penalty < 0 or self.parameters.female_reproduction_penalty < 0:
            raise Exception("Both reproduction penalties must be zero or greater.")
        if self.parameters.max_lifespan <= 1 or type(self.parameters.max_lifespan) is not int:
            raise Exception("max_lifespan must be an integer greater than 1")
        if self.parameters.max_litter_size <= 0 or type(self.parameters.max_litter_size) is not int:
            raise Exception("max_litter_size must be a positive integer.")
        if type(self.parameters.stochastic_death) != bool:
            raise Exception("stochastic_death must be a boolean.")
        if self.parameters.avg_age_of_death < 0:
            raise Exception("mate_chance_average must be zero or greater.")
        if self.parameters.stdev_age_of_death < 0:
            raise Exception("mate_chance_stdev must be zero or greater.")

    def create_generation_A(self):
        for i in range(self.parameters.pop_size):
            identifier = str(self.current_generation)+"_"+str(i+1)
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

    def death(self):
        kill_list = []
        not_today = []
        for i in self.members:
            self.members[i].age += 1
            if self.members[i].age > self.parameters.max_lifespan:
                kill_list.append(i)
            elif self.parameters.stochastic_death and gauss(self.parameters.avg_age_of_death, self.parameters.stdev_age_of_death) <= self.members[i].age:
                kill_list.append(i)
            else:
                not_today.append(i)
        for i in kill_list:
            self.kill(i)

    def kill(self, individual_id):
        if self.members[individual_id].sex == "M":
            self.male_number -= 1
            self.male_list.remove(individual_id)
        elif self.members[individual_id].sex == "F":
            self.female_number -= 1
            self.female_list.remove(individual_id)
        if individual_id in self.heterozygous_carrier_list:
            self.heterozygous_carrier_list.remove(individual_id)
        if individual_id in self.homozygous_carrier_list:
            self.homozygous_carrier_list.remove(individual_id)
        del self.members[individual_id]
        self.dead_list.append(individual_id)

    def mate(self):
        self.death()
        if len(self.male_list) >= len(self.female_list):
            self.num_pairs_mating_by_generation.append(len(self.female_list))
        else:
            self.num_pairs_mating_by_generation.append(len(self.male_list))
        moms = sample(self.female_list, self.num_pairs_mating_by_generation[self.current_generation])
        dads = sample(self.male_list, self.num_pairs_mating_by_generation[self.current_generation])
        pairs = []
        self.current_generation += 1
        for i in range(len(moms)):
            pairs.append([moms[i], dads[i]])
        for i in pairs:
            for j in range(self.parameters.max_litter_size):
                if random() <= self.members[i[0]].mate_chance*self.members[i[1]].mate_chance: #if True, pair mates
                    offspring_identifier = str(self.current_generation)+"_"+str(len(self.members) + 1)
                    #TODO: FIX ABOVE LINE
                    avg_mate_chance = (self.members[i[0]].mate_chance + self.members[i[1]].mate_chance) / 2
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
        if len(self.members) == 0:
            all_carrier_percentage = 0
        else:
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
            if self.pass_gene_chance > 0:
                if self.sex=="M":
                    self.mate_chance = mate_chance - self.parameters.male_reproduction_penalty
                if self.sex=="F":
                    self.mate_chance = mate_chance - self.parameters.female_reproduction_penalty
            else:
                self.mate_chance = mate_chance



def main():
    parameters = Parameters()
    population = Population(parameters)
    print(len(population.members))

    for i in range(parameters.generations):
        population.mate()
        print(len(population.members), population.get_carrier_percentage())



main()
