#python genedrive.py pop_size num_introduced inherit_chance

import sys
from random import choice as choice


class Population():
    def __init__(self, pop_size, num_introduced, inherit_chance, male_mate_chance, female_mate_chance,
                 fitness_reduction):
        self.members = {}
        self.num_introduced = num_introduced
        self.male_number = 0
        self.female_number = 0
        for i in range(1,pop_size+1):
            if self.num_introduced > 0:
                self.members["A"+str(i)] = Individual(male_mate_chance, female_mate_chance, fitness_reduction, True)
                self.num_introduced -= 1
            else:
                self.members["A"+str(i)] = Individual(male_mate_chance, female_mate_chance, fitness_reduction, False)
        for i in self.members:
            if self.members[i].sex == "M":
                self.male_number += 1
            else:
                self.female_number += 1

    def update_sex_numbers(self):
        self.male_number = 0
        self.female_number = 0
        for i in self.members:
            if self.members[i].sex == "M":
                self.male_number += 1
            else:
                self.female_number += 1
        return self.male_number, self.female_number


class Individual():
    def __init__(self, male_mate_chance, female_mate_chance, fitness_reduction, has_gene):
        self.sex = choice(["M","F"])
        self.age = 0
        self.has_gene = has_gene
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


def main():

    generations = 100           #number of generations to run
    pop_size = 100              #total population size
    num_introduced = 1          #number of organisms introduced
    inherit_chance = 0.5        #chance of inheritance of gene drive
    male_mate_chance = 1.0      #chance of a male to mate in a generation
    female_mate_chance = 1.0    #chance of female to mate in generation
    fitness_reduction = 0.1     #reduction of mating chances of gene drive
    lifespan = 5                #number of generations an individual lives
    litter_size = 1             #number of offspring per mating event

    population = Population(pop_size, num_introduced, inherit_chance, male_mate_chance, female_mate_chance, fitness_reduction)
    print population.update_sex_numbers()

main()
