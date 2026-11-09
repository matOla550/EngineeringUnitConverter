
from flask import Flask, render_template, request

from pathlib import Path

from datetime import datetime

import csv

import math


app = Flask(__name__)


LOG = Path(__file__).with_name('conversion_log.csv')



CONVERSIONS = {
    'm_cm': (
        'Metres to centimetres',
        'm', 'cm',
        lambda x: x * 100,
        0
    ),

    'km_m': (
        'Kilometres to metres',
        'km', 'm',
        lambda x: x * 1000,
        0
    ),

    'c_f': (
        'Celsius to Fahrenheit',
        '°C', '°F',
        lambda x: x * 9 / 5 + 32,
        -273.15
    ),

    'f_c': (
        'Fahrenheit to Celsius',
        '°F', '°C',
        lambda x: (x - 32) * 5 / 9,
        -459.67
    ),

    'kg_g': (
        'Kilograms to grams',
        'kg', 'g',
        lambda x: x * 1000,
        0
    ),

    'speed': (
        'Kilometres/hour to metres/second',
        'km/h', 'm/s',
        lambda x: x / 3.6,
        0
    ),

    'km_mi': (
        'Kilometres to miles',
        'km', 'mi',
        lambda x: x * 0.621371,
        0
    ),

    'deg_rad': (
        'Degrees to radians',
        '°', 'rad',
        math.radians,
        None
    )
}


FIELDS = [
    'date',
    'conversion',
    'input',
    'result',
    'from_unit',
    'to_unit'
]



def load_history():

    if not LOG.exists():
        return [], None

    try:
        with LOG.open('r', newline='', encoding='utf-8') as file:

            history = list(csv.DictReader(file))

            return history, None

    except (OSError, UnicodeError, csv.Error) as exc:

        return [], f'Could not read history: {exc}'



def save_record(record):

    try:
        is_new = not LOG.exists() or LOG.stat().st_size == 0

        with LOG.open('a', newline='', encoding='utf-8') as file:

            writer = csv.DictWriter(file, fieldnames=FIELDS)

            if is_new:
                writer.writeheader()

            writer.writerow(record)

        return None

    except OSError as exc:

        return f'Conversion worked, but saving failed: {exc}'




@app.route('/', methods=['GET', 'POST'])
def home():

    selected = request.form.get('conversion', 'm_cm')

    entered = request.form.get('value', '')

    result = None

    error = None


    if request.method == 'POST':

        if selected not in CONVERSIONS:
            error = 'Choose a valid conversion.'

        else:
            label, from_unit, to_unit, formula, minimum = CONVERSIONS[selected]

            try:
                number = float(entered)

                if not math.isfinite(number):
                    raise ValueError('non-finite number')

                if minimum is not None and number < minimum:

                    error = (
                        f'The minimum allowed value is '
                        f'{minimum} {from_unit}.'
                    )

                else:
                    answer = formula(number)

                    if not math.isfinite(answer):
                        error = 'The result is too large to display.'

                    else:
                        result = {
                            'value': f'{answer:,.4f}',
                            'unit': to_unit,
                            'expression': (
                                f'{number:g} {from_unit} = '
                                f'{answer:,.4f} {to_unit}'
                            ),
                            'label': label
                        }

                        error = save_record({
                            'date': datetime.now().strftime(
                                '%Y-%m-%d %H:%M:%S'
                            ),
                            'conversion': label,
                            'input': number,
                            'result': answer,
                            'from_unit': from_unit,
                            'to_unit': to_unit
                        })

            except (ValueError, OverflowError):

                error = 'Please enter a valid finite number.'



    history, read_error = load_history()

    if read_error and not error:
        error = read_error



    values = []

    if selected in CONVERSIONS:

        label = CONVERSIONS[selected][0]

        for item in history:

            if item.get('conversion') == label:

                try:
                    n = float(item['result'])

                    if math.isfinite(n):
                        values.append(n)

                except (ValueError, KeyError, TypeError):

                    pass


    stats = None

    if values:

        stats = {
            'count': len(values),

            'average': f'{math.fsum(values)/len(values):,.2f}',

            'minimum': f'{min(values):,.2f}',

            'maximum': f'{max(values):,.2f}',

            'total': f'{math.fsum(values):,.2f}'
        }



    return render_template(
        'index.html',

        conversions=CONVERSIONS,

        selected=selected,

        entered=entered,

        result=result,

        error=error,

        history=list(reversed(history))[:30],

        stats=stats
    )



if __name__ == '__main__':

    app.run(debug=True)
