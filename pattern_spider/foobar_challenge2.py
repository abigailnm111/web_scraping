#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 12:08:41 2021

@author: panda
"""

def solution(l):
        new_list=[]
        l=[elevator.split(".") for elevator in l]
        print(l)
        major_list=sorted({e[0] for e in l})
        for x in major_list:
            all_majors=[[int(m) for m in i] for i in l if i[0]==x]
            if len(all_majors)==1:
                new_list.append(all_majors[0])
            else:
                for elevator in all_majors:
                    if len(elevator)==1:
                        new_list.append(elevator)
                        all_majors.remove(elevator)
                all_majors.sort(key=lambda x: x[1]) 
                minor_list=sorted({e[1] for e in all_majors})
                for minor in minor_list:
                    all_minors=[i for i in all_majors if i[1]==minor]
                    for minor in all_minors:
                        if len(minor)==2:
                            new_list.append(minor)
                            all_minors.remove(minor)
                    all_minors.sort(key=lambda x:x[2])
                    for revision in all_minors:
                        new_list.append(revision)
        new_list=['.'.join([str(m) for m in x]) for x in new_list]
        print( new_list)
        
        
        
    
    
        #print( asc_list)



solution(["1.11", "2.0.0", "1.2", "2", "0.1", "1.2.1", "1.1.1", "2.0"])