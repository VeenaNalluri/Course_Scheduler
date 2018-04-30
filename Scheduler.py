import course_dictionary
import copy
import time
import pprint
from collections import namedtuple

#Main Function
#def course_scheduler(Dict, goalCourses, initialCourses)
def course_scheduler(Dict, goalCourses, initialCourses) :
    #Dict: Dictionary storing course information
    goalCourses = Goal
    initialCourses = Initial
    output = None
    # Start_Time: for recording start time of searching
    Start_time = time.time()
    while output == None:
        #DepthFirstSearch is done until goal is reached
        output = DepthFirstSearch(Nodes, VisitedNodes)

    if(output== 0):
        print('Goal cannot be reached')
        return None

    End_time = time.time()
    # Execution Time for running is noted
    print('ExecutionTime =', End_time - Start_time, 's')
    FinalState = output[0]
    FinalOperator = output[1]
    # Move courses in plan forward so courses would be taken at earlier semesters
    print('\n Original Schedule \n')
    Scheduler(FinalOperator)
    while (not MovecourseToPreviousTerms(FinalState, FinalOperator, VisitedNodes)):
        None
    print('\n Modified Schedule\n')
    # List the Schedule satisfying goal,initial and prerequisites requirements but may not satisfy 12 credits limit
    Scheduler(FinalOperator)
    # TermInfo contains information whether the number of credits in each semester is too many or too few
    # code for adding random courses to satisfy minimum credit limit
    TermInfo1 = TermInfo(FinalOperator)
    Operatorchanged = 0
    for terminfo in TermInfo1:   # TermInfo : [ScheduledTerm, nbrOfCredits, Limit]
        if terminfo[2] < 0:   #means we can add few courses to fill the minimum credit limit
            addRandomCourses(FinalOperator, terminfo[0], terminfo[2])
            Operatorchanged = 1
        if terminfo[2] > 0:
            print(terminfo[0], 'Too many credits')

    if Operatorchanged:
        print('\n Add some random courses to satisfy minimum credits limit \n')
        Scheduler(FinalOperator)
# Creating the final Operator as a dictionary with key as courses in the final operator and the value as CourseInfo
    Course_Dict = {}
    Course = namedtuple('Course', 'program, designation')
    CourseInfo = namedtuple('CourseInfo', 'credits, terms, prereqs')

    for e in FinalOperator:
        key = Course(e[0][0],e[0][1])
        x = Dict[e[0]]
        Value = CourseInfo(x[0],e[1],x[2])
        Course_Dict[key]= Value
    print('\n','Final Course Scheduler:','\n')
    pprint.pprint(Course_Dict)

    return

Dict=course_dictionary.create_course_dict()# (CREDITS,TERM,PREREQS)
Goal = {('CS', '4260')}  # set your Goal Courses
Initial = {('CS', '1101')}  # set your Initial Courses

Initial=set()
# Schedule varialbles
Scheduled_Terms=(('Fall','Frosh'),('Spring','Frosh'),('Fall','Soph'),('Spring','Soph'),('Fall','Junior'),('Spring','Junior'),('Fall','Senior'),('Spring','Senior'))
Operator = set()  #(course, term, credit)

def InitialPrereqCond(Goal):

    PrereqCond = set()    #(course,term)
    for course in Goal:
        PrereqCond.add((course, 7))
    return PrereqCond

PrereqCond = InitialPrereqCond(Goal)
VisitedNodes=[]
Nodes=[(Goal,Operator,PrereqCond),]
# returns true if goal is reached
def Reachgoal(node):

    # getting state and operator from node
    State=node[0]
    Operator=node[1]
    # If currentState is not subset of initial state goal is not reached
    if not State.issubset(Initial):# Initial state reached
        return 0

    for ScheduledTerm in Scheduled_Terms: # if nbrofCredits greater than 18 goal is not reached
        nbrOfCredits=sum([C[2] for C in Operator if C[1]==ScheduledTerm])
        if nbrOfCredits>18:
            return 0

    for Op in Operator:
        idx=Scheduled_Terms.index(Op[1])
        Courseset={c[0] for c in Operator if c[1] in Scheduled_Terms[0:idx+1]} # find all courses taken in the semester before of the course term
        for prep in Dict[Op[0]][2]:  # getting prereqs of the current course
            if set(prep).issubset(Courseset): # if the set of prep contains atleast one of the course from course set then returns true
                return 1

        if Dict[Op[0]][2]!=():  # if prereqs is not empty goal is not reached
            return 0

    return 1


# depth first search is performed until goal is reached
def DepthFirstSearch(Nodes,VisitedNodes):
    n=Nodes.pop()# (State,Plan)
    if n in VisitedNodes:
        return None
    VisitedNodes.append(n)
    if Reachgoal(n):
        return n
# extract the variables from node
    State=n[0]
    Operator=n[1]
    PrereqCond=n[2]
    for term in Scheduled_Terms:
        Nextnodes_h = possibleConstraints(State, Operator, term, PrereqCond)
        if(Nextnodes_h == None):  # if Nextnodes_h is none means we can't reach goal
            #print('Not Possible')
            return 0

        else:
            Nextnodes_h.sort(key=lambda Nextnode_h: Nextnode_h[1],reverse=True)
            # possible substates in order of their heuristic info
            Nextnodes=[Nextnode_h[0] for Nextnode_h in Nextnodes_h]
            Nodes.extend(Nextnodes)

    return None
# update Operator for each new course and function returns the NewCourse,Term and credits
def updateOperator(Operator,NewCourse,ScheduledTerm,Credit):
    temp = [temp for temp in Operator if temp[0]==NewCourse]
    if temp==[]:            # if operator is empty add new course
        Operator.add((NewCourse,ScheduledTerm,Credit))
    else:
        OldOperator=temp[0]
        if Scheduled_Terms.index(ScheduledTerm)<Scheduled_Terms.index(OldOperator[1]):
            Operator.remove(OldOperator)        # if scheduled term index is small than opeartor index remove old opeartor and add new course
            Operator.add((NewCourse,ScheduledTerm,Credit))
    return Operator
# update PrereqCond with new terms when it is taken
def updatePrereqCondition(PrereqCond,Termindex,Prereqs,Higherlevelreq):
    if not Higherlevelreq: # Higherlevelrequirement cannot be taken in the same term as prereqs
        Termindex=Termindex-1

    if Termindex<0:   # term index cannot be 0
        return None
    for course in Prereqs: # update PrereqCond for all the prereqs
        PrereqCond=Update_Courseterm(PrereqCond,course,Termindex)

    return PrereqCond


def Update_Courseterm(PrereqCond, course, NewTermindex):

    TempCond = [Cond for Cond in PrereqCond if Cond[0] == course]
    if(TempCond == None):
        print(course,NewTermindex)

    PrereqCond = PrereqCond - set(TempCond)
    NewCond = (course, NewTermindex)
    TempCond.append(NewCond)
    FinalCond = min(TempCond, key=lambda c: c[1])
    PrereqCond.add(FinalCond)
    return PrereqCond

# if course is a higher requirement set credits as 0
def IsCourseHigherRequirement(Course):
    if Dict[Course].credits== '0':
        return 1
    return 0

# displays the final operator
def Scheduler(Operator):# Operator : Course,Terms,Credits
    if (Goal == Initial):
        print({})
    for ScheduledTerm in  Scheduled_Terms:
        nbrOfCredit = sum([C[2] for C in Operator if C[1] == ScheduledTerm and not IsCourseHigherRequirement(C[0])])
        Course = [C[0] for C in Operator if C[1] == ScheduledTerm and not IsCourseHigherRequirement(C[0])]
        print(ScheduledTerm, nbrOfCredit, Course)

# defines all the possible constarints if satisfoed add the new node
def possibleConstraints(State,Operator,ScheduledTerm,PrereqCond):
    Nextnodes_h = []  # empty list with new nodes to be added if all constraints are satisfies
    for s in State:
        if s in Initial:
            continue
        if (PrereqCond==None):   # if PrereqCond is none goal cannot be reached
            #print(s,Operator,ScheduledTerm)
            return None
        else:
            CourseTerm = [PC[1] for PC in PrereqCond if PC[0] == s]  # ggetting the latest term course can be taken
            CourseTerm = CourseTerm[0]
            if Scheduled_Terms.index(ScheduledTerm) > CourseTerm:
                continue

        CourseInfo = Dict[s]

        if ScheduledTerm[0] not in CourseInfo[1]:
            continue
        # If total credits of this semester exceed 18
        nbrOfCredits = sum([C[2] for C in Operator if C[1] == ScheduledTerm])
        if nbrOfCredits + int(CourseInfo[0]) > 18:
            continue

        # Heuristic function len(State-InitialState)
        if CourseInfo[2] == ():
            O = (((), s), ScheduledTerm, int(CourseInfo[0]))
            Addnewnode(Nextnodes_h, State, Operator, O, PrereqCond)
        else:
            for prereq in CourseInfo[2]:
                O = ((prereq, s), ScheduledTerm, int(CourseInfo[0]))
                Addnewnode(Nextnodes_h, State, Operator, O, PrereqCond)
    return Nextnodes_h

def copiedInstance(self):
    return copy.deepcopy(self)

# function defining how and when to add new node given current node
def Addnewnode(Newnodes_h,State,Operator,O,PrereqCond):
    # copy the instances of current node: (State,Operator,PrereqCond
    S=copiedInstance(State)
    Op=copiedInstance(Operator)
    PC=copiedInstance(PrereqCond)
    S=S.union(set(O[0][0]))   #update the state by removing the course to be selected and adding one of its prereq
    S.remove(O[0][1])
    Op=updateOperator(Op,O[0][1],O[1],O[2]) # update operator
    PC=updatePrereqCondition(PC,Scheduled_Terms.index(O[1]),O[0][0],IsCourseHigherRequirement(O[0][1])) # update PrereqCond
    if PC==None and O[0][0]!=():
        return

    Newnode=(S,Op,PC)  #Newnode :(State,Operator,PrereqCond
    h=len(S-Initial)
    if not (Newnode in VisitedNodes or Newnode in Newnodes_h):
        Newnodes_h.append((Newnode,h))


def CheckPrereq(Course,Operator,ScheduledTerm):  # check if given Operator and term satisfies prereq
    Courseinfo=Dict[Course]
    if Courseinfo.prereqs==():
        return 1
    index=Scheduled_Terms.index(ScheduledTerm)
    Tempterms=Scheduled_Terms[0:index+1]
    Pres=Initial.union({C[0] for C in Operator if C[1] in Tempterms})
    for prereq in Courseinfo.prereqs:
        if set(prereq).issubset(Pres): # If one of the prerequists is subset return true
            return 1
    return 0

# getting the term status
def TermInfo(Operator):
    T_info = []
    for ScheduledTerm in Scheduled_Terms:
        nbrOfCredits = sum([C[2] for C in Operator if C[1] == ScheduledTerm and not IsCourseHigherRequirement(C[0])])
        if nbrOfCredits > 18:
            # few courses has to be removed
            Limit =  nbrOfCredits - 18
        elif nbrOfCredits < 12:
            # few courses can be taken which fills the limit
            Limit = nbrOfCredits - 12
        else:
            Limit = 0
        T_info.append([ScheduledTerm, nbrOfCredits, Limit]) # T_info : [term,nbrOdCredits,Limit]

    return T_info

# function to move the courses to the previous terms if term has enough credits left
def MovecourseToPreviousTerms(State,Operator,VisitedNodes):
    T_Info=TermInfo(Operator)
    Operatorcopy=copiedInstance(Operator)
    for Op in Operatorcopy:
        index=Scheduled_Terms.index(Op[1])
        Courseinfo=Dict[Op[0]]
        # if the course is offered in both fall and spring then step is one. if it is offered in just one term then step is 2
        step=3-len([t for t in Courseinfo.terms if t=='Spring' or t=='Fall'])
        if index-step<0:
            continue
        Credit=Op[2]

        Course=Op[0]
        if T_Info[index-step][1]+Credit<18:  # check if the stepped term after adding course is having credits less than 18
            if T_Info[index][1]-Credit>=12:   # check if after removing this course from the term if nbr of credits is greater than 12
                if CheckPrereq(Course,Operator,Scheduled_Terms[index-step]):
                    Newsche_Course=(Op[0],Scheduled_Terms[index-step],Op[2])
                    Operator.remove(Op)
                    Operator.add(Newsche_Course)
                    T_Info=TermInfo(Operator)

    if Operator==Operatorcopy:
        return 1
    VisitedNodes.append((State,Operator))
    return 0

# add random courses to satisfy minimum credit limit
def addRandomCourses(Operator,ScheduledTerm,credits):

    #for course in range(0,len(Dict)):
     #   CourseInfo = Dict(course)
    for course,CourseInfo in Dict.items():
        if CourseInfo.prereqs==():
            if course not in [Op[0] for Op in Operator]:
                newcourse=((course[0],course[1]),ScheduledTerm,int(CourseInfo.credits))
                Operator.add(newcourse)
                credits=credits+newcourse[2]
                if credits>=0:
                    return

course_scheduler(Dict,Goal,Initial)  # calling CourseScheduler Main function

