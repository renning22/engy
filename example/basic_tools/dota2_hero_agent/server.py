
import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dota2_heroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Load environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# Initialize ChatAnthropic
chat_model = ChatAnthropic(model="claude-3-5-sonnet-20240620", anthropic_api_key=ANTHROPIC_API_KEY)


# Hero model
class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    primary_attribute = db.Column(db.String(50))
    attack_type = db.Column(db.String(50))
    roles = db.Column(db.String(200))
    abilities = relationship('Ability', backref='hero', lazy=True)

class Ability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Scraper function
def scrape_hero_data():
    url = "https://www.dota2.com/heroes"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    heroes = [
        {'name': 'Anti-Mage', 'primary_attribute': 'Intelligence'},
        {'name': 'Axe', 'primary_attribute': 'Strength'},
        {'name': 'Bane', 'primary_attribute': 'Intelligence'},
        {'name': 'Beastmaster', 'primary_attribute': 'Strength'},
        {'name': 'Bloodseeker', 'primary_attribute': 'Agility'},
        {'name': 'Bounty Hunter', 'primary_attribute': 'Agility'},
        {'name': 'Bristleback', 'primary_attribute': 'Strength'},
        {'name': 'Broodmother', 'primary_attribute': 'Agility'},
        {'name': 'Centaur Warrunner', 'primary_attribute': 'Strength'},
        {'name': 'Chaos Knight', 'primary_attribute': 'Strength'},
        {'name': 'Chen', 'primary_attribute': 'Intelligence'},
        {'name': 'Clinkz', 'primary_attribute': 'Agility'},
        {'name': 'Crystal Maiden', 'primary_attribute': 'Intelligence'},
        {'name': 'Dark Seer', 'primary_attribute': 'Intelligence'},
        {'name': 'Dawnbreaker', 'primary_attribute': 'Strength'},
        {'name': 'Dazzle', 'primary_attribute': 'Intelligence'},
        {'name': 'Death Prophet', 'primary_attribute': 'Intelligence'},
        {'name': 'Disruptor', 'primary_attribute': 'Intelligence'},
        {'name': 'Dragon Knight', 'primary_attribute': 'Strength'},
        {'name': 'Drow Ranger', 'primary_attribute': 'Agility'},
        {'name': 'Earthshaker', 'primary_attribute': 'Strength'},
        {'name': 'Elder Titan', 'primary_attribute': 'Strength'},
        {'name': 'Ember Spirit', 'primary_attribute': 'Agility'},
        {'name': 'Enchantress', 'primary_attribute': 'Intelligence'},
        {'name': 'Enigma', 'primary_attribute': 'Intelligence'},
        {'name': 'Faceless Void', 'primary_attribute': 'Agility'},
        {'name': 'Grimstroke', 'primary_attribute': 'Intelligence'},
        {'name': 'Gyrocopter', 'primary_attribute': 'Agility'},
        {'name': 'Hoodwink', 'primary_attribute': 'Agility'},
        {'name': 'Huskar', 'primary_attribute': 'Strength'},
        {'name': 'Invoker', 'primary_attribute': 'Intelligence'},
        {'name': 'Io', 'primary_attribute': 'Strength'},
        {'name': 'Jakiro', 'primary_attribute': 'Intelligence'},
        {'name': 'Juggernaut', 'primary_attribute': 'Agility'},
        {'name': 'Keeper of the Light', 'primary_attribute': 'Intelligence'},
        {'name': 'Kunkka', 'primary_attribute': 'Strength'},
        {'name': 'Legion Commander', 'primary_attribute': 'Strength'},
        {'name': 'Leshrac', 'primary_attribute': 'Intelligence'},
        {'name': 'Lifestealer', 'primary_attribute': 'Strength'},
        {'name': 'Lina', 'primary_attribute': 'Intelligence'},
        {'name': 'Lion', 'primary_attribute': 'Intelligence'},
        {'name': 'Lone Druid', 'primary_attribute': 'Agility'},
        {'name': 'Luna', 'primary_attribute': 'Agility'},
        {'name': 'Lycan', 'primary_attribute': 'Strength'},
        {'name': 'Magnus', 'primary_attribute': 'Strength'},
        {'name': 'Marci', 'primary_attribute': 'Strength'},
        {'name': 'Mars', 'primary_attribute': 'Strength'},
        {'name': 'Medusa', 'primary_attribute': 'Agility'},
        {'name': 'Meepo', 'primary_attribute': 'Agility'},
        {'name': 'Mirana', 'primary_attribute': 'Agility'},
        {'name': 'Monkey King', 'primary_attribute': 'Agility'},
        {'name': 'Morphling', 'primary_attribute': 'Agility'},
        {'name': 'Naga Siren', 'primary_attribute': 'Strength'},
        {'name': 'Nature\'s Prophet', 'primary_attribute': 'Intelligence'},
        {'name': 'Necrophos', 'primary_attribute': 'Intelligence'},
        {'name': 'Night Stalker', 'primary_attribute': 'Strength'},
        {'name': 'Nyx Assassin', 'primary_attribute': 'Agility'},
        {'name': 'Ogre Magi', 'primary_attribute': 'Intelligence'},
        {'name': 'Omniknight', 'primary_attribute': 'Strength'},
        {'name': 'Orchid Malee', 'primary_attribute': 'Agility'},
    ]

    print(heroes)

    with app.app_context():
        for hero_data in heroes:
            existing_hero = Hero.query.filter_by(name=hero_data['name']).first()
            if not existing_hero:
                new_hero = Hero(name=hero_data['name'], primary_attribute=hero_data['primary_attribute'])
                db.session.add(new_hero)
        db.session.commit()


dota2_expert = Agent(
    role='Dota 2 Expert',
    goal='Provide accurate and helpful information about Dota 2 heroes',
    backstory='You are an AI assistant with extensive knowledge of Dota 2 heroes, their abilities, and gameplay mechanics.',
    allow_delegation=False,
    llm=chat_model
)

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# API routes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{'id': hero.id, 'name': hero.name, 'primary_attribute': hero.primary_attribute} for hero in heroes])

@app.route('/hero/<int:hero_id>', methods=['GET'])
def get_hero(hero_id):
    hero = Hero.query.get_or_404(hero_id)
    return jsonify({
        'id': hero.id,
        'name': hero.name,
        'primary_attribute': hero.primary_attribute,
        'attack_type': hero.attack_type,
        'roles': hero.roles,
        'abilities': [{'name': ability.name, 'description': ability.description} for ability in hero.abilities]
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    hero_id = data.get('hero_id')
    question = data.get('question')
    
    hero = Hero.query.get_or_404(hero_id)
    
    task = Task(
        description=f"Answer the following question about the Dota 2 hero {hero.name}: {question}",
        expected_output='Return in markdown format',
        agent=dota2_expert
    )
    
    crew = Crew(
        agents=[dota2_expert],
        tasks=[task]
    )
    
    result = crew.kickoff()
    
    return jsonify({'answer': str(result)})

@app.route('/update_heroes', methods=['POST'])
def update_heroes():
    scrape_hero_data()
    return jsonify({'message': 'Hero data updated successfully'})

if __name__ == '__main__':
    app.run(host='localhost', port=5557, debug=True)
