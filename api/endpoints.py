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
        tgl_akhir = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    else:
        tgl_akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
    return tgl_awal, tgl_akhir


@pelayanan_bp.route('/card_pasien')
def card_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pd.TglPendaftaran, r.NamaRuangan
            FROM rsudtasikmalaya.dbo.PasienDaftar pd
            INNER JOIN rsudtasikmalaya.dbo.Ruangan r
            ON pd.KdRuanganAkhir  = r.KdRuangan  
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
            "ruangan": row['NamaRuangan'].split("\r")[0],
            "judul": "Ruangan (Card Kunjungan)",
            "label": 'Pelayanan Pasien'
            })
    return jsonify(data)


# Detail Card kunjungan (pop up table)
@pelayanan_bp.route('/detail_card_pasien')
def detail_card_pasien():
    tgl_awal = request.args.get('tgl_awal')
    tgl_akhir = request.args.get('tgl_akhir')
    tgl_awal, tgl_akhir = get_default_date(tgl_awal, tgl_akhir)
    result = engine.execute(
        text(
            f"""SELECT pd.TglPendaftaran, pd.NoPendaftaran, pd.NoCM, p.Title, p.NamaLengkap, p.TglLahir, p.JenisKelamin, p.Alamat
            FROM rsudtasikmalaya.dbo.PasienDaftar pd
            INNER JOIN rsudtasikmalaya.dbo.Pasien p
            ON pd.NoCM  = p.NoCM
            WHERE pd.TglPendaftaran >= '{tgl_awal}'
            AND pd.TglPendaftaran < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY pd.TglPendaftaran ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPendaftaran'],
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
            "kelas": row['NamaKelas'],
            "judul": "Kelas Perawatan",
            "label": 'Pelayanan Pasien'
            })
    return jsonify(data)


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
            FROM rsudtasikmalaya.dbo.BiayaPelayanan bp
            INNER JOIN rsudtasikmalaya.dbo.PasienDaftar pd
            ON bp.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN rsudtasikmalaya.dbo.KelompokPasien kp
            ON pd.KdKelasAkhir = kp.KdKelompokPasien
            WHERE bp.TglPelayanan >= '{tgl_awal}'
            AND bp.TglPelayanan < '{tgl_akhir + timedelta(days=1)}'
            ORDER BY bp.TglPelayanan ASC;"""))
    data = []
    for row in result:
        data.append({
            "tanggal": row['TglPelayanan'],
            "kelompok": row['KelompokPasien'],
            "judul": 'Kelompok Pasien',
            "label": 'Pelayanan Pasien'
        })
    return jsonify(data)


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
            "nama": row['Dokter'],
            "judul": 'Pelayanan Dokter',
            "label": 'Pelayanan Pasien'
        })
    return jsonify(data)


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
            "diagnosa": row['NamaDiagnosa'],
            "judul": 'Top Diagnosa',
            "label": 'Pelayanan Pasien'
        })
    return jsonify(data)


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
