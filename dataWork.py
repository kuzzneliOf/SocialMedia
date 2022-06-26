import random
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
import sqlite3
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class Data:
    def print_data(self):
        username = db.Column(db.String(20), nullable=False, unique=True)

        # Create your connection
        self.cnx = sqlite3.connect('database.db')

        df1 = pd.read_sql_query(
            "SELECT friends.id, friends.user1, friends.user2, user.username FROM friends INNER JOIN user ON user.id=friends.user1",
            self.cnx)
        df2 = pd.read_sql_query("SELECT user.id, user.username FROM user", self.cnx)

        self.users = []
        table = pd.DataFrame.to_dict(df2)
        self.G = nx.Graph()
        for i in table['id']:
            self.G.add_node(table['id'][i])
            self.users.append(UserFriend(table['id'][i], table['username'][i]))
        self.edges = pd.DataFrame.to_dict(df1)
        for i in self.edges['user1']:
            self.G.add_edge(self.edges['user1'][i], self.edges['user2'][i])

        nx.draw(self.G)

        plt.show()

    def get_user_friends(self, id):
        ids = list(self.G.neighbors(id))
        userFriends = [self.find_user(i) for i in ids]
        return userFriends

    def find_user(self, id):
        for i in self.users:
            if i.id == id:
                return i
        return None

    def get_user_friends_recommendations(self, id):
        recomm = []
        queue = []
        visited = []
        queue.append(id)
        visited.append(id)
        visited.extend(list(self.G.neighbors(id)))
        while len(recomm) < 5:
            if queue == []:
                break
            curr = queue.pop(0)
            if curr in visited:
                neigh = list(self.G.neighbors(id))
                for i in neigh:
                    if not i in visited:
                        queue.append(i)
            else:
                visited.append(curr)
                recomm.append(curr)

        if len(recomm) < 5:
            while len(self.G.nodes) != len(visited) and len(recomm) != len(visited) and len(recomm) < 5:
                nodes = self.G.nodes
                uniq_nodes = [i for i in nodes if not i in visited]
                ch = random.choice(uniq_nodes)
                recomm.append(ch)
                visited.append(ch)
        recommend_users = []
        print(recomm)
        for i in recomm:
            recommend_users.append(self.find_user(i))
        return recommend_users

    def get_last(self):
        max = 0
        for i in self.edges['id']:
            if max < self.edges['id'][i]:
                max = self.edges['id'][i]
        return max


class UserFriend:
    def __init__(self, id, username):
        self.id = id
        self.username = username
