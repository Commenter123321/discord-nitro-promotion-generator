# Discord Promotion Generator
## WARNING: THIS TOOL IS FOR EDUCATIONAL PURPOSES ONLY. USE WITH CAUTION!

**How does this work?**
- watch [No Text To Speech's video](https://www.youtube.com/watch?v=yWqqMp6ca30) and you will understand
- basically Opera GX has partnered with Discord and is giving out free nitro promotion links if you visit [this link](https://www.opera.com/gx/discord-nitro) in their browser

### Setting this up
1. install python if you haven't already
2. clone the repository with `git clone https://github.com/Commenter123321/discord-nitro-promotion-generator.git` (or download it and unzip)
3. run `python -m pip install -r requirements.txt` to install the libraries required to run this program
4. create a copy of the file `.example.env` named `.env`
5. set the `WEBHOOK_URL` field in `.env` to a discord webhook
6. configure other things in `.env` if needed
7. run the program with `python main.py`