#
#           WEBEX TEAMS SENTIMENT ANALYZER
#           by: David Fernandez davidfe (at) cisco.com
#

import requests,json,math,pprint
from ciscosparkapi import CiscoSparkAPI

# 				VARIABLE DEFINITIONS
#
#	Define Variables to store user's Webex token, the API key so that the engine will recognize and process the text
# 	For the user, and the Sentiment API URL to call. here is also where the CiscoSparkAPI is invoked

WEBEX_TOKEN = ''
               # Enter your Webex Token (get it at http://developer.webex.com)

API_KEY = '2e5cc4cf-e029-4f9f-bd80-fa3f174190e6'
           # Enter your analyzer API Key as per the guide below:

#Pods 1-4 : '2e5cc4cf-e029-4f9f-bd80-fa3f174190e6'
#Pods 5-8 : '8a33d207-a8b3-4526-aedb-567bf86be114'

SENTIMENT_API_URL = 'http://api.havenondemand.com/1/api/sync/analyzesentiment/v2?apikey=' + API_KEY


def main():

    print("Connecting with your WebEx Teams token to the API...")
    api = CiscoSparkAPI(access_token=WEBEX_TOKEN)

    # The following Variables deal more with the temporary storing of information.
    # Limit serves as a break stop in case the chosen space has thousands of messages. Best to try with a small value
    # and increase depending on needs.

    # The variable 'i' is just an iterator used through the code. and 'c' is there as the continue variable, allowing
    # the user to digest the script in chunks and typing the next step's number to continue
    # the structures for analysis take the user's email as the primary key, so we have an emailsAndMessages structure,
    # and equally important a relationship between emails and scores and ranks

    limit=500               #Limits the number of iterations (How many messages back do you want to analyze?)
    i=1                     #Iterator that counts through the loops and exits if the limit is hit
    c=''                    #Character pressed by the user to continue (Step 1,2,3...)
    emailsAndMessages={}    #Structure that holds emails and all the messages said by that email
    emailsAndScores={}      #Structure that holds emails and the API response for that email (Sentiment Responses)
    emailsAndRanks={}       #Structure that holds the emails once sorted

    # Generate a list of spaces, excluding 1:1 spaces. hence the keyword type='group'
    rooms=list(api.rooms.list(type="group"))

    # Print Disclaimer and usage caution message
    print("- - - WebEx Teams Space Sentiment Analyzer Script - - - ")
    print("DISCLAIMER: Use at your own risk and on a test account!")
    print("Only execute script if you are aware of the following:")
    print("Message information WILL leave your WebEx Teams account and be shared outside your organization.\n")
    input("\nPress any key to accept and start with Step 1 (List your Spaces)...")

    # Start Gathering Spaces
    print("\nStep 1: Gathering your Spaces. Sent an API request using your WebEx Teams Token and "
          "the response looks like this (first record): \n "+str(rooms[0]))
    input("\nPress any key to continue to Step 2 (Space selection)...")

    # This block goes space for space listing them and assigning a numeric value to the space, so user can easily choose
    print("\nThese are your Rooms: \n\n")
    for room in rooms:
        print(str(rooms.index(room))+": "+room.title)
    roomToAnalyze=input("\nEnter the Number of the Space you would like to Analyze for Sentiment: ")
    roomToAnalyzeId=rooms[int(roomToAnalyze)].id
    roomToAnalyzeTitle=rooms[int(roomToAnalyze)].title

    print("\nYour chosen room is: "+str(roomToAnalyzeTitle))
    input("\nPress any key to continue to Step 3 (Message history gathering for space "+roomToAnalyzeTitle+")...")

    # Once space is identified, have the CiscosparkAPI fetch all messages for us, until a limit is reached!
    # then for every message, either start a list with the email and the first message, or append a message if
    # the email already exists in emailsAndMessages
    messageHistory=api.messages.list(roomId=roomToAnalyzeId)
    for message in messageHistory:
        if ( message.text and message.personEmail):
            if message.personEmail not in emailsAndMessages: emailsAndMessages[message.personEmail]=[message.text]
            else: emailsAndMessages[message.personEmail].append(message.text)
        if (i>=limit):break
        i+=1

    print("\nProcessed "+str(i-1)+" Messages.\n")

    print("\nSent API request to gather the space's messages. Here's a sample message: \n\n"+str(message))

    input("\nPress any key to continue to step 4 (Space History Analysis)...")

    # At this point we have a structure containing all of the emails and all of the messages for that email in a list.
    # next step is to create a fake 'file' which makes the upload to the API easier:
    # then we'll send that using requests, and then create a structure that will store the API response (sentiment score)
    # into a list called emailsAndScores.
    for email in emailsAndMessages:
        fakeFile = {'file': ('fakeFile.txt', str(emailsAndMessages[email]))}
        print("Analyzing member "+str(email)+"...")
        r = requests.post(SENTIMENT_API_URL,files=fakeFile)
        emailsAndScores[email]=[json.loads(r.text)]

    print("\nSent Message History from all space members to Sentiment Analysis API. \nHere is a sample response for "+email+": \n\n")
    pprint.pprint(emailsAndScores[email])
    input("\nPress any key to continue to step 5 (Sentiment Ranking)...")

    print("\nThese are the Webex Team Members of \""+roomToAnalyzeTitle+"\" and their respective Sentiment: \n")

    for email in emailsAndScores:
        emailsAndRanks[email]=[math.ceil(emailsAndScores[email][0]['sentiment_analysis'][0]['aggregate']['score']*100),
                               str(emailsAndScores[email][0]['sentiment_analysis'][0]['aggregate']['sentiment'])]

    for email,rank in sorted(emailsAndRanks.items(), key=lambda p:p[1],reverse=True):
        print(email+": ",str(rank[0])+"% "+rank[1]+", Message Count: "+ str(len(emailsAndMessages[email])))

    print("Done!")

if __name__ == '__main__':
    main()