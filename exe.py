import Tier_Pull
import Tier_Analysis
import Tier_Metrics
import time

global path

path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"


def initial_questions():
    """
    Some initial criteria to make sure that the program will run:
    """


    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    while True:
        print('Answer [yes/no] for some initial criteria to run the program...\n')
        try:
            file_pointing = (input("Have you made sure that the file is pointing at the correct location?\n"))
        except ValueError:
            print("Sorry, I didn't understand that.\n")
            continue
        else:
            if file_pointing in yes:
                try:
                    initializing_match_up = (input("Does the first date and time from the Alpha and MI reports match\n"
                                                   "up with the first date and time from the LP manager tier\n"
                                                   "change document?\n"))
                except ValueError:
                    print("Sorry, I didn't understand that.\n")
                    continue
                else:
                    if initializing_match_up in yes:
                        print('Well done, running program. Will take around 20 mins, go and make a cup of tea,\n'
                              'put your feet up, and wait for this whole thing to blow over...')
                        return 1
                    elif initializing_match_up in no:
                        print('Make sure you are looking at the correct time periods. The Alpha\n'
                              'and MI reports needto have the start period running from the same\n '
                              'time as the tier changes otherwise there are issues with how the\n'
                              'information from the first tier is found. Correct and rerun exe.py\n')
                        break
                    else:
                        print("Please respond with 'yes' or 'no'...\n")
            elif file_pointing in no:
                print('Repoint file at correct path and rerun exe.py\n')
                break
            else:
                print("Please respond with 'yes' or 'no'...\n")


def main():

    if initial_questions() == 1:
        start_time_X = time.clock()
        Tier_Pull.main()
        Tier_Analysis.main()
        Tier_Metrics.main()
        print('Exe,', time.clock() - start_time_X, "seconds")


if __name__ == '__main__':
    main()

"""
Known Bugs/Quirks - 

1) Query from KDB is producing identical data for single ticket and sweepable tiers in some cases because 
   not differentiated
2) Need to have initial tier correctly matched so can compare from initial tier
3) Should put in a rule about if rejection rate is 100% then skip to the row before


"""