from flask import Flask, render_template, request, jsonify
from varasto import Varasto

app = Flask(__name__)

# Store warehouses with unique IDs
warehouses = {}
warehouse_counter = 0


def parse_float(value, default=0.0):
    """Safely parse a float value with error handling."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/warehouses', methods=['GET'])
def get_warehouses():
    result = {}
    for wid, warehouse in warehouses.items():
        result[wid] = {
            'tilavuus': warehouse.tilavuus,
            'saldo': warehouse.saldo,
            'tilaa': warehouse.paljonko_mahtuu()
        }
    return jsonify(result)


@app.route('/api/warehouses', methods=['POST'])
def create_warehouse():
    global warehouse_counter
    data = request.get_json()

    tilavuus = parse_float(data.get('tilavuus'), 0)
    alku_saldo = parse_float(data.get('alku_saldo'), 0)

    warehouse = Varasto(tilavuus, alku_saldo)
    warehouse_counter += 1
    wid = str(warehouse_counter)
    warehouses[wid] = warehouse

    return jsonify({
        'id': wid,
        'tilavuus': warehouse.tilavuus,
        'saldo': warehouse.saldo,
        'tilaa': warehouse.paljonko_mahtuu()
    })


@app.route('/api/warehouses/<wid>/paljonko_mahtuu', methods=['GET'])
def paljonko_mahtuu(wid):
    if wid not in warehouses:
        return jsonify({'error': 'Warehouse not found'}), 404

    warehouse = warehouses[wid]
    return jsonify({'tilaa': warehouse.paljonko_mahtuu()})


@app.route('/api/warehouses/<wid>/lisaa', methods=['POST'])
def lisaa_varastoon(wid):
    if wid not in warehouses:
        return jsonify({'error': 'Warehouse not found'}), 404

    data = request.get_json()
    maara = parse_float(data.get('maara'), 0)

    warehouse = warehouses[wid]
    warehouse.lisaa_varastoon(maara)

    return jsonify({
        'saldo': warehouse.saldo,
        'tilaa': warehouse.paljonko_mahtuu()
    })


@app.route('/api/warehouses/<wid>/ota', methods=['POST'])
def ota_varastosta(wid):
    if wid not in warehouses:
        return jsonify({'error': 'Warehouse not found'}), 404

    data = request.get_json()
    maara = parse_float(data.get('maara'), 0)

    warehouse = warehouses[wid]
    otettu = warehouse.ota_varastosta(maara)

    return jsonify({
        'otettu': otettu,
        'saldo': warehouse.saldo,
        'tilaa': warehouse.paljonko_mahtuu()
    })


@app.route('/api/warehouses/<wid>', methods=['DELETE'])
def delete_warehouse(wid):
    if wid not in warehouses:
        return jsonify({'error': 'Warehouse not found'}), 404

    del warehouses[wid]
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
