from sqlalchemy import text

from api.config import get_connection

engine = get_connection()


def query_card_pasien(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT bp.TglPelayanan, i.NamaInstalasi
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.Ruangan r
            ON bp.KdRuangan  = r.KdRuangan
            INNER JOIN dbo.Instalasi i
            ON r.KdInstalasi = i.KdInstalasi
            WHERE bp.TglPelayanan >= '{start_date}'
            AND bp.TglPelayanan < '{end_date}'
            ORDER BY bp.TglPelayanan ASC;"""))
    return result


def query_detail_card_pasien(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT DISTINCT bp.TglPelayanan, pd.NoPendaftaran, pd.NoCM, p.Title, p.NamaLengkap, p.TglLahir, p.JenisKelamin, p.Alamat
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.PasienDaftar pd
            ON bp.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN dbo.Pasien p
            ON pd.NoCM  = p.NoCM
            WHERE bp.TglPelayanan >= '{start_date}'
            AND bp.TglPelayanan < '{end_date}'
            ORDER BY bp.TglPelayanan ASC;"""))
    return result


def query_kelas_perawatan(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT bp.TglPelayanan, kp.DeskKelas as NamaKelas
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.KelasPelayanan kp
            ON bp.KdKelas = kp.KdKelas
            WHERE bp.TglPelayanan >= '{start_date}'
            AND bp.TglPelayanan < '{end_date}'
            ORDER BY bp.TglPelayanan ASC;"""))
    return result


def query_kelompok_pasien(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT bp.TglPelayanan, kp.JenisPasien as KelompokPasien
            FROM dbo.BiayaPelayanan bp
            INNER JOIN dbo.PasienDaftar pd
            ON bp.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN dbo.KelompokPasien kp
            ON pd.KdKelasAkhir = kp.KdKelompokPasien
            WHERE bp.TglPelayanan >= '{start_date}'
            AND bp.TglPelayanan < '{end_date}'
            ORDER BY bp.TglPelayanan ASC;"""))
    return result


def query_pelayanan_dokter(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT rr.TglMasuk, rr.IdDokter, dp.NamaLengkap AS Dokter
            FROM dbo.RegistrasiRI rr
            INNER JOIN dbo.DataPegawai dp
            ON rr.IdDokter = dp.IdPegawai
            WHERE rr.TglMasuk >= '{start_date}'
            AND rr.TglMasuk < '{end_date}'
            ORDER BY rr.TglMasuk ASC;"""))
    return result


def query_top_daignosa(start_date, end_date):
    result = engine.execute(
        text(f"""SELECT rr.NoPendaftaran, pd.TglPeriksa, pd.KdDiagnosa, d.NamaDiagnosa
            FROM dbo.RegistrasiRI rr
            INNER JOIN dbo.PeriksaDiagnosa pd ON rr.NoPendaftaran = pd.NoPendaftaran
            INNER JOIN dbo.Diagnosa d ON pd.KdDiagnosa = d.KdDiagnosa
            WHERE pd.TglPeriksa >= '{start_date}'
            AND pd.TglPeriksa < '{end_date}'
            ORDER BY pd.TglPeriksa ASC;"""))
    return result