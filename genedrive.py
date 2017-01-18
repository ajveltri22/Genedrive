from __future__ import division
from random import choice as choice
from random import gauss as gauss
from random import random as random
from random import sample as sample
from string import ascii_uppercase as generation_ID

#TODO: make sure Population.check_parameters() is exhaustive
#TODO: data output formatting
# TODO: double check mating chance logic
# assumes conversion only happens in germ line cells "Meiotic drive"

class Parameters():
    def __init__(self):
        self.generations = 1000           #number of generations to run
        self.initial_pop_size = 1000  #total population size
        self.population_cap = 7000         #Must be 'False' or a number greater than initial_pop_size
        self.num_introduced = 1  # number of organisms introduced
        self.inherit_chance = .3  #chance of inheritance of gene drive from heterozygous individual
        self.inherit_from_mother = True
        self.inherit_from_father = True
        self.initial_mate_chance_average = .9  # chance to mate in generation
        self.mate_chance_stdev = .05
        self.male_reproduction_penalty = 0
        self.female_reproduction_penalty = 0
        self.max_litter_size = 1             #number of offspring per mating event
        self.max_lifespan = 5  # number of generations an individual lives
        self.stochastic_death = True
        self.avg_age_of_death = 4
        self.stdev_age_of_death = .5
        self.parameter_check()

    def parameter_check(self):
        if self.initial_pop_size <= 0 or type(self.initial_pop_size) is not int:
            raise Exception("initial_pop_size must be a positive integer.")
        if self.population_cap == False:
            pass
        elif self.population_cap == True:
            raise Exception("population_cap must equal 'False' or an integer greater than or equal to initial_pop_size.")
        elif type(self.population_cap) != int:
            raise Exception("population_cap must equal 'False' or an integer greater than or equal to initial_pop_size.")
        elif self.population_cap < self.initial_pop_size:
            raise Exception("population_cap must equal 'False' or an integer greater than or equal to initial_pop_size.")
        if self.num_introduced < 0 or self.num_introduced > self.initial_pop_size or type(self.num_introduced) is not int:
            raise Exception("num_introduced must be a nonnegative integer or zero and must be less than or equal to initial_pop_size.")
        if type(self.inherit_from_father) != bool or type(self.inherit_from_mother) != bool:
            raise Exception("inherit_from_father and inherit_from_mother must be booleans.")
        if self.num_introduced > 0 and not (self.inherit_from_mother or self.inherit_from_father):
            raise Exception("Inheritance must be turned on for at least one parent if num_introduced is nonzero.")
        if self.inherit_chance < 0 or self.inherit_chance > 1:
            raise Exception("inherit_chance must be between 0 and 1 inclusive.")
        if self.initial_mate_chance_average < 0:
            raise Exception("initial_mate_chance_average must be zero or greater.")
        if self.mate_chance_stdev < 0:
            raise Exception("mate_chance_stdev must be zero or greater.")
        if self.male_reproduction_penalty < 0 or self.female_reproduction_penalty < 0:
            raise Exception("Both reproduction penalties must be zero or greater.")
        if self.max_lifespan <= 1 or type(self.max_lifespan) is not int:
            raise Exception("max_lifespan must be an integer greater than 1")
        if self.max_litter_size <= 0 or type(self.max_litter_size) is not int:
            raise Exception("max_litter_size must be a positive integer.")
        if type(self.stochastic_death) != bool:
            raise Exception("stochastic_death must be a boolean.")
        if self.avg_age_of_death < 0:
            raise Exception("initial_mate_chance_average must be zero or greater.")
        if self.stdev_age_of_death < 0:
            raise Exception("mate_chance_stdev must be zero or greater.")


class Population():
    def __init__(self, parameters):
        self.parameters = parameters

        self.cumulative_number_of_individuals = self.parameters.initial_pop_size
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
        self.create_generation_A()

    def create_generation_A(self):
        for i in range(self.parameters.initial_pop_size):
            identifier = str(self.current_generation)+"_"+str(i+1)
            assigned_mate_chance = gauss(self.parameters.initial_mate_chance_average, self.parameters.mate_chance_stdev)
            if self.parameters.num_introduced > 0:
                if self.parameters.inherit_from_mother and self.parameters.inherit_from_father:
                    self.members[identifier] = \
                        self.Individual(self.parameters, self.parameters.inherit_chance, assigned_mate_chance)
                    self.parameters.num_introduced -= 1
                elif self.parameters.inherit_from_mother and not self.parameters.inherit_from_father:
                    self.members[identifier] = \
                        self.Individual(self.parameters, self.parameters.inherit_chance,
                                        assigned_mate_chance, "F")
                    self.parameters.num_introduced -= 1
                elif self.parameters.inherit_from_father and not self.parameters.inherit_from_mother:
                    self.members[identifier] = \
                        self.Individual(self.parameters, self.parameters.inherit_chance,
                                        assigned_mate_chance, "M")
                    self.parameters.num_introduced -= 1
            else:
                self.members[identifier] = \
                    self.Individual(self.parameters, 0, assigned_mate_chance)

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
                if self.parameters.population_cap != False:
                    population_uncapped = len(self.members) < self.parameters.population_cap and gauss(.95*self.parameters.population_cap, 0.0167*len(self.members)) > len(self.members)
                else:
                    population_uncapped = True
                if random() <= self.members[i[0]].mate_chance*self.members[i[1]].mate_chance and population_uncapped: #if True, pair mates
                    self.cumulative_number_of_individuals += 1
                    offspring_identifier = str(self.current_generation)+"_"+str(self.cumulative_number_of_individuals)
                    avg_mate_chance = (self.members[i[0]].assigned_mate_chance + self.members[
                        i[1]].assigned_mate_chance) / 2
                    mother_pass_chance = self.members[i[0]].pass_gene_chance
                    father_pass_chance = self.members[i[1]].pass_gene_chance
                    frandom = random()
                    mrandom = random()
                    assigned_mate_chance = 0
                    while assigned_mate_chance == 0 or assigned_mate_chance > 1:
                        assigned_mate_chance = gauss(avg_mate_chance, self.parameters.mate_chance_stdev)
                    if self.parameters.inherit_from_father and self.parameters.inherit_from_mother:
                        if mrandom > mother_pass_chance and frandom > father_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters, 0,
                                                                                 assigned_mate_chance)
                        elif mrandom <= mother_pass_chance and frandom <= father_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters, 1,
                                                                                 assigned_mate_chance)
                        elif mrandom <= mother_pass_chance or frandom <= father_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters,
                                                                                 self.parameters.inherit_chance,
                                                                                 assigned_mate_chance)
                    elif self.parameters.inherit_from_father and not self.parameters.inherit_from_mother:
                        if frandom > father_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters, 0,
                                                                                 assigned_mate_chance)
                        elif frandom <= father_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters,
                                                                                 self.parameters.inherit_chance,
                                                                                 assigned_mate_chance)
                    elif self.parameters.inherit_from_mother and not self.parameters.inherit_from_father:
                        if mrandom > mother_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters, 0,
                                                                                 assigned_mate_chance)
                        elif mrandom <= mother_pass_chance:
                            self.members[offspring_identifier] = self.Individual(self.parameters,
                                                                                 self.parameters.inherit_chance,
                                                                                 assigned_mate_chance)
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

    def get_mate_chance_average(self):
        mate_chance_sum = 0
        for i in self.members:
            mate_chance_sum += self.members[i].mate_chance
        if len(self.members) == 0:
            return 0
        else:
            population_average_mate_chance = mate_chance_sum / len(self.members)
            return population_average_mate_chance

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
            self.assigned_mate_chance = mate_chance
            if self.assigned_mate_chance > 1:
                self.assigned_mate_chance = 1
            if self.pass_gene_chance > 0:
                if self.sex=="M":
                    self.mate_chance = self.assigned_mate_chance - self.parameters.male_reproduction_penalty
                if self.sex=="F":
                    self.mate_chance = self.assigned_mate_chance - self.parameters.female_reproduction_penalty
            else:
                self.mate_chance = mate_chance


def main():
    parameters = Parameters()
    population = Population(parameters)
    x = population.get_carrier_percentage()
    num_introduced = parameters.num_introduced
    print(population.current_generation, len(population.members), x, population.get_mate_chance_average())
    for i in range(parameters.generations):
        population.mate()
        x = population.get_carrier_percentage()
        print(population.current_generation, len(population.members), x, population.get_mate_chance_average())
        if len(population.members)==0:
            print("Population zero at generation " + str(population.current_generation) + ", " + str(
                population.cumulative_number_of_individuals) + " total individuals.")
            break
        elif x == 0 and num_introduced != 0:
            print("Gene drive gone at generation " + str(population.current_generation) + ", " + str(
                population.cumulative_number_of_individuals) + " total individuals.")
            break


main()
