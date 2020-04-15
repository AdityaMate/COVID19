import numpy as np
import random
import networkx as nx






class FamilyUnit(object):
    def __init__(self, family_size,member_age):
        self.family_size=family_size
        self.member_age=member_age
        self.member_list=[]
        
