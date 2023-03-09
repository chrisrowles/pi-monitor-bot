# pi-monitor-discord

Discord integration to work with [pi-monitor-api](https://github.com/chrisrowles/pi-monitor-api).

![image](https://i.imgur.com/csAnczi.png)

## Requirements

- Python 3
- Discord account

Before you begin, you'll need to get the [API](https://github.com/chrisrowles/pi-monitor-api). up and running, follow the instructions over there for more details.

## Setup

1. Clone this repository
  ```sh
  git clone git@github.com:chrisrowles/pi-monitor-discord.git
  ```

2. Create a new virtualenv and activate it:
  ```sh
  python -m venv /path/to/new/venv
  ```

  ```sh
  source <venv>/bin/activate
  ```

3. Install dependencies
  ```sh
  pip install -r requirements.txt
  ``` 

4. Copy `.env` to `.env.example` and fill out your environment variables (they are all documented)
  ```sh
  cp .env .env.example
  ```

5. Run the bot
  ```sh
  python bot.py
  ```

  ```
  (pi-monitor-discord) chris ~/workspace/pi-monitord (main) λ python bot.py 
  2023-03-09 10:36:27 INFO     discord.client logging in using static token
  2023-03-09 10:36:28 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: ...)
  ```

![image](https://i.imgur.com/hi2CC1R.png)


