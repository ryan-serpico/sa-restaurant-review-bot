![Github banner](img/banner.png)

## Summary

Every six months the San Antonio Express-News does a roundup of the worst restaurant inspection reports from the [Metropolitan Health District](https://www.sanantonio.gov/Health). You can see past stories [here](https://www.expressnews.com/news/local/article/worst-San-Antonio-restaurant-inspections-16785545.php) and [here](https://www.expressnews.com/news/local/article/worst-restaurant-inspections-first-half-2022-17291150.php).

This bot automates the process of story creation.

## How it works in plain english

1. The bot loads [Metro Health's page with weekly inspection roundups](https://www.sanantonio.gov/Health/News/RestaurantReports#229314405-2022) for a designated year.
2. The bot compiles every weeks report into one annual report, sorts it by the inspection score, and drops everything but the ten worst.
3. The bot then loads each reports inspection page, grabs basic info like the date of the inspection and the address of the restaurant, and, most importantly, what the inspectors observed during their review.
4. The bot then slings those observations over to GPT-3, asking the LLM to simplify them as well as rank in terms of how gross they are. You can check out the prompt I'm using [here](https://github.com/ryan-serpico/sa-restaurant-review-bot/blob/main/prompts/observation-ranker.txt).
5. Finally, the bot writes everything out to a markdown file one by one.

## Run it yourself

1. Clone this repo.
2. Create a virtual environment.
3. Install requirements.txt.
4. Add `.env` file to your directory and plop in your OpenAI API key.
5. Run it: `python3 app.py`

## Things to note

- I, and you, do not blindly take these simplified and ranked observations and publish them without review. LLMs *do not* understand the truth. They hallucinate. In fact, I have seen this very bot hallucinate when there are not at least ten observations in the original inspection. **So a human must be in the loop at all times**.
