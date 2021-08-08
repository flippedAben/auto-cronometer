import os
import auto_cronometer.auto_cm as auto_cm
import shutil


def scrape_recipes(out_dir):
    # Enable headless Firefox
    os.environ['MOZ_HEADLESS'] = '1'

    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)

    with auto_cm.AutoCronometer() as ac:
        ac.login()
        ac.go_to_recipes_tab()

        print('Scraping recipe HTMLs...')
        htmls = ac.get_recipe_page_sources()
        for i, html in enumerate(htmls):
            with open(f'{out_dir}/recipe_{i}.html', 'w') as f:
                f.write(html)
