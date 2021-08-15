# Automated Cronometer

A CLI tool for programmatically working with Cronometer.

## How I use this

This tool was made with my particular behaviors in mind:

- I store recipes on Cronometer.
- I log what food I plan to eat once a week. I don't log food by the day like
  many MyFitnessPal or Cronometer users do.
    - I add recipes to Sunday until all my macros and micros are at 700% daily
      value (7 days a week, so on average, I'm getting the daily recommended
      dose).
- I only eat what I make myself (i.e. I rarely go out to eat).
- I go grocery shopping once a week.
- I keep notice of what is in stock in my kitchen.
- I export the recipes I have planned for this week into a grocery list stored
  on the cloud.

## Assumptions

- The Cronometer website doesn't get a massive UI update that messes up all of
  my assumptions on which web elements are where.
- Cronometer recipe ID changes whenever you edit a recipe.

## Setup

### Download `geckodriver`

Selenium needs a web driver to run. Let's use Firefox's.

- Get the latest release from [the GitHub page](https://github.com/mozilla/geckodriver/releases).
- `tar xzf <the geckodriver tar.gz>`

### Generate `client_id.json`

You only need this if you want a grocery list.

Basically follow the instructions on [the Google Sheets API v4 Quickstart page](https://developers.google.com/sheets/api/quickstart/python).

### Generate a service account JSON

- Create a service account [here](https://console.cloud.google.com/iam-admin/serviceaccounts).
- Create a key for the service account.
    - Download the key as a JSON file into `setup_files`.

### Create `config.sh`

This file should look like this:

```python3
geckodriver_path=<path to geckodriver>
cronometer_user=<cronometer username>
cronometer_pass=<cronometer password>
google_sheets_api_sheet_id=<existing google sheet that will contain the grocery list>
export google_sheets_api_sheet_id=<the sheet you want to edit>
export GOOGLE_APPLICATION_CREDENTIALS=<path to your JSON file>
```

Don't share it with anyone. Apply your own security measures.

## Usage

```bash
source config.sh
poetry run main -h
```

### active.yaml

List of dictionaries containing: id and name. If a recipe is in this file, then
it is "active". This means that if you create a grocery list, it'll only use
the active recipes' ingredients to do so.

## Research: Finding the API

I looked at a few sites. Many of them, such as [Web Scraping - Discovering
Hidden APIs][1], assume the website uses REST APIs. Unfortunately, Cronometer
does not. The above website's instructions did help, though.

I used my browser's developer tools, and looked at the _Network_ tab. I found a
request Cronometer made, and found something peculiar:
`com.cronometer.client.CronometerService`. This reminds of Java. So, I google
that Java line, and found [a thread of the Chronometer developers asking for
help on GWT][2]. GWT is Google Web Toolkit. So this is what they use!

I googled _how to reverse engineer GWT web apps_ and found [this tool][3].


[1]: https://ianlondon.github.io/blog/web-scraping-discovering-hidden-apis/
[2]: https://groups.google.com/g/google-web-toolkit/c/QAjq1OYOOYM/m/d2YFSqPPCgAJ?utm_medium=email&utm_source=footer
[3]: https://labs.f-secure.com/blog/gwtmap-reverse-engineering-google-web-toolkit-applications/
