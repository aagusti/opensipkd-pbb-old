import os
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    Date,
    SmallInteger,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
    func,
    extract,
    case
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )
from sqlalchemy.sql.functions import concat
from ..models import (
    Base,
    DefaultModel,
    DBSession,
    osBaseModel,
    osExtendModel,
    User
    )
from ..models.pemda import (
    Unit, Urusan, UserUnit
    )
from ..tools import (
    create_now, get_settings,
    )

## Kecamatan ##
class Kecamatan(Base, osExtendModel):
    __tablename__  = 'kecamatans'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    disabled       = Column(SmallInteger, nullable=False, default=0)
    
## Kelurahan ##
class Kelurahan(Base, osExtendModel):
    __tablename__  = 'kelurahans'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    
    kecamatan_id   = Column(Integer, ForeignKey("reklame.kecamatans.id"), nullable=False)   
    disabled       = Column(SmallInteger, nullable=False, default=0)
    
    kecamatans     = relationship("Kecamatan", backref=backref('kelurahans'))
   
## Kelas Jalan ##
class KelasJalan(Base, osExtendModel):
    __tablename__  = 'kelas_jalans'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    nilai          = Column(Float)
    disabled       = Column(SmallInteger, nullable=False, default=0)
       
## Jalan ##
class Jalan(Base, osExtendModel):
    __tablename__  = 'jalans'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    
    kelas_jalan_id = Column(Integer, ForeignKey("reklame.kelas_jalans.id"), nullable=False) 
    disabled       = Column(SmallInteger, nullable=False, default=0)
    
    kelas_jalans   = relationship("KelasJalan", backref=backref('jalans'))
    
## Pemilik ##
class Pemilik(Base, osExtendModel):
    __tablename__  = 'pemiliks'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}   
    
    alamat     = Column(String(255))
    telephone  = Column(String(16))
    mobile     = Column(String(16))
    disabled   = Column(SmallInteger, nullable=False, default=0)

## Rekening ##
class Rekening(Base, osExtendModel):
    __tablename__  = 'rekenings'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
	
    id         = Column(Integer, primary_key=True)
    header_id  = Column(Integer, ForeignKey("reklame.rekenings.id"), nullable=True)	
    level_id   = Column(SmallInteger, default=1)
    is_summary = Column(SmallInteger, default=1)
    defsign    = Column(SmallInteger, default=1)
    disabled   = Column(SmallInteger, nullable=False, default=0)
	
    header     = relationship("Rekening", backref=backref('rekenings'), remote_side=[id])
	
    @classmethod
    def get_next_level(cls,id):
        return cls.query_id(id).first().level_id+1
     
## Ketinggian ##
class Ketinggian(Base, osExtendModel):
    __tablename__  = 'ketinggians'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    nilai          = Column(BigInteger)
    tinggi_min     = Column(Integer, default=0)
    tinggi_max     = Column(Integer, default=0)
    disabled       = Column(SmallInteger, nullable=False, default=0)
    
## Lokasi Pasang ##
class Lokasi(Base, osExtendModel):
    __tablename__  = 'lokasi_pasangs'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    nilai          = Column(Float)
    disabled       = Column(SmallInteger, nullable=False, default=0)
    
## Sudut Pandang ##
class Sudut(Base, osExtendModel):
    __tablename__  = 'sudut_pandangs'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    nilai          = Column(Float)
    disabled       = Column(SmallInteger, nullable=False, default=0) 
    
## Bahan ##
class Bahan(Base, osExtendModel):
    __tablename__  = 'bahans'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    nilai          = Column(Float)
    disabled       = Column(SmallInteger, nullable=False, default=0)

class FaktorLain(Base, osExtendModel):
    __tablename__  = 'faktor_lains'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    tarif          = Column(Float, nullable=False, default=0,
                        server_default='0')
    status         = Column(SmallInteger, nullable=False, default=1,
                        server_default='1')

class MasaPajak(Base, osExtendModel):
    __tablename__  = 'masa_pajaks'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    pembagi          = Column(Float, nullable=False, default=1,
                        server_default='1')
    accres          = Column(Float, nullable=False, default=0, 
                        server_default='0')
    status         = Column(SmallInteger, nullable=False, default=1,
                        server_default='1')
                        
## Jenis / Nilai Sewa Reklame ##
class JenisReklame(Base, osExtendModel):
    __tablename__  = 'jenis_reklame'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    rekening_id    = Column(Integer, ForeignKey("reklame.rekenings.id"), nullable=False) 
    tarif          = Column(Float, nullable=False, default=0,
                        server_default='0')
    status         = Column(SmallInteger, nullable=False, default=1,
                        server_default='1')
    masa_pajak_id = Column(Integer, ForeignKey("reklame.masa_pajaks.id"), nullable=False)
    rekenings      = relationship("Rekening", backref=backref('jenis_reklame'))
    masa_pajaks    = relationship("MasaPajak", backref=backref('jenis_reklame'))

## Jenis / Nilai Sewa Reklame ##
class Jenis(Base, osExtendModel):
    __tablename__  = 'jenis'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    
    rekening_id    = Column(Integer, ForeignKey("reklame.rekenings.id"), nullable=False) 
    nilai          = Column(BigInteger)
    disabled       = Column(SmallInteger, nullable=False, default=0)
    
    rekenings      = relationship("Rekening", backref=backref('jenis'))
    
class JenisNssr(Base, osExtendModel):
    __tablename__  = 'jenis_nssr'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',}
    status         = Column(SmallInteger, nullable=False, default=1,
                        server_default='1')
                        
## Nilai Satuan Strategis Reklame ##
class Nssr(Base, osExtendModel):
    __tablename__  = 'nssr'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    luas_min       = Column(Integer, default=0)
    luas_max       = Column(Integer, default=0)
    nilai          = Column(BigInteger)
    status         = Column(SmallInteger, nullable=False, default=0)
    jenis_nssr_id  = Column(Integer, ForeignKey("reklame.jenis_nssr.id"), nullable=False)
    jenis_nssr     = relationship("JenisNssr", backref=backref('nssr'))
    @classmethod
    def search_by_luas(cls, jenis_nssr_id,luas):
        return DBSession.query(cls).\
                  filter(cls.jenis_nssr_id==jenis_nssr_id,
                          cls.luas_min <= luas,
                          cls.luas_max > luas).first()

## Nilai Jual Objek Pajak Reklame ##
class Njop(Base, osExtendModel):
    __tablename__  = 'njop'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 
    luas_min       = Column(Integer, default=0)
    luas_max       = Column(Integer, default=0)
    nilai          = Column(BigInteger)
    jenis_reklame_id = Column(Integer, ForeignKey("reklame.jenis_reklame.id"), nullable=False)
    status         = Column(SmallInteger, nullable=False, default=0)
    jenis_reklame  =  relationship("JenisReklame", backref=backref('njop'))
    
    @classmethod
    def search_by_luas(cls, jenis_reklame_id,luas):
        return DBSession.query(cls).\
                  filter(cls.jenis_reklame_id==jenis_reklame_id,
                          cls.luas_min <= luas,
                          cls.luas_max > luas).first()
    
## Objek Pajak Reklame ##
class Reklame(Base, osExtendModel):
    __tablename__  = 'reklames'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 

    #kode            = Column(String(32)) || kecamatan + kelurahan + jalan + no_urut (007.001.001-0001)
    #kecamatan_id     = Column(Integer, ForeignKey("reklame.kecamatans.id"),     nullable=False) 
    #kelurahan_id     = Column(Integer, ForeignKey("reklame.kelurahans.id"),     nullable=False) 
    kelas_jalan_id         = Column(Integer, ForeignKey("reklame.kelas_jalans.id"), nullable=False)	
    no_urut          = Column(Integer, nullable=True)
    #rekening_id      = Column(Integer, ForeignKey("reklame.rekenings.id"),      nullable=False)
    jenis_reklame_id         = Column(Integer, ForeignKey("reklame.jenis_reklame.id"), nullable=False)
    lokasi_id        = Column(Integer, ForeignKey("reklame.lokasi_pasangs.id"), nullable=False)
    panjang          = Column(Float, default=1)
    lebar            = Column(Float, default=1)
    luas             = Column(Float, default=1) ## panjang * lebar * muka * jumlah_titik ##
    tinggi           = Column(Integer, default=1)
    muka             = Column(Integer, default=1)
    jumlah_titik     = Column(Integer, default=1) 
    sudut_id         = Column(Integer, ForeignKey("reklame.sudut_pandangs.id"), nullable=False)
    lahan_id         = Column(SmallInteger, nullable=False, default=1) # 1 'Pemda', 2 'Swasta'
    # pemilik_id       = Column(Integer, ForeignKey("reklame.pemiliks.id"),       nullable=False) 	
    # bersinar         = Column(SmallInteger, nullable=False, default=0) # 0 'Tidak', 1 'Ya'	
    # menempel         = Column(SmallInteger, nullable=False, default=0) # 0 'Tidak', 1 'Ya'	
    # dalam_ruang      = Column(SmallInteger, nullable=False, default=0) # 0 'Tidak', 1 'Ya'
    # koordinat_x      = Column(Float) 
    # koordinat_y      = Column(Float)
    status         = Column(SmallInteger, nullable=False, default=1)	
    #alamat         = Column(String(255)) 
    #ketinggian_id  = Column(Integer, ForeignKey("reklame.ketinggians.id"),    nullable=False)
    
    # pemiliks       = relationship("Pemilik",    backref=backref('reklames'))
    # rekenings      = relationship("Rekening",   backref=backref('reklames'))
    # jenis          = relationship("Jenis",      backref=backref('reklames'))
    # kecamatans     = relationship("Kecamatan",  backref=backref('reklames'))
    # kelurahans     = relationship("Kelurahan",  backref=backref('reklames'))
    # jalans         = relationship("Jalan",      backref=backref('reklames'))
    # lokasi_pasangs = relationship("Lokasi",     backref=backref('reklames'))
    # sudut_pandangs = relationship("Sudut",      backref=backref('reklames'))
    #ketinggians    = relationship("Ketinggian", backref=backref('reklames'))
   
    @classmethod
    def max_no_urut(cls, kel_id, jln_id):
        return DBSession.query(func.max(cls.no_urut).label('no_urut'))\
                .filter(cls.kelurahan_id == kel_id,
                        cls.jalan_id     == jln_id
                ).scalar() or 0
 	
## Transaksi Pajak Reklame ##
class Transaksi(Base, osExtendModel):
    __tablename__  = 'transaksis'
    __table_args__ = {'extend_existing':True, 'schema' : 'reklame',} 

    #reklame_id     = Column(Integer, ForeignKey("reklame.reklames.id"), nullable=False) 
    #kode_reklame   = Column(String(32))
    nama_pemohon   = Column(String(64))
    alamat_pemohon = Column(String(255)) 
    no_permohonan  = Column(String(32)) 
    id_permohonan  = Column(String(32))
    tgl_permohonan = Column(Date)
    no_sk_ipr      = Column(String(64))
    tgl_sk_ipr     = Column(Date)
    periode_awal   = Column(Date)
    periode_akhir  = Column(Date)
    npwpd          = Column(String(32))
    nama_wp        = Column(String(64))
    panjang          = Column(Float, default=1)
    lebar            = Column(Float, default=1)
    luas             = Column(Float, default=1) ## panjang * lebar * muka * jumlah_titik ##
    muka             = Column(Integer, default=1)
    jumlah_titik     = Column(Integer, default=1) 
    jml_luas             = Column(Float, default=1) ## panjang * lebar * muka * jumlah_titik ##
    tinggi           = Column(Integer, default=1)
    ketinggian_id    = Column(SmallInteger, ForeignKey("reklame.ketinggians.id"), nullable=False, default=1)
    ketinggian_ni   = Column(Float ,nullable=False, )
    jml_ketinggian   = Column(Float ,nullable=False, )
    
    masa_pajak_id = Column(Integer, ForeignKey("reklame.masa_pajaks.id") ,nullable=False, )
    pembagi       = Column(Float, nullable=False, )
    accres        = Column(Integer,nullable=False, )
    
    jenis_reklame_id = Column(Integer, ForeignKey("reklame.jenis_reklame.id") ,nullable=False, )
    jenis_reklame_ni = Column(Float ,nullable=False, )
    
    kelas_jalan_id   = Column(Integer, ForeignKey("reklame.kelas_jalans.id"), nullable=False)
    kelas_jalan_ni   = Column(Float ,nullable=False, )
    sudut_pandang_id = Column(Integer, ForeignKey("reklame.sudut_pandangs.id"),nullable=False)
    sudut_pandang_ni = Column(Float ,nullable=False, )
    lokasi_pasang_id = Column(Integer, ForeignKey("reklame.lokasi_pasangs.id"),nullable=False)
    lokasi_pasang_ni = Column(Float ,nullable=False, )

    faktor_lain_id   = Column(Integer, ForeignKey("reklame.faktor_lains.id") ,nullable=False,)
    faktor_lain_ni   = Column(Float ,nullable=False, )
    
    nssr_ni   = Column(Float ,nullable=False, )
    nssr              = Column(Float ,nullable=False, )
    jenis_nssr_id    = Column(Integer, ForeignKey("reklame.jenis_nssr.id") ,nullable=False, )
    nsr             = Column(Float ,nullable=False, )
    dasar          = Column(Float, default=0)
    tarif          = Column(Integer, default=0)
    pokok          = Column(Float, default=0)
    denda          = Column(Float, default=0)
    bunga          = Column(Float, default=0)
    kompensasi          = Column(Float, default=0)
    kenaikan          = Column(Float, default=0)
    lain          = Column(Float, default=0)
    jml_terhutang  = Column(Float, default=0)

    no_skpd        = Column(String(32))
    tgl_skpd       = Column(Date)
    no_bayar       = Column(String(32))
    tgl_bayar      = Column(Date)
    
    status       = Column(SmallInteger, nullable=False, default=0)
    jenis_reklames = relationship("JenisReklame",   backref=backref('transaksis'))
    kelas_jalans   = relationship("KelasJalan",     backref=backref('reklames'))
    jenis_nssr     = relationship("JenisNssr",     backref=backref('transaksis'))
    lokasi_pasangs = relationship("Lokasi",     backref=backref('transaksis'))
    sudut_pandangs = relationship("Sudut",      backref=backref('transaksis'))
    ketinggians    = relationship("Ketinggian", backref=backref('transaksis'))
    faktor_lains   = relationship("FaktorLain", backref=backref('transaksis'))
    masa_pajaks    = relationship("MasaPajak", backref=backref('transaksis'))
    #nopd           = Column(String(32))
    #tahun          = Column(Integer, nullable=False, default=0)
    #naskah         = Column(String(255)) 
    
    # pemiliks       = relationship("Pemilik",    backref=backref('reklames'))
    # rekenings      = relationship("Rekening",   backref=backref('reklames'))
    # jenis          = relationship("Jenis",      backref=backref('reklames'))
    # kecamatans     = relationship("Kecamatan",  backref=backref('reklames'))
    # kelurahans     = relationship("Kelurahan",  backref=backref('reklames'))
    # jalans         = relationship("Jalan",      backref=backref('reklames'))
    #    lahan_id         = Column(SmallInteger, ForeignKey("reklame.lahans.id"), nullable=False, default=1) # 1 'Pemda', 2 'Swasta'
    # pemilik_id       = Column(Integer, nullable=False) 	
    # bersinar         = Column(SmallInteger, nullable=False, default=0) # 0 'Tidak', 1 'Ya'	
    # menempel         = Column(SmallInteger, nullable=False, default=0) # 0 'Tidak', 1 'Ya'	
    # dalam_ruang      = Column(SmallInteger, nullable=False, default=0) # 0 'Tidak', 1 'Ya'
    
       