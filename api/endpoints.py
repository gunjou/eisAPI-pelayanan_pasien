from collections import Counter
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import text

from api.config import get_connection

pelayanan_bp = Blueprint("pelayanan", __name__)
engine = get_connection()


def get_default_date(tgl_awal, tgl_akhir):
    if tgl_awal == None:
        tgl_awal = datetime.today() - relativedelta(months=1)
        tgl_awal = tgl_awal.strftime('%Y-%m-%d')
    else:
        tgl_awal = datetime.strptime(tgl_awal, '%Y-%m-%d')

    if tgl_akhir == None:
        tgl_akhir = datetime.strptime(
            datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
    return tgl_awal, tgl_akhir


def count_values(data, param):
    cnt = Counter()
    for i in range(len(data)):
        cnt[data[i][param].lower().replace(' ', '_')] += 1
    return cnt


@pelayanan_bp.route('/card_pasien')
def card_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT bp.TglPelayanan, i.NamaInstalasi
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.Ruangan r
            ON bp.KdRuangan  = r.KdRuangan
            INNER JOIN dbo.Instalasi i
            ON r.KdInstalasi = i.KdInstalasi
            WHERE bp.TglPelayanan >= '{tgl_awal}'
            AND bp.TglPelayanan < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY bp.TglPelayanan ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPelayanan'],
            "instalasi": row['NamaInstalasi'].split("\r")[0]
        })
    result = {
        "judul": "Ruangan (Card Kunjungan)",
        "label": 'Pelayanan Pasien',
        "instalasi": count_values(data, 'instalasi'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


# Detail Card kunjungan (pop up table)
@pelayanan_bp.route('/detail_card_pasien')
def detail_card_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT DISTINCT bp.TglPelayanan, pd.NoPendaftaran, pd.NoCM, p.Title, p.NamaLengkap, p.TglLahir, p.JenisKelamin, p.Alamat
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.PasienDaftar pd
            ON bp.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN dbo.Pasien p
            ON pd.NoCM  = p.NoCM
            WHERE bp.TglPelayanan >= '{tgl_awal}'
            AND bp.TglPelayanan < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY bp.TglPelayanan ASC;"""))
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


@pelayanan_bp.route('/mutu_pelayanan')
def mutu_palayanan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'standar mutu pelayanan'})


@pelayanan_bp.route('/kelas_perawatan')
def kelas_perawatan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT bp.TglPelayanan, kp.DeskKelas as NamaKelas
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.KelasPelayanan kp
            ON bp.KdKelas = kp.KdKelas
            WHERE bp.TglPelayanan >= '{tgl_awal}'
            AND bp.TglPelayanan < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY bp.TglPelayanan ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPelayanan'],
            "kelas": row['NamaKelas']
        })
    result = {
        "judul": 'Kelas Perawatan',
        "label": 'Pelayanan Pasien',
        "kelas": count_values(data, 'kelas'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/kepuasan_pelayanan')
def kepuasan_pelayanan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'ini data Kepuasan Pelayanan'})


@pelayanan_bp.route('/kelompok_pasien')
def kelompok_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT bp.TglPelayanan, kp.JenisPasien as KelompokPasien
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.PasienDaftar pd
            ON bp.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN dbo.KelompokPasien kp
            ON pd.KdKelasAkhir = kp.KdKelompokPasien
            WHERE bp.TglPelayanan >= '{tgl_awal}'
            AND bp.TglPelayanan < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY bp.TglPelayanan ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPelayanan'],
            "kelompok": row['KelompokPasien']
        })
    result = {
        "judul": 'Kelompok Pasien',
        "label": 'Pelayanan Pasien',
        "kelompok": count_values(data, 'kelompok'),
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/pelayanan_dokter')
def pelayanan_dokter():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT rr.TglMasuk, rr.IdDokter, dp.NamaLengkap AS Dokter
            FROM dbo.RegistrasiRI rr
            INNER JOIN dbo.DataPegawai dp
            ON rr.IdDokter = dp.IdPegawai
            WHERE rr.TglMasuk >= '{tgl_awal}'
            AND rr.TglMasuk < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY rr.TglMasuk ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglMasuk'],
            "id_dokter": row['IdDokter'],
            "nama": row['Dokter']
        })
    cnt = Counter()
    for i in range(len(data)):
        cnt[data[i]['nama']] += 1
    result = {
        "judul": 'Pelayanan Dokter',
        "label": 'Pelayanan Pasien',
        "dokter": cnt,
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/top_diagnosa')
def top_diagnosa():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT rr.NoPendaftaran, pd.TglPeriksa, pd.KdDiagnosa, d.NamaDiagnosa
            FROM dbo.RegistrasiRI rr
            INNER JOIN dbo.PeriksaDiagnosa pd ON rr.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN dbo.Diagnosa d ON pd.KdDiagnosa = d.KdDiagnosa
            WHERE pd.TglPeriksa >= '{tgl_awal}'
            AND pd.TglPeriksa < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPeriksa ASC;"""))
    data = []
    for row in result:
        data.append({
            "no_pendaftaran": row['NoPendaftaran'],
            "tanggal": row['TglPeriksa'],
            "kode_diagnosa": row['KdDiagnosa'],
            "diagnosa": row['NamaDiagnosa']
        })
    cnt = Counter()
    for i in range(len(data)):
        cnt[data[i]['diagnosa']] += 1
    result = {
        "judul": 'Top Diagnosa',
        "label": 'Pelayanan Pasien',
        "diagnosa": cnt,
        "tgl_filter": {
            "tgl_awal": tgl_awal,
            "tgl_akhir": tgl_akhir
        }
    }
    return jsonify(result)


@pelayanan_bp.route('/pendidikan')
def pendidikan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'ini data Pendidikan'})


@pelayanan_bp.route('/pekerjaan')
def pekerjaan():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)

    return jsonify({'response': 'ini data Pekerjaan'})
