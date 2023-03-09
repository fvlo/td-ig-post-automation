from flask import Flask, request
from flask_restful import Resource, Api

from ig_carousel_via_latelysocial import post_to_ig
import pandas as pd
import time
from datetime import datetime
from sys import exit
import os
from random import randint


app = Flask(__name__)
api = Api(app)

class Poster(Resource):
    def get(self):
        # Get posting instructions from google sheets.
        sheet_url = "https://docs.google.com/spreadsheets/d/1b3KojEnGWyRxAz1lMcPjani2SfGRg3nlkDGPglfPxjI/edit#gid=0"
        url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
        instructions = pd.read_csv(url)
        instructions

        # Identify correct row of instructions. If =! 1 throw error and exit.
        todays_date = str(datetime.date(datetime.now()))
        index_to_post = instructions.index[instructions['Date'] == todays_date].tolist()
        if len(index_to_post) == 1:
            index_to_post = index_to_post[0]
        elif len(index_to_post) == 0:
            print("ERROR - No posts found for today's date.")
            exit()
        else:
            print("ERROR - More than one post found for today's date.")
            exit()

        # Set instructions for post
        caption_to_post = instructions.loc[index_to_post, "Caption_full"].replace('\n', '')
        category_to_post = instructions.loc[index_to_post, "Category"].replace('\n', '')
        question_to_post = instructions.loc[index_to_post, "Question"].replace('\n', '')
        answer_to_post = instructions.loc[index_to_post, "Answer"].replace('\n', '')
        image_content_to_post = [category_to_post, question_to_post, answer_to_post]

        # Sleep max 2 min
        time.sleep(randint(0,120))
        
        # Post to ig using imported function
        post_to_ig(image_content_to_post, caption_to_post)
        
        return { 'status_code': 200, 'text': 'Done.' }


api.add_resource(Poster, '/')

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')