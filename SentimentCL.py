import requests,json,math,pprint
from ciscosparkapi import CiscoSparkAPI

def main():

    # Define Variables to store user's Webex token, the API key so that the engine will recognize and process the text
    # For the user, and the Sentiment API URL to call. here is also where the CiscoSparkAPI is invoked

    WEBEX_TOKEN=''
    API_KEY=''
    SENTIMENT_API_URL = 'http://api.havenondemand.com/1/api/sync/analyzesentiment/v2?apikey='+API_KEY
    api = CiscoSparkAPI(access_token=WEBEX_TOKEN)

    # The following Variables deal more with the temporary storing of information.
    # Limit serves as a break stop in case the chosen space has thousands of messages. Best to try with a small value
    # and increase depending on needs.
    # The variable 'i' is just an iterator used through the code. and 'c' is there as the continue variable, allowing
    # the user to digest the script in chunks and typing the next step's number to continue
    # the structures for analysis take the user's email as the primary key, so we have an emailsAndMessages structure,
    # and equally important a relationship between emails and scores and ranks

    limit=500
    i=1
    c=''
    emailsAndMessages={}
    emailsAndScores={}
    emailsAndRanks={}

    # Generate a list of spaces, excluding 1:1 spaces. hence the keyword type='group'
    rooms=list(api.rooms.list(type="group"))

    # Disclaimer
    print("- - - WebEx Teams Space Sentiment Analyzer Script - - - ")
    print("DISCLAIMER: Use at your own risk and on a test account!")
    print("Only execute script if you are aware of the following:")
    print("Message information WILL leave your WebEx Teams account and be shared outside your organization.\n")
    while c!="1": c=input("\nType '1' to accept and start with Step 1 (List your Spaces)...")
    print("\nStep 1: Gathering your Spaces. Sent an API request using your WebEx Teams Token and the response looks like this (first record): \n "+str(rooms[0]))
    while c!="2": c=input("\nType '2' to continue to Step 2 (Space selection)...")

    # This block goes space for space listing them and assigning a numeric value to the space, so user can easily choose
    print("\nThese are your Rooms: \n\n")
    for room in rooms:
        print(str(rooms.index(room))+": "+room.title)
    roomToAnalyze=input("\nEnter the Number of the Space you would like to Analyze for Sentiment: ")
    roomToAnalyzeId=rooms[int(roomToAnalyze)].id
    roomToAnalyzeTitle=rooms[int(roomToAnalyze)].title

    print("\nYour chosen room is: "+str(roomToAnalyzeTitle))
    while c!="3": c=input("\nType '3' to continue to Step 3 (Message history gathering for space "+roomToAnalyzeTitle+")...")

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

    while c!="4": c=input("\nType '4' to continue to step 4 (Space History Analysis)...")

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
    while c!="5": c=input("\n\nType '5' to continue to step 5 (Sentiment Ranking)...")

    print("\nThese are the Webex Team Members of \""+roomToAnalyzeTitle+"\" and their respective Sentiment: \n")

    for email in emailsAndScores:
        emailsAndRanks[email]=[math.ceil(emailsAndScores[email][0]['sentiment_analysis'][0]['aggregate']['score']*100),str(emailsAndScores[email][0]['sentiment_analysis'][0]['aggregate']['sentiment'])]

    for email,rank in sorted(emailsAndRanks.items(), key=lambda p:p[1],reverse=True):
        print(email+": ",str(rank[0])+"% "+rank[1]+", Message Count: "+ str(len(emailsAndMessages[email])))

if __name__ == '__main__':
    main()
