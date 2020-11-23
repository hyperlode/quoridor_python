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
import time
import bga_scraping_database_operations
import traceback

# https://github.com/tpq/bga/blob/master/py/bga.py

class BoardGameArenaScraper:
    
    # Initialize a Game object from the html "logs" of a BGA game
    def __init__(self, email, password):
        # self.tableID = str(tableID)
        # self.roles = self.get(tableID, email, password)
        # self.turnorder = [role.player_name for role in self.roles]
        # self.roleorder = [role.rol_type for role in self.roles]

        self.session = requests.session()

        # Login to Board Game Arena
        url_login = "http://en.boardgamearena.com/account/account/login.html"
        prm_login = {'email': email, 'password': password, 'rememberme': 'on',
                     'redirect': 'join', 'form_id': 'loginform'}

        r = self.session.post(url_login, params = prm_login)
        if r.status_code != 200:
            print("Error trying to login!")
    
    def close(self):
        self.session.close()

    def scrape_player_games_metadata_by_page(self, player_id, page):
        player_id = str(player_id)
        
        url_player_games = "https://boardgamearena.com/gamestats/gamestats/getGames.html?player={}&opponent_id=0&game_id=43&finished=1&page={}&updateStats=0&dojo.preventCache=1605921362257".format(
            player_id,
            page,
        )
        r = self.session.get(url_player_games)
        if r.status_code != 200:
            print("Error trying to load the games per player page!")

        return r.text

    def get_full_game(self, tableID):
        
        tableID = str(tableID)
        
        # Define parameters to access to Board Game Arena
       
       
        url_game = "http://en.boardgamearena.com/gamereview?table=" + tableID
        url_log = "http://en.boardgamearena.com/archive/archive/logs.html"
        prm_log = {"table": tableID, "translated": "true"}
            
        # Generate the log files
        r = self.session.get(url_game)
        if r.status_code != 200:
            print("Error trying to load the gamereview page!")
        
        # Retrieve the log files
        r = self.session.get(url_log, params = prm_log)
        if r.status_code != 200:
            print("Error trying to load the log file!")
        log = r.text

        return log     
        # # Save the requested log file
        # self.request = log

        # parsed = json.loads(log)
        # print(json.dumps(parsed, indent=4, sort_keys=False))
        
    # def table_data(self):
    #     self.request
       
    def scrape_player_games_metadata(self, player_id):

        start_t = time.time()
        previous_t = start_t


        db_path = r"C:\Data\Generated_program_data\boardgamearena_quoridor_scraper\bga_quoridor_data.db".format()
        db = bga_scraping_database_operations.BoardGameArenaDatabaseOperations(db_path)
    
        # for game in games_meta_data:
        #     print(game)

        ran_over_all_player_games = False
        page = 1

        while not ran_over_all_player_games:
            result_raw = self.scrape_player_games_metadata_by_page(player_id, page)
            result_parsed = self.parse_scraped_games_metadata(result_raw, player_id)
                
            for game in result_parsed:
                db.add_game_metadata(game["table_id"],game,False)

            if len(result_parsed) == 0:
                ran_over_all_player_games = True
            else:
                db.commit()
                page += 1

            print(" dt since start: {}, dt since previous:{}, at page: {})".format(
                time.time() - start_t,
                time.time() - previous_t,
                page,
                ))
            previous_t = time.time()

    def parse_scraped_games_metadata (self, raw, from_scraped_player_id):
        data_json = json.loads(raw)
        
        games = data_json["data"]["tables"]

        if len(games) == 0:
            # no data sent
            return []
        
        games_meta_data = []
        for game in games:
            game_meta_data = {}
            
            scores =  game["scores"].split(",")
            ranks =  game["ranks"].split(",")
            player_names =  game["player_names"].split(",")
            player_ids =  game["players"].split(",")

            # game_meta_data["table_id"] = int(game["table_id"])
            # game_meta_data["time_start"] = int(game["start"])
            # game_meta_data["time_end"] = int(game["end"])
            # game_meta_data["concede"] = int(game["concede"])
            # game_meta_data["unranked"] = int(game["unranked"])
            # game_meta_data["normalend"] = int(game["normalend"])
            # game_meta_data["player_1_id"] = int(player_ids[0])
            # game_meta_data["player_2_id"] = int(player_ids[1])
            # game_meta_data["player_1_name"] = player_names[0]
            # game_meta_data["player_2_name"] = player_names[1]
            # game_meta_data["player_1_score"] = int(scores[0])
            # game_meta_data["player_2_score"] = int(scores[1])
            # game_meta_data["player_1_rank"] = int(ranks[0])
            # game_meta_data["player_2_rank"] = int(ranks[0])
            # game_meta_data["elo_after"] = int(game["elo_after"])
            # game_meta_data["elo_win"] = int(game["elo_win"])
            # game_meta_data["player_id_scraped_player"] = from_scraped_player_id
            
            game_meta_data["table_id"] = (game["table_id"])
            game_meta_data["time_start"] = (game["start"])
            game_meta_data["time_end"] = (game["end"])
            game_meta_data["concede"] = (game["concede"])
            game_meta_data["unranked"] = (game["unranked"])
            game_meta_data["normalend"] = (game["normalend"])
            game_meta_data["player_1_id"] = (player_ids[0])
            game_meta_data["player_2_id"] = (player_ids[1])
            game_meta_data["player_1_name"] = player_names[0]
            game_meta_data["player_2_name"] = player_names[1]
            game_meta_data["player_1_score"] = (scores[0])
            game_meta_data["player_2_score"] = (scores[1])
            game_meta_data["player_1_rank"] = (ranks[0])
            game_meta_data["player_2_rank"] = (ranks[0])
            game_meta_data["elo_after"] = (game["elo_after"])
            game_meta_data["elo_win"] = (game["elo_win"])
            game_meta_data["player_id_scraped_player"] = str(from_scraped_player_id)

            games_meta_data.append(game_meta_data)
        return games_meta_data



if __name__ == "__main__":
    
    player_id_scraped_player = 84781397

    # if nothing sent (page 100): 
    # raw_games_meta_data = '''{"status":1,"data":{"tables":[],"stats":[]}}'''
    # raw_games_meta_data = '''{"status":1,"data":{"tables":[{"table_id":"122024753","game_name":"quoridor","game_id":"43","start":"1604690444","end":"1604690607","concede":"1","unranked":"0","normalend":"1","players":"84781397,88915338","player_names":"Mehrschad,Paco2000","scores":"0,0","ranks":"1,2","elo_win":"8","elo_after":"1578","arena_win":null,"arena_after":"1.1500"},{"table_id":"121839640","game_name":"quoridor","game_id":"43","start":"1604609605","end":"1604609943","concede":"1","unranked":"0","normalend":"1","players":"84201182,84781397","player_names":"SDFSDF,Mehrschad","scores":"0,0","ranks":"1,2","elo_win":"-5","elo_after":"1570","arena_win":null,"arena_after":"1.1500"},{"table_id":"121820186","game_name":"quoridor","game_id":"43","start":"1604609180","end":"1604609578","concede":"0","unranked":"0","normalend":"1","players":"84201182,84781397","player_names":"SDFSDF,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-5","elo_after":"1575","arena_win":null,"arena_after":"1.1500"},{"table_id":"121799917","game_name":"quoridor","game_id":"43","start":"1604602259","end":"1604602476","concede":"0","unranked":"0","normalend":"1","players":"84105726,84781397","player_names":"zila78,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-5","elo_after":"1579","arena_win":null,"arena_after":"1.1500"},{"table_id":"121796306","game_name":"quoridor","game_id":"43","start":"1604601927","end":"1604602243","concede":"0","unranked":"0","normalend":"1","players":"84105726,84781397","player_names":"zila78,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-5","elo_after":"1584","arena_win":null,"arena_after":"1.1500"},{"table_id":"121796394","game_name":"quoridor","game_id":"43","start":"1604601595","end":"1604601910","concede":"0","unranked":"0","normalend":"1","players":"84105726,84781397","player_names":"zila78,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-5","elo_after":"1589","arena_win":null,"arena_after":"1.1500"},{"table_id":"121799193","game_name":"quoridor","game_id":"43","start":"1604601313","end":"1604601578","concede":"0","unranked":"0","normalend":"1","players":"84105726,84781397","player_names":"zila78,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-5","elo_after":"1594","arena_win":null,"arena_after":"1.1500"},{"table_id":"121724379","game_name":"quoridor","game_id":"43","start":"1604579488","end":"1604579780","concede":"1","unranked":"0","normalend":"1","players":"87795080,84781397","player_names":"Godalec,Mehrschad","scores":"0,0","ranks":"1,2","elo_win":"-4","elo_after":"1599","arena_win":null,"arena_after":"1.1500"},{"table_id":"121725509","game_name":"quoridor","game_id":"43","start":"1604579205","end":"1604579460","concede":"0","unranked":"0","normalend":"1","players":"87795080,84781397","player_names":"Godalec,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-4","elo_after":"1603","arena_win":null,"arena_after":"1.1500"},{"table_id":"121723248","game_name":"quoridor","game_id":"43","start":"1604578952","end":"1604579188","concede":"0","unranked":"0","normalend":"1","players":"87795080,84781397","player_names":"Godalec,Mehrschad","scores":"1,0","ranks":"1,2","elo_win":"-4","elo_after":"1607","arena_win":null,"arena_after":"1.1500"}],"stats":[]}}'''
    # games_meta_data = parse_scraped_games_metadata(raw_games_meta_data, player_id_scraped_player)
    
    
    # exit()
    
    try:
        
       
        # init (log in )
        g = BoardGameArenaScraper("sun"+"setonalo"+"nelybea" + "ch"+"@"+"gma" + "il.com","w8"+  "w" + "oo" + "rd")

        # print("logged in at {}".format(
        #     start_t,
        #     ))


        # raw_game_data = g.get_full_game(124984142)
        # print(raw_game_data)
        g.scrape_player_games_metadata(player_id_scraped_player)
        # games_meta_data = g.get_player_games(player_id_scraped_player)
        # print(games_meta_data)
        
        # print("retrieve 1 dt = {}".format(
        #     time.time() -start_t,
        # ))
      
        # raw_game_data = g.get_full_game(125651498)

        # print("retrieve 2 dt = {}".format(
        #     time.time() -start_t,
        # ))
        # {"status":1,"data":{"status":1,"data":{"valid":1,"data":[{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"1","packet_type":"resend","move_id":"1","time":"1605705114","data":[{"uid":"5fb51d9a01462","type":"gameStateChange","log":"","args":{"name":"gameSetup","description":"Game setup","type":"manager","action":"stGameSetup","transitions":{"":10},"active_player":88772103,"args":null,"reflexion":{"total":{"88772103":null,"87795080":null}}}}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"2","packet_type":"resend","move_id":"2","time":"1605705138","data":[{"uid":"5fb51db254d8d","type":"gameStateChange","log":"","args":{"id":10,"active_player":"88772103","args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"108","87795080":"108"}}},"h":"24be45"}]},{"channel":"\/player\/p87795080","table_id":"124984142","packet_id":"3","packet_type":"resend","move_id":"3","time":"1605705151","data":[{"uid":"5fb51dbfeb0c8","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"1":0},"6":{"1":0},"5":{"2":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"8c2bce76-2499-4ed1-8599-64da99bb82f1","h":"573b63"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"4","packet_type":"resend","move_id":"3","time":"1605705151","data":[{"uid":"5fb51dbfea5c9","type":"playToken","log":"${player_name} moves his pawn","args":{"player_id":"88772103","player_name":"leldabest","x":"5","y":"8","quoridorstrats_notation":"e2"},"h":"573b63"},{"uid":"5fb51dbfeac8d","type":"gameStateChange","log":"","args":{"id":11,"active_player":"88772103","args":null,"type":"game","reflexion":{"total":{"88772103":96,"87795080":"108"}},"updateGameProgression":0}},{"uid":"5fb51dbfeb170","type":"updateReflexionTime","log":"","args":{"player_id":87795080,"delta":"16","max":"108"}},{"uid":"5fb51dbfeba39","type":"gameStateChange","log":"","args":{"id":10,"active_player":87795080,"args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"96","87795080":"108"}}},"lock_uuid":"8c2bce76-2499-4ed1-8599-64da99bb82f1"}]},{"channel":"\/player\/p88772103","table_id":"124984142","packet_id":"5","packet_type":"resend","move_id":"4","time":"1605705160","data":[{"uid":"5fb51dc8a78f4","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"8":0},"6":{"8":0},"5":{"7":0,"9":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"d3e09b20-34dc-40e4-8f84-a1514aa7e263","h":"48c0d8"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"6","packet_type":"resend","move_id":"4","time":"1605705160","data":[{"uid":"5fb51dc8a7388","type":"playToken","log":"${player_name} moves his pawn","args":{"player_id":"87795080","player_name":"Godalec","x":"5","y":"2","quoridorstrats_notation":"e8"},"h":"48c0d8"},{"uid":"5fb51dc8a76ad","type":"gameStateChange","log":"","args":{"id":11,"active_player":"87795080","args":null,"type":"game","reflexion":{"total":{"88772103":"96","87795080":100}},"updateGameProgression":5}},{"uid":"5fb51dc8a795d","type":"updateReflexionTime","log":"","args":{"player_id":88772103,"delta":"16","max":"108"}},{"uid":"5fb51dc8a7ded","type":"gameStateChange","log":"","args":{"id":10,"active_player":88772103,"args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"108","87795080":"100"}}},"lock_uuid":"d3e09b20-34dc-40e4-8f84-a1514aa7e263"}]},{"channel":"\/player\/p87795080","table_id":"124984142","packet_id":"7","packet_type":"resend","move_id":"5","time":"1605705163","data":[{"uid":"5fb51dcb93d08","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"2":0},"6":{"2":0},"5":{"1":0,"3":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"3b865c4a-1b10-4149-85e4-580aa1dd9d3e","h":"95fc5c"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"8","packet_type":"resend","move_id":"5","time":"1605705163","data":[{"uid":"5fb51dcb937b2","type":"playToken","log":"${player_name} moves his pawn","args":{"player_id":"88772103","player_name":"leldabest","x":"5","y":"7","quoridorstrats_notation":"e3"},"h":"95fc5c"},{"uid":"5fb51dcb93af9","type":"gameStateChange","log":"","args":{"id":11,"active_player":"88772103","args":null,"type":"game","reflexion":{"total":{"88772103":106,"87795080":"100"}},"updateGameProgression":10}},{"uid":"5fb51dcb93d64","type":"updateReflexionTime","log":"","args":{"player_id":87795080,"delta":"16","max":"108"}},{"uid":"5fb51dcb94233","type":"gameStateChange","log":"","args":{"id":10,"active_player":87795080,"args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"106","87795080":"108"}}},"lock_uuid":"3b865c4a-1b10-4149-85e4-580aa1dd9d3e"}]},{"channel":"\/player\/p88772103","table_id":"124984142","packet_id":"9","packet_type":"resend","move_id":"6","time":"1605705176","data":[{"uid":"5fb51dd8df7e2","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"7":0},"6":{"7":0},"5":{"6":0,"8":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"76d86d8b-6204-4fad-8069-b629925731e0","h":"d300ab"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"10","packet_type":"resend","move_id":"6","time":"1605705176","data":[{"uid":"5fb51dd8df2e0","type":"playToken","log":"${player_name} moves his pawn","args":{"player_id":"87795080","player_name":"Godalec","x":"5","y":"3","quoridorstrats_notation":"e7"},"h":"d300ab"},{"uid":"5fb51dd8df5e8","type":"gameStateChange","log":"","args":{"id":11,"active_player":"87795080","args":null,"type":"game","reflexion":{"total":{"88772103":"106","87795080":96}},"updateGameProgression":15}},{"uid":"5fb51dd8df83b","type":"updateReflexionTime","log":"","args":{"player_id":88772103,"delta":"16","max":"108"}},{"uid":"5fb51dd8dfda0","type":"gameStateChange","log":"","args":{"id":10,"active_player":88772103,"args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"108","87795080":"96"}}},"lock_uuid":"76d86d8b-6204-4fad-8069-b629925731e0"}]},{"channel":"\/player\/p87795080","table_id":"124984142","packet_id":"11","packet_type":"resend","move_id":"7","time":"1605705179","data":[{"uid":"5fb51ddb24eb5","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"3":0},"6":{"3":0},"5":{"2":0,"4":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"dc9200db-2aee-4525-865a-bf407f871a06","h":"311012"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"12","packet_type":"resend","move_id":"7","time":"1605705179","data":[{"uid":"5fb51ddb24879","type":"playToken","log":"${player_name} moves his pawn","args":{"player_id":"88772103","player_name":"leldabest","x":"5","y":"6","quoridorstrats_notation":"e4"},"h":"311012"},{"uid":"5fb51ddb24c75","type":"gameStateChange","log":"","args":{"id":11,"active_player":"88772103","args":null,"type":"game","reflexion":{"total":{"88772103":106,"87795080":"96"}},"updateGameProgression":20}},{"uid":"5fb51ddb24f15","type":"updateReflexionTime","log":"","args":{"player_id":87795080,"delta":"16","max":"108"}},{"uid":"5fb51ddb253c9","type":"gameStateChange","log":"","args":{"id":10,"active_player":87795080,"args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"106","87795080":"108"}}},"lock_uuid":"dc9200db-2aee-4525-865a-bf407f871a06"}]},{"channel":"\/player\/p88772103","table_id":"124984142","packet_id":"13","packet_type":"resend","move_id":"8","time":"1605705198","data":[{"uid":"5fb51dee1924e","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"6":0},"6":{"6":0},"5":{"5":0,"7":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"4d285254-bab4-4eef-8e90-98b2e70cbbe6","h":"735408"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"14","packet_type":"resend","move_id":"8","time":"1605705198","data":[{"uid":"5fb51dee18d38","type":"playToken","log":"${player_name} moves his pawn","args":{"player_id":"87795080","player_name":"Godalec","x":"5","y":"4","quoridorstrats_notation":"e6"},"h":"735408"},{"uid":"5fb51dee19039","type":"gameStateChange","log":"","args":{"id":11,"active_player":"87795080","args":null,"type":"game","reflexion":{"total":{"88772103":"106","87795080":90}},"updateGameProgression":25}},{"uid":"5fb51dee192ac","type":"updateReflexionTime","log":"","args":{"player_id":88772103,"delta":"16","max":"108"}},{"uid":"5fb51dee19723","type":"gameStateChange","log":"","args":{"id":10,"active_player":88772103,"args":{"impossibleWallPlacements":[]},"type":"activeplayer","reflexion":{"total":{"88772103":"108","87795080":"90"}}},"lock_uuid":"4d285254-bab4-4eef-8e90-98b2e70cbbe6"}]},{"channel":"\/player\/p87795080","table_id":"124984142","packet_id":"15","packet_type":"resend","move_id":"9","time":"1605705203","data":[{"uid":"5fb51df397e09","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"4":0},"6":{"4":0},"5":{"3":0,"5":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"b17e1887-1f2a-4a1a-8543-7ff6fdb5176f","h":"7a3824"}]},{"channel":"\/table\/t124984142","table_id":"124984142","packet_id":"16","packet_type":"resend","move_id":"9","time":"1605705203","data":[{"uid":"5fb51df3977b7","type":"playWall","log":"${player_name} places a fence","args":{"player_id":"88772103","player_name":"leldabest","x":"5","y":"6","orientation":"horizontal","counters":{"wallcount_p87795080":{"counter_name":"wallcount_p87795080","counter_value":"10"},"wallcount_p88772103":{"counter_name":"wallcount_p88772103","counter_value":"9"}},"quoridorstrats_notation":"e3h"},"h":"7a3824"},{"uid":"5fb51df397b2e","type":"gameStateChange","log":"","args":{"id":11,"active_player":"88772103","args":null,"type":"game","reflexion":{"total":{"88772103":104,"87795080":"90"}},"updateGameProgression":30}},{"uid":"5fb51df397e82","type":"updateReflexionTime","log":"","args":{"player_id":87795080,"delta":"16","max":"108"}},{"uid":"5fb51df3983e2","type":"gameStateChange","log":"","args":{"id":10,"active_player":87795080,"args":{"impossibleWallPlacements":{"5_6_horizontal":1,"4_6_horizontal":2,"6_6_horizontal":2,"5_6_vertical":3}},"type":"activeplayer","reflexion":{"total":{"88772103":"104","87795080":"106"}}},"lock_uuid":"b17e1887-1f2a-4a1a-8543-7ff6fdb5176f"}]},{"channel":"\/player\/p88772103","table_id":"124984142","packet_id":"17","packet_type":"resend","move_id":"10","time":"1605705214","data":[{"uid":"5fb51dfef20af","type":"updateMoves","log":"","args":{"possibleTokenMoves":{"4":{"6":0},"6":{"6":0},"5":{"5":0}},"canPlayWall":true},"synchro":2,"lock_uuid":"e6e0ece0

    except Exception as e:
        print(e)
        print(traceback.format_exc())
    
    finally:
        g.close()