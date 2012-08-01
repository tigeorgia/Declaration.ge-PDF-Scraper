#!/usr/bin/python
# vim: set fileencoding=utf-8

#Asset declaration scraper -- scrapes and processes http://declaration.ge
#Copyright 2012 Transparency International Georgia http://transparency.ge
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import incomeExceptions 
from bs4 import BeautifulSoup

# Figures out which table we're parsing based on header information
def detect_table(num,ft2s):
    if num <= 11:
        # Guess page number first; usually page num == table num
        for ft2 in ft2s: 
            #print "Guessing table %d" %num
            #print "Header strings:" +(header_strings[num][0].encode('utf-8'))
            #print "FT2: "+(ft2.contents[0].encode('utf-8'))
            if ft2.contents[0] in header_strings[num]:
                #print "Detected table %d (guessed right)"%num
                return num

    for ft2 in ft2s:
        print "Guessed wrong, trying others"
        for i in range(1,len(header_strings)): # 1-indexed
            #print i
            #print ft2.contents[0]
            #print header_strings[i]
            if ft2.contents[0] in header_strings[i]:
                #print "Detected table %d (guessed wrong)"%i
                return i
    return 0


header_strings = [[""],# 1-indexed
    [u"თქვენი ოჯახის წევრების (მეუღლე, არასრულწლოვანი შვილი, გერი, თქვენთან მუდმივად მცხოვრები პირი) მონაცემები",u"თქვენი და თქვენი ოჯახის წევრების (მეუღლე, არასრულწლოვანი შვილი, გერი, თქვენთან მუდმივად მცხოვრები პირი) მონაცემები"],
    [u"თქვენი, თქვენი ოჯახის წევრის საკუთრებაში არსებული უძრავი ქონება"],
    [u"თქვენი, თქვენი ოჯახის წევრის საკუთრებაში არსებული მოძრავი ქონება (ფასიანი ქაღალდების, საბანკო ანგარიშების ან/და შენატანის, ნაღდი ფულადი თანხის გარდა),"],
    [u"თქვენი, თქვენი ოჯახის წევრის საკუთრებაში არსებული ფასიანი ქაღალდები"],
    [u"საქართველოს ან სხვა ქვეყნის საბანკო ან/და სხვა საკრედიტო დაწესებულებებში არსებული ანგარიში ან/და შენატანი, რომლის განკარგვის უფლება გაქვთ თქვენ, თქვენი"],
    [u"თქვენი, თქვენი ოჯახის წევრის საკუთრებაში არსებული ნაღდი ფულადი თანხა, რომლის ოდენობა აღემატება 4 000 ლარს"],
    [u"საქართველოში ან სხვა ქვეყანაში თქვენი, თქვენი ოჯახის წევრის მონაწილეობა სამეწარმეო საქმიანობაში"],
    [u"საქართველოში ან სხვა ქვეყანაში, თქვენი, თქვენი ოჯახის წევრის მიერ შესრულებული ნებისმიერი ანაზღაურებადი სამუშაო, სამეწარმეო საქმიანობაში მონაწილეობის გარდა"],
    [u"საქართველოში ან სხვა ქვეყანაში თქვენი, თქვენი ოჯახის წევრის მიერ წინა წლის პირველი იანვრიდან დღემდე დადებული  ან/და მოქმედი ხელშეკრულება, რომლის საგნის"], 
    [u"თქვენი, თქვენი ოჯახის წევრის მიერ წინა წლის პირველი იანვრიდან 31 დეკემბრის ჩათვლით მიღებული საჩუქარი, რომლის ღირებულება აღემატება 500 ლარს"],
    [u"წინა წლის პირველი იანვრიდან 31 დეკემბრის ჩათვლით თქვენი ან თქვენი ოჯახის წევრის ნებისმიერი შემოსავალი ან/და გასავალი, რომლის ოდენობა (ღირებულება)"], 
]
