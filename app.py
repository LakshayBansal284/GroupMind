from flask import Flask, render_template, request, jsonify
import praw
import math
import openai

# Flask app initialization
app = Flask(__name__)

# Reddit API credentials
client_id = 'YOUR_CLIENT_ID'  # Replace with your Reddit API client_id
client_secret = 'YOUR_CLIENT_SECRET'  # Replace with your Reddit API client_secret
user_agent = 'YOUR_USER_AGENT'  # Replace with your Reddit user_agent
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your OpenAI API key

# Initialize PRAW (Reddit API)
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

# Function to summarize text using OpenAI's GPT
def summarize_text(text, max_length=200):
    try:
        prompt = f"Summarize the following text in less than {max_length} words:\n{text}"
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can change this based on your model choice
            prompt=prompt,
            max_tokens=max_length,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return text[:max_length]  # Return first part of the text if there's an error

# Function to get top comments for a post
def get_top_comments(post, top_percentage=0.2):
    try:
        post.comments.replace_more(limit=0)
        all_comments = post.comments.list()
        if not all_comments:
            return []

        top_n = math.ceil(len(all_comments) * top_percentage)
        sorted_comments = sorted(all_comments, key=lambda x: x.score, reverse=True)
        top_comments = [comment.body for comment in sorted_comments[:top_n]]
        return top_comments
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

# Function to get top posts from a subreddit
def get_top_posts(subreddit_name, limit=10):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.top(limit=limit):
            post_data = {
                'title': post.title,
                'summary': summarize_text(post.selftext),
                'comments': get_top_comments(post)
            }
            posts.append(post_data)
        return posts
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []

# Flask route to render homepage
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle subreddit analysis
@app.route('/analyze', methods=['POST'])
def analyze_subreddit():
    subreddit_name = request.json.get('subreddit_name')
    if not subreddit_name:
        return jsonify({"error": "Subreddit name is required"}), 400

    subreddit_data = get_top_posts(subreddit_name)

    if not subreddit_data:
        return jsonify({"error": "No data available for this subreddit"}), 404

    return jsonify(subreddit_data)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
