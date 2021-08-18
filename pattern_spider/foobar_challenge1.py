#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 16:00:17 2021

@author: panda
"""
s=("abcabcdefabcabcdefabcabcdef")

def solution(s):
    i=0
    pattern=""
    for letter in s:
        pattern+=letter
        i+=1
        print("pattern", pattern, "s", s[i:i+len(pattern)])
        if pattern== s[i:i+len(pattern)] and len(s)%len(pattern)==0:
            x=len(pattern)
            servings= int(len(s)/len(pattern))
            
            for slice in range(1,servings):
                print(s[slice*x:slice*x+x])

                if pattern!= s[slice*x:slice*x+x]:

                    break
                print ("slice", slice, "serv",servings)
                if slice+1==servings:

                    return servings
    return 1

        
print(solution(s))