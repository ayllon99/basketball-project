from taipy.gui import Gui
import taipy.gui.builder as tgb
from utils.setup import *
from utils.variables import config


with tgb.Page() as root_page:
    tgb.text('')
    # tgb.navbar(class_name='m-auto')

# in %: decimal e.g. 0.62 means 62 %
# in average: integer or decimal


with tgb.Page() as player_by_stat:

    with tgb.layout("1 1 1 1 1 1"):
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("League:", class_name='text-center')
            tgb.selector(value='{league_scraping}',
                         lov='{leagues_list}',
                         dropdown=True,
                         multiple=False,
                         mode='selector')
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Season:", class_name='text-center')
            tgb.selector(value='{season_scraping}',
                         lov='{seasons_list}',
                         dropdown=True,
                         multiple=False,
                         mode='selector')
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Number of matches: (integer)", class_name='m-auto')
            tgb.input("{n_matches}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Minutes average: (integer or mm:ss)",
                     class_name='m-auto')
            tgb.input("{min_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Points average:",
                     class_name='m-auto')
            tgb.input("{points_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Twos in average:",
                     class_name='m-auto')
            tgb.input("{twos_in_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Twos tried average:",
                     class_name='m-auto')
            tgb.input("{twos_tried_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Twos %:",
                     class_name='m-auto')
            tgb.input("{twos_perc}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Threes in average:",
                     class_name='m-auto')
            tgb.input("{threes_in_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Threes tried average:",
                     class_name='m-auto')
            tgb.input("{threes_tried_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Threes %:",
                     class_name='m-auto')
            tgb.input("{threes_perc}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Field goals in average:",
                     class_name='m-auto')
            tgb.input("{field_goals_in_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Field goals tried average:",
                     class_name='m-auto')
            tgb.input("{field_goals_tried_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Field goals %:",
                     class_name='m-auto')
            tgb.input("{field_goals_perc}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Free throws in average:",
                     class_name='m-auto')
            tgb.input("{free_throws_in_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Free throws tried average:",
                     class_name='m-auto')
            tgb.input("{free_throws_tried_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Free throws %:",
                     class_name='m-auto')
            tgb.input("{free_throws_perc}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Offensive rebounds average:",
                     class_name='m-auto')
            tgb.input("{offensive_rebounds_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Deffensive rebounds average:",
                     class_name='m-auto')
            tgb.input("{deffensive_rebounds_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Total rebounds average:",
                     class_name='m-auto')
            tgb.input("{total_rebounds_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Assists average:",
                     class_name='m-auto')
            tgb.input("{assists_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Turnovers average:",
                     class_name='m-auto')
            tgb.input("{turnovers_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Blocks favor average:",
                     class_name='m-auto')
            tgb.input("{blocks_favor_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Blocks against average:",
                     class_name='m-auto')
            tgb.input("{blocks_against_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Dunks average:",
                     class_name='m-auto')
            tgb.input("{dunks_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Personal fouls average:",
                     class_name='m-auto')
            tgb.input("{personal_fouls_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Fouls received average:",
                     class_name='m-auto')
            tgb.input("{fouls_received_avg}", type="number",
                      class_name="form-control")
        with tgb.part(class_name='m-auto text-center'):
            tgb.text("Efficiency average:",
                     class_name='m-auto')
            tgb.input("{efficiency_avg}", type="number",
                      class_name="form-control")
    tgb.text(' ', mode='pre')
    with tgb.layout("1 1 1 1 1 1"):
        with tgb.part():
            tgb.text('')
        with tgb.part():
            tgb.text('')
        with tgb.part(class_name='m-auto'):
            tgb.button("Submit", on_action=submit_stats)
        with tgb.part(class_name='m-auto'):
            tgb.button("Clear", on_action=clear_button)
        with tgb.part(class_name='m-auto'):
            tgb.text('Legend:',class_name="h5 text-center text-underline")
            tgb.text("""- All parameters "in average" use integer or decimal
                     number. E.g. 15 or 15.45""", mode="markdown")
            tgb.text("""- All parameters "in percentage" use decimal number.
                     E.g. 0.45 or 0.25""", mode="markdown")
    tgb.text(' ', mode='pre')
    tgb.text('{scraper_instructions}', class_name='h5 text-center')
    tgb.table('{players_scraped}',
              page_size=4,
              on_action=scraper_triggered)


with tgb.Page() as player_by_team:
    tgb.text('{player_id}', mode='pre', class_name='d-none')
    tgb.text('{team_ids_dict}', mode='pre', class_name='d-none')
    tgb.text('{player_ids_dict}', mode='pre', class_name='d-none')
    with tgb.layout("1 1 1 1"):
        with tgb.part():
            tgb.selector(value='{league_analysis}',
                         lov='{leagues_list}',
                         dropdown=True,
                         multiple=False,
                         mode='selector',
                         label="Select league",
                         class_name="fullwidth",
                         on_change=league_function)
        with tgb.part():
            tgb.selector(value='{season_analysis}',
                         lov='{seasons_list}',
                         dropdown=True,
                         multiple=False,
                         mode='selector',
                         label="Select year",
                         class_name="fullwidth",
                         on_change=season_function)
        with tgb.part():
            tgb.selector(value='{team_analysis}',
                         lov='{teams_list}',
                         dropdown=True,
                         multiple=False,
                         mode='selector',
                         label="Select team",
                         class_name="fullwidth",
                         on_change=team_function)
        with tgb.part():
            tgb.selector(value='{player_analysis}',
                         lov='{players_list}',
                         dropdown=True,
                         multiple=False,
                         mode='selector',
                         label="Select player",
                         class_name="fullwidth",
                         on_change=player_function)


with tgb.Page() as dashboard:
    tgb.expandable('Player founder by stats', page="player_by_stat",
                   expanded=False)
    tgb.text(' ', mode='pre')
    tgb.expandable('Player founder by team', page="player_by_team",
                   expanded=False)
    tgb.text(' ', mode='pre')
    with tgb.layout("1 1 1"):
        with tgb.part(class_name='m-auto'):
            tgb.image('{player_image}',
                      height='{player_image_height}',
                      width='{player_image_width}')
        with tgb.part(class_name='m-auto'):
            tgb.text('{name}', class_name="h2 text-center text-underline")
    tgb.text(' ', mode='pre')
    with tgb.layout("1 1 1 1 1"):
        with tgb.part():
            tgb.text(f'Age', class_name="h3 text-center text-underline")
            tgb.text('{age}', class_name="h3 text-center")
        with tgb.part():
            tgb.text(f'Last season',
                     class_name="h3 text-center text-underline")
            tgb.text('{last_season}', class_name="h3 text-center")
        with tgb.part():
            tgb.text(f'Last league',
                     class_name="h3 text-center text-underline")
            tgb.text('{last_league}', class_name="h3 text-center")
        with tgb.part():
            tgb.text(f'Position', class_name="h3 text-center text-underline")
            tgb.text('{position}', class_name="h3 text-center")
        with tgb.part():
            tgb.text(f'Nationality',
                     class_name="h3 text-center text-underline")
            tgb.text('{nationality}', class_name="h3 text-center")

    tgb.text(' ', mode='pre')
    tgb.text('PLAYER CAREER IN THE COUNTRY', class_name="h2 text-center")
    tgb.table("{player_path}")
    with tgb.layout("1 1 1"):
        with tgb.part():
            tgb.image('{image_1}', width=10, label='')
        with tgb.part():
            tgb.image('{image_2}', width=10, label='')
        with tgb.part():
            tgb.image('{image_3}', width=10, label='')

    tgb.toggle(value='{stat_mode}',
               lov=['AVERAGE', 'TOTAL'],
               dropdown=True,
               multiple=False,
               mode='selector',
               label="",
               class_name="fullwidth",
               on_change=on_mode)
    tgb.text(' ', mode='pre')
    tgb.text('PLAYER CAREER STATS', class_name="h2 text-center")
    tgb.text(' ', mode='pre')
    tgb.table("{player_stats_table}")
    tgb.text(' ', mode='pre')
    with tgb.layout("225px 1"):
        tgb.selector(value='{stats_to_show}',
                     lov='{stats_columns}',
                     dropdown=True,
                     multiple=True,
                     mode='selector',
                     label="Select stat",
                     class_name="fullwidth",
                     on_change=on_stats_selector)
    with tgb.layout("1"):
        with tgb.part():
            tgb.chart(figure="{figg}", class_name='fullwidth')

pages = {
    "/": root_page,
    "dashboard": dashboard,
    "player_by_stat": player_by_stat,
    "player_by_team": player_by_team
    }

gui = Gui(pages=pages)
gui.on_init = init
gui.run(title='Player analysis', port=5000, watermark='',
        favicon=config['icon_path'])
