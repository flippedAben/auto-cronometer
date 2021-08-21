# Automated Cronometer

A CLI tool for programmatically working with Cronometer.

## How I use this

This tool was made with my particular behaviors in mind:

- I store recipes on Cronometer.
- I log what food I plan to eat once a week.
    - I add recipes to Sunday until all my macros and micros are at 700% daily
      value (7 days a week, so on average, I'm getting the daily recommended
      dose).
    - I eat exactly what I plan (to minimize food waste).
- Occasionally, I go out to eat, and I add that to my weekly total.
- I go grocery shopping once a week.
- I export the recipes I have planned for this week into a grocery list stored
  on the cloud.
    - I download that list onto my phone before I go shopping for groceries.
- I keep notice of what is in stock in my kitchen.

## Assumptions

- The Cronometer backend uses GWT and doesn't get a major API overhaul. If that
  happens, this tool will probably not work.

## Setup

### Download `geckodriver`

We use Selenium to log into Cronometer. I didn't figure out how to do this with
just `requests`. Selenium needs a web driver to run. Let's use Firefox's.

- Get the latest release from [the GitHub page][1]
- `tar xzf <the geckodriver tar.gz>`


### Generate `client_id.json`

You only need this if you want a grocery list on Google Sheets.

Basically follow the instructions on the Google Sheets API v4 [Quickstart
page][2].


### Generate a service account JSON

- Create a service account [here][3].
- Create a key for the service account.
    - Download the key as a JSON file into `setup_files`.

### Create `config.sh`

This file should look like this:

```python3
geckodriver_path=<path to geckodriver>
cronometer_user=<cronometer username>
cronometer_pass=<cronometer password>
cronometer_hex=<ask the author>
google_sheets_api_sheet_id=<existing google sheet that will contain the grocery list>
export google_sheets_api_sheet_id=<the sheet you want to edit>
export GOOGLE_APPLICATION_CREDENTIALS=<path to your JSON file>
```

Don't share it with anyone. Apply your own security measures.

`cronometer_hex` is still a work in progress. If you log into Cronometer
manually, and then inspect the network traffic, you'll see something like:

```
7|0|7|https://cronometer.com/cronometer/|<cronometer_hex>|...
```

TODO: Figure out how to get this via the code, and not manually.

## Usage

```bash
source config.sh
poetry run main -h
```

### config.yaml

You create this file, and update it manually. This file contains entries like
this:

```
11369138:
  group: pantry
  in_stock: false
  name: Huy Fong Foods, Sambal Oelek Ground Fresh Chili Paste
```

The Cronometer food ID indexes:

- the name of the food
- whether its in stock
- which group of groceries it belongs to (used to organize the grocery list)


### `<recipes>.yaml` and `locked_<recipes>.yaml`

You can store recipes into a YAML file, and lock it. If I liked the recipes I
planned for the week, I'll do this, so I have a reproducible experience.

## Research: Finding the API

I looked at a few sites. Many of them, such as [Web Scraping - Discovering
Hidden APIs][4], assume the website uses REST APIs. Unfortunately, Cronometer
does not. The above website's instructions did help, though.

I used my browser's developer tools, and looked at the _Network_ tab. I found a
request Cronometer made, and found something peculiar:
`com.cronometer.client.CronometerService`. This reminds of Java. So, I google
that Java line, and found [a thread of the Chronometer developers asking for
help on GWT][5]. GWT is Google Web Toolkit. So this is what they use!

I googled _how to reverse engineer GWT web apps_ and found [this tool][6].


[1]: https://github.com/mozilla/geckodriver/releases
[2]: https://developers.google.com/sheets/api/quickstart/python
[3]: https://console.cloud.google.com/iam-admin/serviceaccounts
[4]: https://ianlondon.github.io/blog/web-scraping-discovering-hidden-apis/
[5]: https://groups.google.com/g/google-web-toolkit/c/QAjq1OYOOYM/m/d2YFSqPPCgAJ?utm_medium=email&utm_source=footer
[6]: https://labs.f-secure.com/blog/gwtmap-reverse-engineering-google-web-toolkit-applications/
