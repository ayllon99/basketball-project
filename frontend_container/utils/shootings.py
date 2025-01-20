from matplotlib import pyplot as plt
import matplotlib.axes as axes
import matplotlib.figure as figure
from matplotlib.patches import Circle, Rectangle, Arc, Wedge
import matplotlib.image as mpimg
from utils.variables import config


data_not_found_path = config['data_not_found_path']
error_proc_data_path = config['error_proc_data_path']


def draw_court(ax: axes.Axes, color: str = "black", lw: int = 1,
               outer_lines: bool = True) -> axes.Axes:
    """
    Draws a basketball court on the given matplotlib axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw the court on.
    color : str, optional
        The color of the court lines. Defaults to "black".
    lw : int, optional
        The line width of the court lines. Defaults to 1.
    outer_lines : bool, optional
        Whether to draw the outer lines of the court. Defaults to True.

    Returns
    -------
    matplotlib.axes
        The axes with the drawn court.

    Notes
    -----
    This function draws all the elements of a basketball court, including the
    hoop, backboard, paint, free throw lines, restricted zone, three point
    line, and center court.
    """
    # Basketball Hoop
    hoop = Circle((0, -20), radius=7.5, linewidth=lw, color=color,
                  fill=False)
    # Backboard
    backboard = Rectangle((-30, -32.5), 60, 0, linewidth=lw, color=color)
    # The paint
    # Outer box
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw,
                          color=color, fill=False)
    # Inner box
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw,
                          color=color, fill=False)
    # Free Throw Top Arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Free Bottom Top Arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color)
    # Restricted Zone
    restricted = Arc((0, -20), 80, 80, theta1=0, theta2=180,
                     linewidth=lw, color=color)
    # Three Point Line
    corner_three_a = Rectangle((-220.2, -47.5), 0, 136.4, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220.2, -47.5), 0, 136.4, linewidth=lw,
                               color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)
    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    # Painting
    color_front = '#f9cb9c'
    color_sides = '#e58b2f'
    color_corners = '#f9cb9c'
    three_point_line_wedge_right = Wedge((0, 0), 238, 22, 75, width=70,
                                         facecolor=color_sides)
    three_point_line_wedge_left = Wedge((0, 0), 238, 95, 158, width=70,
                                        facecolor=color_sides)
    three_point_line_wedge_front = Wedge((0, 0), 238, 70.5, 109.8,
                                         width=50, facecolor=color_front)
    front_rect = Rectangle((-80, 142.5), 160, 81, linewidth=1,
                           color=color_front, fill=True)
    left_side_rect = Rectangle((-80, 88.9), -90, 60, linewidth=1,
                               color=color_sides, fill=True)
    right_side_rect = Rectangle((80, 88.9), 90, 60, linewidth=1,
                                color=color_sides, fill=True)
    right_corner_rect = Rectangle((220.2, -47.5), -140, 136.4,
                                  linewidth=1, color=color_corners,
                                  fill=True)
    left_corner_rect = Rectangle((-220.2, -47.5), 140, 136.4, linewidth=1,
                                 color=color_corners, fill=True,)

    court_elements = [three_point_line_wedge_left,
                      three_point_line_wedge_right,
                      three_point_line_wedge_front, right_side_rect,
                      right_corner_rect, left_side_rect, left_corner_rect,
                      front_rect, hoop, outer_box, backboard,
                      top_free_throw, bottom_free_throw, restricted,
                      corner_three_a, corner_three_b, three_arc,
                      center_outer_arc]

    if outer_lines:
        outer_lines = Rectangle((-275, -47.5), 550, 470, linewidth=lw,
                                color='white', fill=False)
        court_elements.append(outer_lines)

    for element in court_elements:
        ax.add_patch(element)
    return ax


def process_dict_stats(dic_stats: dict, year: int) -> dict:
    """
    Process the shooting statistics dictionary for a given year.

    This function takes a dictionary of shooting statistics and a year
    as input, and returns a new dictionary with the processed statistics
    for the given year.

    The processed statistics include the total shots made and attempted,
    as well as the percentage of shots made, for each zone on the court.

    Args:
        dic_stats (dict): A dictionary of shooting statistics.
        year (int): The year for which to process the statistics.

    Returns:
        dict: A dictionary with the processed shooting statistics for the
        given year.

    Raises:
        Exception: If an error occurs while processing the statistics.
    """
    try:
        right_corner_three_total = f"""{
            dic_stats[year]['Right Corner Three']['in']}/\
            {dic_stats[year]['Right Corner Three']['tried']}"""\
            .replace(' ', '')
        right_corner_three = f"""{
            round((int(dic_stats[year]['Right Corner Three']['in']) /
                  int(dic_stats[year]['Right Corner Three']['tried']))
                  * 100, 2)}%"""
    except Exception:
        right_corner_three_total = f"""{
            dic_stats[year]['Right Corner Three']['in']}/\
            {dic_stats[year]['Right Corner Three']['tried']}"""\
                .replace(' ', '')
        right_corner_three = '0%'
    try:
        right_corner_middle_total = f"""{
            dic_stats[year]['Right Corner Middle']['in']}/\
            {dic_stats[year]['Right Corner Middle']['tried']}"""\
                .replace(' ', '')
        right_corner_middle = f"""{
            round((int(dic_stats[year]['Right Corner Middle']['in']) /
                  int(dic_stats[year]['Right Corner Middle']['tried']))
                  * 100, 2)}%"""
    except Exception:
        right_corner_middle_total = f"""{
            dic_stats[year]['Right Corner Middle']['in']}/\
            {dic_stats[year]['Right Corner Middle']['tried']}"""\
                .replace(' ', '')
        right_corner_middle = '0%'
    try:
        right_side_three_total = f"""{
            dic_stats[year]['Right Side Three']['in']}/\
            {dic_stats[year]['Right Side Three']['tried']}"""\
                .replace(' ', '')
        right_side_three = f"""{
            round((int(dic_stats[year]['Right Side Three']['in']) /
                  int(dic_stats[year]['Right Side Three']['tried']))
                  * 100, 2)}%"""
    except Exception:
        right_side_three_total = f"""{
            dic_stats[year]['Right Side Three']['in']}/\
            {dic_stats[year]['Right Side Three']['tried']}""".replace(' ', '')
        right_side_three = '0%'
    try:
        right_side_middle_total = f"""{
            dic_stats[year]['Right Side Middle']['in']}/\
            {dic_stats[year]['Right Side Middle']['tried']}"""\
                .replace(' ', '')
        right_side_middle = f"""{
            round((int(dic_stats[year]['Right Side Middle']['in']) /
                  int(dic_stats[year]['Right Side Middle']['tried']))
                  * 100, 2)}%"""
    except Exception:
        right_side_middle_total = f"""{
            dic_stats[year]['Right Side Middle']['in']}/\
            {dic_stats[year]['Right Side Middle']['tried']}""".replace(' ', '')
        right_side_middle = '0%'
    try:
        front_three_total = f"""{
            dic_stats[year]['Front Three']['in']}/\
            {dic_stats[year]['Front Three']['tried']}"""\
                .replace(' ', '')
        front_three = f"""{
            round((int(dic_stats[year]['Front Three']['in']) /
                  int(dic_stats[year]['Front Three']['tried']))
                  * 100, 2)}%"""
    except Exception:
        front_three_total = f"""{
            dic_stats[year]['Front Three']['in']}/\
        {dic_stats[year]['Front Three']['tried']}""".replace(' ', '')
        front_three = '0%'
    try:
        front_middle_total = f"""{
            dic_stats[year]['Front Middle']['in']}/\
            {dic_stats[year]['Front Middle']['tried']}"""\
                .replace(' ', '')
        front_middle = f"""{
            round((int(dic_stats[year]['Front Middle']['in']) /
                  int(dic_stats[year]['Front Middle']['tried']))
                  * 100, 2)}%"""
    except Exception:
        front_middle_total = f"""{
            dic_stats[year]['Front Middle']['in']}/\
            {dic_stats[year]['Front Middle']['tried']}""".replace(' ', '')
        front_middle = '0%'
    try:
        left_side_three_total = f"""{
            dic_stats[year]['Left Side Three']['in']}/\
            {dic_stats[year]['Left Side Three']['tried']}"""\
                .replace(' ', '')
        left_side_three = f"""{
            round((int(dic_stats[year]['Left Side Three']['in']) /
                  int(dic_stats[year]['Left Side Three']['tried']))
                  * 100, 2)}%"""
    except Exception:
        left_side_three_total = f"""{
            dic_stats[year]['Left Side Three']['in']}/\
            {dic_stats[year]['Left Side Three']['tried']}""".replace(' ', '')
        left_side_three = '0%'
    try:
        left_side_middle_total = f"""{
            dic_stats[year]['Left Side Middle']['in']}/\
            {dic_stats[year]['Left Side Middle']['tried']}"""\
                .replace(' ', '')
        left_side_middle = f"""{
            round((int(dic_stats[year]['Left Side Middle']['in']) /
                  int(dic_stats[year]['Left Side Middle']['tried']))
                  * 100, 2)}%"""
    except Exception:
        left_side_middle_total = f"""{
            dic_stats[year]['Left Side Middle']['in']}/\
            {dic_stats[year]['Left Side Middle']['tried']}""".replace(' ', '')
        left_side_middle = '0%'
    try:
        left_corner_three_total = f"""{
            dic_stats[year]['Left Corner Three']['in']}/\
            {dic_stats[year]['Left Corner Three']['tried']}"""\
            .replace(' ', '')
        left_corner_three = f"""{
            round((int(dic_stats[year]['Left Corner Three']['in']) /
                  int(dic_stats[year]['Left Corner Three']['tried']))
                  * 100, 2)}%"""
    except Exception:
        left_corner_three_total = f"""{
            dic_stats[year]['Left Corner Three']['in']}/\
            {dic_stats[year]['Left Corner Three']['tried']}"""\
            .replace(' ', '')
        left_corner_three = '0%'
    try:
        left_corner_middle_total = f"""{
            dic_stats[year]['Left Corner Middle']['in']}/\
            {dic_stats[year]['Left Corner Middle']['tried']}"""\
                .replace(' ', '')
        left_corner_middle = f"""{
            round((int(dic_stats[year]['Left Corner Middle']['in']) /
                  int(dic_stats[year]['Left Corner Middle']['tried']))
                  * 100, 2)}%"""
    except Exception:
        left_corner_middle_total = f"""{
            dic_stats[year]['Left Corner Middle']['in']}/\
            {dic_stats[year]['Left Corner Middle']['tried']}"""\
                .replace(' ', '')
        left_corner_middle = '0%'
    try:
        zone_total = f"""{
            dic_stats[year]['Zone']['in']}/\
            {dic_stats[year]['Zone']['tried']}""".replace(' ', '')
        zone = f"""{
            round((int(dic_stats[year]['Zone']['in']) /
                  int(dic_stats[year]['Zone']['tried']))
                  * 100, 2)}%"""
    except Exception:
        zone_total = f"""{
            dic_stats[year]['Zone']['in']}/\
            {dic_stats[year]['Zone']['tried']}""".replace(' ', '')
        zone = '0%'

    stats_to_display = {
        'right_corner_three_total': right_corner_three_total,
        'right_corner_three': right_corner_three,
        'right_corner_middle_total': right_corner_middle_total,
        'right_corner_middle': right_corner_middle,
        'right_side_three_total': right_side_three_total,
        'right_side_three': right_side_three,
        'right_side_middle_total': right_side_middle_total,
        'right_side_middle': right_side_middle,
        'front_three_total': front_three_total,
        'front_three': front_three,
        'front_middle_total': front_middle_total,
        'front_middle': front_middle,
        'left_side_three_total': left_side_three_total,
        'left_side_three': left_side_three,
        'left_side_middle_total': left_side_middle_total,
        'left_side_middle': left_side_middle,
        'left_corner_three_total': left_corner_three_total,
        'left_corner_three': left_corner_three,
        'left_corner_middle_total': left_corner_middle_total,
        'left_corner_middle': left_corner_middle,
        'zone_total': zone_total,
        'zone': zone
        }

    return stats_to_display


def adding_stats_to_display(ax: axes.Axes,
                            stats_to_display: dict) -> axes.Axes:
    """
    Adds shooting statistics to a matplotlib axes object.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to add the statistics to.
    stats_to_display : dict
        A dictionary containing the shooting statistics to display.
        The dictionary should have the following keys:
            - 'zone'
            - 'zone_total'
            - 'front_middle'
            - 'front_middle_total'
            - 'right_side_middle'
            - 'right_side_middle_total'
            - 'left_side_middle'
            - 'left_side_middle_total'
            - 'left_corner_middle'
            - 'left_corner_middle_total'
            - 'right_corner_middle'
            - 'right_corner_middle_total'
            - 'front_three'
            - 'front_three_total'
            - 'right_side_three'
            - 'right_side_three_total'
            - 'left_side_three'
            - 'left_side_three_total'
            - 'left_corner_three'
            - 'left_corner_three_total'
            - 'right_corner_three'
            - 'right_corner_three_total'

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object with the added statistics.

    Notes
    -----
    The statistics are added as text annotations to the axes object at specific
    locations.
    The locations are hardcoded and are based on a basketball court layout.
    """
    # Zone
    ax.text(0, 60, stats_to_display['zone'], ha="center", va="center",
            fontsize=10)
    ax.text(0, 40, stats_to_display['zone_total'], ha="center", va="center",
            fontsize=10)
    # Front Middle
    ax.text(0, 185, stats_to_display['front_middle'], ha="center", va="center",
            fontsize=10)
    ax.text(0, 165, stats_to_display['front_middle_total'], ha="center",
            va="center", fontsize=10)
    # Right Side Middle
    ax.text(145, 140, stats_to_display['right_side_middle'], ha="center",
            va="center", fontsize=10)
    ax.text(145, 120, stats_to_display['right_side_middle_total'], ha="center",
            va="center", fontsize=10)
    # Left Side Middle
    ax.text(-145, 140, stats_to_display['left_side_middle'], ha="center",
            va="center", fontsize=10)
    ax.text(-145, 120, stats_to_display['left_side_middle_total'],
            ha="center", va="center", fontsize=10)
    # Left Corner Middle
    ax.text(-150, 20, stats_to_display['left_corner_middle'], ha="center",
            va="center", fontsize=10)
    ax.text(-150, 0, stats_to_display['left_corner_middle_total'],
            ha="center", va="center", fontsize=10)
    # Right Corner Middle
    ax.text(150, 20, stats_to_display['right_corner_middle'], ha="center",
            va="center", fontsize=10)
    ax.text(150, 0, stats_to_display['right_corner_middle_total'], ha="center",
            va="center", fontsize=10)
    # Front Three
    ax.text(0, 280, stats_to_display['front_three'], ha="center", va="center",
            fontsize=10)
    ax.text(0, 260, stats_to_display['front_three_total'], ha="center",
            va="center", fontsize=10)
    # Right Side Three
    ax.text(210, 180, stats_to_display['right_side_three'], ha="center",
            va="center", fontsize=10)
    ax.text(210, 160, stats_to_display['right_side_three_total'], ha="center",
            va="center", fontsize=10)
    # Left Side Three
    ax.text(-210, 180, stats_to_display['left_side_three'], ha="center",
            va="center", fontsize=10)
    ax.text(-210, 160, stats_to_display['left_side_three_total'], ha="center",
            va="center", fontsize=10)
    # Left Corner Three
    ax.text(-280, 0, stats_to_display['left_corner_three'], fontsize=10)
    ax.text(-280, -20, stats_to_display['left_corner_three_total'],
            fontsize=10)
    # Right Corner Three
    ax.text(230, 0, stats_to_display['right_corner_three'], fontsize=10)
    ax.text(230, -20, stats_to_display['right_corner_three_total'],
            fontsize=10)

    return ax


def set_look(ax: axes.Axes, fig: figure.Figure, year: int,
             found: bool) -> tuple[axes.Axes, figure.Figure]:
    """
    Configures the appearance of a matplotlib axes and figure for displaying
    shooting statistics.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to configure.
    fig : matplotlib.figure.Figure
        The figure to configure.
    year : int
        The year for which the shooting statistics are being displayed.
    found : bool
        A flag indicating whether data was found for the specified year.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The configured axes.
    fig : matplotlib.figure.Figure
        The configured figure.

    Notes
    -----
    This function sets the title, tick labels, and face color of the axes and
    figure.
    If data was found for the specified year, it will also create an empty
    plot.
    """
    ax.set_title(f'Shootings stats in {year}/{year+1}', color='white')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.patch.set_facecolor('white')
    fig.patch.set_facecolor('none')
    if found:
        ax.plot()
    return ax, fig


def generate_image(dic_stats: dict = None, year: int = None) -> figure.Figure:
    """
    Generates an image based on the provided statistics dictionary and year.

    Parameters:
    ----------
    dic_stats : dict, optional
        A dictionary containing shooting statistics (default is None).
    year : int, optional
        The year for which the image is generated (default is None).

    Returns:
    -------
    figure.Figure
        The generated figure object.

    Raises:
    ------
    Exception
        If an error occurs while processing the data, an exception is caught
        and an error message is printed.
    """
    try:
        plt.close('all')
        fig, ax = plt.subplots()
        if year in dic_stats.keys():
            ax = draw_court(ax)
            stats_to_display = process_dict_stats(dic_stats, year)
            ax = adding_stats_to_display(ax, stats_to_display)
            ax, fig = set_look(ax, fig, year, found=True)

        else:
            img = mpimg.imread(data_not_found_path)
            ax.imshow(img)
            ax, fig = set_look(ax, fig, year, found=False)
    except Exception:
        print(f'Error processing data in: {year}')
        img = mpimg.imread(error_proc_data_path)
        ax.imshow(img)
        ax, fig = set_look(ax, fig, year, found=False)
    return fig
