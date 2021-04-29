from nltk.corpus import words as wo
import random
class TicTacToe:
    def __init__(self, player1, player2):
        self.start = {"a1": " ", "b1": " ", "c1": " ",
                      "a2": " ", "b2": " ", "c2": " ",
                      "a3": " ", "b3": " ", "c3": " "}
        self.win = [
            ["a1", "a2", "a3"], ["b1", "b2", "b3"], ["c1", "c2", "c3"],
            ["a1", "b1", "c1"], ["a2", "b2", "c2"], ["a3", "b3", "c3"],
            ["a1", "b2", "c3"], ["a3", "b2", "c1"]
        ]
        
        self.player = "x"

        self.players = {"x": player1, "o": player2}

    def winner(self):
        winn = None
        for win in self.win:
            state = [self.start[win[0]], self.start[win[1]], self.start[win[2]]]
            if state[0] == state[1] and state[1] == state[2] and state[0] != " ":
                winn = self.players[state[0]]
        return winn

    def draw(self):
        for keys in list(self.start.keys()):
            if self.start[keys] == " ":
                return False
        return True
            
    def turn(self, player):
        if player == "x":
            new_player = "o"
        elif player == "o":
            new_player = "x"
        return new_player
    
    def game(self, move):
        if self.start[move] == "x" or self.start[move] == "o":
            return False
        elif self.start[move] != "x" or self.start[move] != "o":
            self.start[move] = self.player
            return True
            
class HangMan:
    def __init__(self):
        #self.words = ["word", 'aawwaa', "absurd", "affix", "bagpipes", "awkward", "bandwagon", "blizzard", "cobweb", "jelly", "zombie", "zipper", "wizard", "wave", "unzip", "quartz", "lucky", "luxury", "lymph", "oxygen", "pixel", "puppy", "yachtsman", "vaporize", "transplant", "strengths", "unknown", "subway"]
        self.words = wo.words()
        self.hang = {
                             'hanger' : "|",
                             'head' : "(^•^)",
                             'body' :     "|",
                             "left_hand" : "\\",
                             "right_hand" : "/",
                             "left_leg" : "/",
                             "right_leg" : "\\"
        }
        self.hang_word = ""
        self.word = ""
        self.person = {}
        self.remove_word = []
    
    def restart(self):
        self.hang_word = ""
        self.person = {
                                'hanger' : " ",
                                'head': ' ',
                                "body": " ",
                                "left_hand" : " ",
                                "right_hand" : " ",
                                "left_leg" : " ",
                                "right_leg": " "
        }
        self.remove_word = []
        
    
    def start(self):
        self.word = random.choice(self.words)
        self.person = {
                                'hanger': ' ',
                                'head': ' ',
                                "body": " ",
                                "left_hand" : " ",
                                "right_hand" : " ",
                                "left_leg" : " ",
                                "right_leg": " "
        }
        word = self.word.strip()
        word_list = []
        for w in word:
            word_list.append(w)
        remove_list = word_list
        remove_word = []
        word_list = word_list
        
        if len(word) <5:
            while len(remove_word) < 1:
                c = random.choice(remove_list)
                remove_word.append(c)
                remove_list.remove(c)
                
                
        elif len(word) <8:
            while len(remove_word) < 2:
                c = random.choice(remove_list)
                remove_word.append(c)
                remove_list.remove(c)
                
                
        elif len(word) <11:
            while len(remove_word) < 3:
                c = random.choice(remove_list)
                remove_word.append(c)
                remove_list.remove(c)
                
        for i in remove_word:
            if not i in self.remove_word:
                self.remove_word.append(i)
          
        word_list = []
        for w in word:
            word_list.append(w)
        hang_word_list = word_list

        for r in self.remove_word:
            i = 0
            for words in hang_word_list:
                if words == r:
                    word_list.pop(i)
                    word_list.insert(i, "_")
                i += 1
        for words in hang_word_list:
            self.hang_word += words
        return self.hang_word
            
    def guess(self, message):
        word = self.word.strip()
        hang_word = self.hang_word.strip()
        word_list = []
        hang_word_list = []
        for w in word:
            word_list.append(w)
        for w in hang_word:
            hang_word_list.append(w)
        if message in self.remove_word:
            i = 0
            for r in word_list:
                if r == message:
                    for l in hang_word_list:
                        if l == "_":
                            hang_word_list.pop(i)
                            hang_word_list.insert(i, message)
                i += 1
        else:
            for parts in self.person.keys():
                if self.hang[parts] != self.person[parts]:
                    self.person[parts] = self.hang[parts]
                    break
        self.hang_word = ""
        for words in hang_word_list:
            self.hang_word += words
        return self.hang_word
        
    def ans(self):
        if self.hang_word == self.word:
            self.restart()
            self.start()
            return "Won"
        elif self.person == self.hang:
            return "Lose"
