from flask import Flask
from models import setup_db, Person, Objective, Requirement


app = Flask(__name__)
setup_db(app)


user1 = Person('Mustermann', 'Max')
user1.insert()

user2 = Person('Li', 'Ali')
user2.insert()

user3 = Person('Mendez', 'Maria', True)
user3.insert()


objective11 = Objective('Be a good husband', user1.id)
objective12 = Objective('Be a good employee', user1.id)
objective11.insert()
objective12.insert()

objective21 = Objective('Be a good investor', user2.id)
objective21.insert()

objective31 = Objective('Be a good boss', user3.id)
objective31.insert()


requirement111 = Requirement('Take out trash', objective11.id)
requirement112 = Requirement('Buy flowers', objective11.id)
requirement113 = Requirement('Say something nice each day', objective11.id)
requirement111.insert()
requirement112.insert()
requirement113.insert()



requirement121 = Requirement('Go to work', objective12.id)
requirement122 = Requirement('Finish presentation', objective12.id)
requirement123 = Requirement('Go to work', objective12.id)
requirement121.insert()
requirement122.insert()
requirement123.insert()



requirement211 = Requirement('Make money each day', objective21.id)
requirement212 = Requirement('Do not blow up', objective21.id)
requirement211.insert()
requirement212.insert()


requirement311 = Requirement('Keep company alive', objective31.id)
requirement312 = Requirement('Be nice to employees', objective31.id)
requirement311.insert()
requirement312.insert()