from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import requests, json, time, sys

def Authorization():
    payload = {'username': 'kamilbot', 'appKey': '', 'secret': '', 'accessToken': '', 'accessTokenSecret': ''}
    headers = {'Content-Type': 'application/json'}
    login_url = 'https://lo.agentvep.liveperson.net/api/account/91200013/login??v=1&NC=true'
    r = requests.post(login_url, headers=headers, data=json.dumps(payload))
    parsed_json = json.loads(r.content)
    bearer = parsed_json['bearer']
    print "Auth bearer: ", bearer
    return bearer
            
def StartAgentSession(bearer):
    create_agent_session_url = 'https://lo.agentvep.liveperson.net/api/account/91200013/agentSession?v=1&NC=true'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + bearer}
    payload = {'loginData': ''}
    r = requests.post(create_agent_session_url, headers=headers, data=json.dumps(payload))
    parsed_json = json.loads(r.content)
    agent_session_id = parsed_json['agentSessionLocation']['link']['@href'].rsplit('/', 1)[-1]
    print "Agent Session ID: ", agent_session_id
    return agent_session_id

def TakeChat(agent_session_id, bearer):
    while True:
        take_chat_url = 'https://lo.agentvep.liveperson.net/api/account/91200013/agentSession/'+agent_session_id+'/incomingRequests?v=1&NC=true'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + bearer}
        payload = {'': ''}
        r = requests.post(take_chat_url, headers=headers, data=json.dumps(payload))
        parsed_json = json.loads(r.content)
        try:
            chat_id = parsed_json['chatLocation']['link']['@href'].rsplit('/', 1)[-1]
            print "Chat ID: ", chat_id
            return chat_id
            break
        except:
            print "No incoming chat session.."

bearer = Authorization()
agent_session_id = StartAgentSession(bearer)
chat_id = TakeChat(agent_session_id, bearer)

bot = ChatBot('Norman')
bot = ChatBot(
    'Norman',
    filters=["chatterbot.filters.RepetitiveResponseFilter"],
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    agent_session_id=agent_session_id,
    chat_id=chat_id,
    bearer=bearer,
    input_adapter='chatterbot.input.LivePerson',
    output_adapter='chatterbot.output.LivePerson',
    database='./database.sqlite3',
    logic_adapters=[
        {
            "import_path": "chatterbot.logic.BestMatch",
            "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
            "response_selection_method": "chatterbot.response_selection.get_most_frequent_response"
        }
    ],
)

bot.set_trainer(ChatterBotCorpusTrainer)
#bot.train("chatterbot.corpus.english")
#bot.set_trainer(ListTrainer)
        
#bot.train([
#    "do you know kamil sienicki?",
#    
#])

#print("Ready..")

# Get a response to the input text 'How are you?'
while True:
    try:
        response = bot.get_response(None)
    except:
        pass