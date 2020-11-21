# import urllib.request
# import base64

# theurl = 'https://boardgamearena.com/playernotif'
# theurl = 'https://boardgamearena.com'
# username = 'superlode'
# password = 'sl8afval'
# req = urllib.request.Request(theurl)

# credentials = ('%s:%s' % (username, password))
# encoded_credentials = base64.b64encode(credentials.encode('ascii'))
# req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))


# with urllib.request.urlopen(req) as response:
#     print(response.read())
# # with urllib.request.urlopen(req) as response, open(out_file_path, 'wb') as out_file:
# #     data = response.read()
# #     out_file.write(data)

import requests
import json

# https://github.com/tpq/bga/blob/master/py/bga.py

class Game:
    
    # Initialize a Game object from the html "logs" of a BGA game
    def __init__(self, tableID, email, password):
        self.tableID = str(tableID)
        self.roles = self.get(tableID, email, password)
        # self.turnorder = [role.player_name for role in self.roles]
        # self.roleorder = [role.rol_type for role in self.roles]
        
    # Parse the game into a list of "role blocks"
    def get(self, tableID, email, password):
        
        tableID = str(tableID)
        
        # Define parameters to access to Board Game Arena
        url_login = "http://en.boardgamearena.com/account/account/login.html"
        prm_login = {'email': email, 'password': password, 'rememberme': 'on',
                     'redirect': 'join', 'form_id': 'loginform'}
        url_game = "http://en.boardgamearena.com/gamereview?table=" + tableID
        url_log = "http://en.boardgamearena.com/archive/archive/logs.html"
        prm_log = {"table": tableID, "translated": "true"}
        
        with requests.session() as c:
            
            # Login to Board Game Arena
            r = c.post(url_login, params = prm_login)
            if r.status_code != 200:
                print("Error trying to login!")
            
            # Generate the log files
            r = c.get(url_game)
            if r.status_code != 200:
                print("Error trying to load the gamereview page!")
            
            # Retrieve the log files
            r = c.get(url_log, params = prm_log)
            print(url_log)
            if r.status_code != 200:
                print("Error trying to load the log file!")
            log = r.text
            
        # Save the requested log file
        self.request = log

        parsed = json.loads(log)
        print(json.dumps(parsed, indent=4, sort_keys=False))
        
    def table_data(self):
        self.request
        # # Index all role changes
        # index_role = []
        # loc = 0
        # while loc > -1:
        #     index_role.append(loc)
        #     loc = log.find("[\"rol_type_tr\"],\"player_name\"", loc + 1)
        
        # # Ignore the first "role block" as a superfluous header
        # # Organize remaining data into list of Role objects
        # roles = []
        # for i in range(1, len(index_role)):
        #     start = index_role[i]
        #     if(i == len(index_role) - 1):
        #         end = len(log) - 1     
        #     else:
        #         end = index_role[i + 1] - 1
        #     role_new = Role(log[start:end])
        #     roles.append(role_new)
        
        # # Return partitioned roles
        # return(roles)

if __name__ == "__main__":
    
    g = Game(124984142,"sun"+"setonalo"+"nelybea" + "ch"+"@"+"gma" + "il.com","w8"+  "w" + "oo" + "rd")