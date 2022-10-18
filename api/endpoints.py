from collections import Counter
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request

from api.config import get_connection
from api.query import *

pelayanan_bp = Blueprint("pelayanan", __name__)
engine = get_connection()


def get_default_date(tgl_awal, tgl_akhir):
    if tgl_awal == None:
        tgl_awal = datetime.strptime((datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_awal = datetime.strptime(tgl_awal, '%Y-%m-%d')

    if tgl_akhir == None:
        tgl_akhir = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
    return tgl_awal, tgl_akhir


def get_date_prev(tgl_awal, tgl_akhir):
    tgl_awal = tgl_awal - relativedelta(months=1)
    tgl_awal = tgl_awal.strftime('%Y-%m-%d')
    tgl_akhir = tgl_akhir - relativedelta(months=1)
    tgl_akhir = tgl_akhir.strftime('%Y-%m-%d')
    return tgl_awal, tgl_akhir


def count_values(data, param):
    cnt = Counter()
    for i in range(len(data)):
        # cnt[data[i][param].lower().replace(' ', '_')] += 1
        cnt[data[i][param]] += 1
    return cnt


@pelayanan_bp.route('/pelayanan/card_pasien')
def card_pasien():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_card_pasien(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_card_pasien(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPelayanan'], "instalasi": row['NamaInstalasi'].split("\r")[0]} for row in result]
    tmp_prev = [{"tanggal": row['TglPelayanan'], "instalasi": row['NamaInstalasi'].split("\r")[0]} for row in result_prev]

    # Extract data as (dataframe)
    cnts = count_values(tmp, 'instalasi')
    cnts_prev = count_values(tmp_prev, 'instalasi')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None
    
    result = {
        "judul": "Ruangan (Card Kunjungan)",
        "label": 'Pelayanan Pasien',
        "data": data, #count_values(data, 'instalasi'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


# Detail Card kunjungan (pop up table)
@pelayanan_bp.route('/pelayanan/detail_card_pasien')
def detail_card_pasien():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    # Get query result
    result = query_detail_card_pasien(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Define return result as a json
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPelayanan'],
            "no_daftar": row['NoPendaftaran'],
            "no_cm": row['NoCM'],
            "nama": row['Title']+' '+row['NamaLengkap'],
            "tgl_lahir": row['TglLahir'],
            "jenis_kelamin": row['JenisKelamin'],
            "alamat": row['Alamat'],
            "judul": "Detail (Card Kunjungan)",
            "label": "Kunjungan Pasien"
        })
    return jsonify(data)


@pelayanan_bp.route('/pelayanan/mutu_pelayanan')
def mutu_palayanan():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'standar mutu pelayanan'})


@pelayanan_bp.route('/pelayanan/kelas_perawatan')
def kelas_perawatan():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_kelas_perawatan(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_kelas_perawatan(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPelayanan'], "kelas": row['NamaKelas']} for row in result]
    tmp_prev = [{"tanggal": row['TglPelayanan'], "kelas": row['NamaKelas']} for row in result_prev]
    
    # Extract data as (dataframe)
    cnts = count_values(tmp, 'kelas')
    cnts_prev = count_values(tmp_prev, 'kelas')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None

    result = {
        "judul": 'Kelas Perawatan',
        "label": 'Pelayanan Pasien',
        "data": data, #count_values(data, 'kelas'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/pelayanan/kepuasan_pelayanan')
def kepuasan_pelayanan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'ini data Kepuasan Pelayanan'})


@pelayanan_bp.route('/pelayanan/kelompok_pasien')
def kelompok_pasien():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_kelompok_pasien(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_kelompok_pasien(tgl_awal, tgl_akhir + timedelta(days=1))
    
    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPelayanan'], "kelompok": row['KelompokPasien']} for row in result]
    tmp_prev = [{"tanggal": row['TglPelayanan'], "kelompok": row['KelompokPasien']} for row in result_prev]

    # Extract data as (dataframe)
    cnts = count_values(tmp, 'kelompok')
    cnts_prev = count_values(tmp_prev, 'kelompok')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None

    # Define return result as a json
    result = {
        "judul": 'Kelompok Pasien',
        "label": 'Pelayanan Pasien',
        "data": data, #count_values(data, 'kelompok'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/pelayanan/pelayanan_dokter')
def pelayanan_dokter():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    
    # Get query result
    result = query_pelayanan_dokter(tgl_awal, tgl_akhir + timedelta(days=1))

    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglMasuk'], "id_dokter": row['IdDokter'], "nama": row['Dokter']} for row in result]

    # Extract data as (dataframe)
    cnt_name = count_values(tmp, 'nama')
    cnts_id = count_values(tmp, 'id_dokter')
    data = [{"name": x, "value": y, "id_dokter": z} for x, y in cnt_name.items() for z, _ in cnts_id.items()]
    
    # Define return result as a json
    result = {
        "judul": 'Pelayanan Dokter',
        "label": 'Pelayanan Pasien',
        "data": data,
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/pelayanan/top_diagnosa')
def top_diagnosa():
    # Date Initialization
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    tgl_awal_prev, tgl_akhir_prev = get_date_prev(tgl_awal, tgl_akhir)

    # Get query result
    result_prev = query_top_daignosa(tgl_awal_prev, datetime.strptime(tgl_akhir_prev, '%Y-%m-%d') + timedelta(days=1))
    result = query_top_daignosa(tgl_awal, tgl_akhir + timedelta(days=1))

    # Extract data by date (dict)
    tmp = [{"tanggal": row['TglPeriksa'], "kode_diagnosa": row['KdDiagnosa'], "diagnosa": row['NamaDiagnosa']} for row in result]
    tmp_prev = [{"tanggal": row['TglPeriksa'], "kode_diagnosa": row['KdDiagnosa'], "diagnosa": row['NamaDiagnosa']} for row in result_prev]

    # Extract data as (dataframe)
    cnts = count_values(tmp, 'diagnosa')
    cnts_prev = count_values(tmp_prev, 'diagnosa')
    data = [{"name": x, "value": y} for x, y in cnts.items()]
    data_prev = [{"name": x, "value": y} for x, y in cnts_prev.items()]

    # Define trend percentage
    for i in range(len(cnts)):
        percentage = None
        for j in range(len(cnts_prev)):
            if data[i]["name"] == data_prev[j]["name"]:
                percentage = (data[i]["value"] - data_prev[j]["value"]) / data[i]["value"]
            try:
                data[i]["trend"] = round(percentage, 3)
            except:
                data[i]["trend"] = percentage
        data[i]["predict"] = None
    
    # Define return result as a json
    result = {
        "judul": 'Top Diagnosa',
        "label": 'Pelayanan Pasien',
        "data": data,
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/pelayanan/pendidikan')
def pendidikan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'ini data Pendidikan'})


@pelayanan_bp.route('/pelayanan/pekerjaan')
def pekerjaan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'ini data Pekerjaan'})
