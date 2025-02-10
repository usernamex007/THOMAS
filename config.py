import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "28795512"))
API_HASH = os.getenv("API_HASH", "c17e4eb6d994c9892b8a8b6bfea4042a")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7983720117:AAGKo1TZaKNKXZMIzW_QOE7o_71_1gvlNrc")
SESSION_STRINGS = os.getenv("SESSION_STRINGS", "1ApWapzMAUEe4naqf3D3xf6-1e2xFaDCUreX14j0izDbRanzfKjNgbLpZA2EU-mBGJezJvUvjgjBTS2149gYg1EMebFVdqvhwd8HsOoTg42dUbJR5jeUCiMdaTj73RQA6Ynx2TVDUerkDcs-VorHtMiekZ17jrL4x9o6jB4Mrt5xWYLmXuRHMmLq3jRAe8u2SThu5UTc8zxF7K-Y6sYEpOn_j2uGj4hikaldZLWRfVG0400iN8nVhNXJ2-fhhrCEvKOBiYMVK0lFY7-_cglLoLItKoNeiyLkT04LXEfYxTvYL1Bjxy149rDzDMrSp5vYbPw6JcjefcxCkQwVW0siBYrM97ERtAdE=").split(",")  # Multiple Sessions Supported
