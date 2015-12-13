import os
import unittest
import os.path
import uuid
import urlparse

from datetime import datetime
from sqlalchemy import *
from sqlalchemy.sql.expression import literal_column
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
    
from datatables import ColumnDT, DataTables

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver

from ...models import DBSession, User
from ...models.reklame import *
from ...models.pemda import *
from ...views.base_view import _DTstrftime
from datetime import datetime

def get_rpath(filename):
    a = AssetResolver('reklame')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
angka = {1:'satu',2:'dua',3:'tiga',4:'empat',5:'lima',6:'enam',7:'tujuh',\
         8:'delapan',9:'sembilan'}
b = ' puluh '
c = ' ratus '
d = ' ribu '
e = ' juta '
f = ' milyar '
g = ' triliun '
def Terbilang(x):   
    y = str(x)         
    n = len(y)        
    if n <= 3 :        
        if n == 1 :   
            if y == '0' :   
                return ''   
            else :         
                return angka[int(y)]   
        elif n == 2 :
            if y[0] == '1' :                
                if y[1] == '1' :
                    return 'sebelas'
                elif y[0] == '0':
                    x = y[1]
                    return Terbilang(x)
                elif y[1] == '0' :
                    return 'sepuluh'
                else :
                    return angka[int(y[1])] + ' belas'
            elif y[0] == '0' :
                x = y[1]
                return Terbilang(x)
            else :
                x = y[1]
                return angka[int(y[0])] + b + Terbilang(x)
        else :
            if y[0] == '1' :
                x = y[1:]
                return 'seratus ' + Terbilang(x)
            elif y[0] == '0' : 
                x = y[1:]
                return Terbilang(x)
            else :
                x = y[1:]
                return angka[int(y[0])] + c + Terbilang(x)
    elif 3< n <=6 :
        p = y[-3:]
        q = y[:-3]
        if q == '1' :
            return 'seribu' + Terbilang(p)
        elif q == '000' :
            return Terbilang(p)
        else:
            return Terbilang(q) + d + Terbilang(p)
    elif 6 < n <= 9 :
        r = y[-6:]
        s = y[:-6]
        return Terbilang(s) + e + Terbilang(r)
    elif 9 < n <= 12 :
        t = y[-9:]
        u = y[:-9]
        return Terbilang(u) + f + Terbilang(t)
    else:
        v = y[-12:]
        w = y[:-12]
        return Terbilang(w) + g + Terbilang(v)

class ViewReklameLap():
    def __init__(self, context, request):
        self.context = context
        self.request = request
		
    # Laporan Reklame
    @view_config(route_name="reklame-opreklame-report", renderer="templates/report_reklame/reklame_report.pt", permission="reklame-opreklame-report")
    def reklame(self):
        params = self.request.params
        return dict()

    @view_config(route_name="reklame-opreklame-report-act", renderer="json", permission="reklame-opreklame-report-act")
    def reklame_act(self):
        global mulai, selesai, unit
        req      = self.request
        params   = req.params
        url_dict = req.matchdict
 
        unit         = 'unit'         in params and params['unit']         or 0
        rek          = 'rek'          in params and params['rek']        or 0
        jenis        = 'jenis'        in params and params['jenis']        or 0
        mulai        = 'mulai'        in params and params['mulai']        or 0
        selesai      = 'selesai'      in params and params['selesai']      or 0
        opreklame_id = 'opreklame_id' in params and params['opreklame_id'] or 0
        transaksi_id = 'transaksi_id' in params and params['transaksi_id'] or 0
        
		# Khusus untuk modul master #
        kec_id       = 'kec_id'       in params and params['kec_id']       or 0
        kel_id       = 'kel_id'       in params and params['kel_id']       or 0
        kls_jln_id   = 'kls_jln_id'   in params and params['kls_jln_id']   or 0
        jalan_id     = 'jalan_id'     in params and params['jalan_id']     or 0
        pemilik_id   = 'pemilik_id'   in params and params['pemilik_id']   or 0
        tinggi_id    = 'tinggi_id'    in params and params['tinggi_id']    or 0
        nsr_id       = 'nsr_id'       in params and params['nsr_id']       or 0
        njop_id      = 'njop_id'      in params and params['njop_id']      or 0
        strategis_id = 'strategis_id' in params and params['strategis_id'] or 0
        lokasi_id    = 'lokasi_id'    in params and params['lokasi_id']    or 0
        sudut_id     = 'sudut_id'     in params and params['sudut_id']     or 0
        bahan_id     = 'bahan_id'     in params and params['bahan_id']     or 0
		
        if url_dict['act']=='laporan' :
            # Jenis laporan pajak reklame #
            if jenis == '1' :
                query = DBSession.query(Reklame.kode.label('op_kd'),
                                        Reklame.nama.label('op_nm'),
                                        Pemilik.nama.label('pem_nm'),
                                        Rekening.nama.label('rek_nm'),
                                        Kelurahan.nama.label('kel_nm'),
                                        Jalan.nama.label('jln_nm'),
                                        Jenis.nilai.label('op_nsr'),
                                        Reklame.muka.label('op_mk'),
                                        Reklame.jumlah_titik.label('op_jml'),
                                        Reklame.luas.label('op_ls'),
                                        case([(Reklame.disabled==0,"N"),
                                              (Reklame.disabled==1,"Y")], else_="").label('dis'),
                                ).join(Pemilik, Rekening, Jalan, Kelurahan
                                ).filter(Reklame.rekening_id   == rek,
                                         Reklame.rekening_id   == Rekening.id, 
                                         Reklame.pemilik_id    == Pemilik.id, 
                                         Reklame.kelurahan_id  == Kelurahan.id, 
                                         Reklame.jalan_id      == Jalan.id,
                                         Reklame.jenis_id      == Jenis.id, 
                                ).order_by(Reklame.kode, 	 			 	 										 
                                ).all()
                generator = laporan_objek_Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                query = DBSession.query(Transaksi.kode.label('tr_kd'),
                                        Transaksi.nama.label('tr_nm'),
                                        Transaksi.kode_reklame.label('tr_nopd'),
                                        Transaksi.npwpd.label('tr_npwpd'),
                                        Transaksi.no_skpd.label('tr_skpd'),
                                        Transaksi.no_bayar.label('tr_byr'),
                                        Transaksi.no_sk_ipr.label('tr_ipr'),
                                        Transaksi.periode_awal.label('tr_aw'),
                                        Transaksi.periode_akhir.label('tr_ak'),
                                        Transaksi.jml_bayar.label('tr_jml'),
                                        Reklame.nama.label('op_nm'),
                                        case([(Transaksi.disabled==0,"N"),
                                              (Transaksi.disabled==1,"Y")], else_="").label('dis'),
                                ).join(Reklame
                                ).filter(Transaksi.reklame_id == Reklame.id,
                                         or_(Transaksi.periode_awal.between(mulai,selesai),
                                             Transaksi.periode_akhir.between(mulai,selesai)),
                                ).order_by(Transaksi.kode, 	 					 	 										 
                                ).all()
                generator = laporan_transaksi_Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            
        elif url_dict['act']=='opreklame' :
            query = DBSession.query(Reklame.kode.label('op_kd'),
                                    Reklame.nama.label('op_nm'),
                                    Pemilik.nama.label('pem_nm'),
                                    Rekening.nama.label('rek_nm'),
                                    Kelurahan.nama.label('kel_nm'),
                                    Jalan.nama.label('jln_nm'),
                                    Jenis.nilai.label('op_nsr'),
                                    Reklame.muka.label('op_mk'),
                                    Reklame.jumlah_titik.label('op_jml'),
                                    Reklame.luas.label('op_ls'),
                                    case([(Reklame.disabled==0,"N"),
                                          (Reklame.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Pemilik, Rekening, Jalan, Kelurahan
                            ).filter(Reklame.id           == opreklame_id,
                                     Reklame.pemilik_id   == Pemilik.id, 
                                     Reklame.rekening_id  == Rekening.id, 
                                     Reklame.kelurahan_id == Kelurahan.id, 
                                     Reklame.jalan_id     == Jalan.id,   
                                     Reklame.jenis_id     == Jenis.id,                           
                            ).order_by(Reklame.kode, 	 			 	 										 
                            ).all()
            generator = opreklame_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        elif url_dict['act']=='opreklame2' :
            query = DBSession.query(Reklame.kode.label('op_kd'),
                                    Reklame.nama.label('op_nm'),
                                    Pemilik.nama.label('pem_nm'),
                                    Rekening.nama.label('rek_nm'),
                                    Kelurahan.nama.label('kel_nm'),
                                    Jalan.nama.label('jln_nm'),
                                    Jenis.nilai.label('op_nsr'),
                                    Reklame.muka.label('op_mk'),
                                    Reklame.jumlah_titik.label('op_jml'),
                                    Reklame.luas.label('op_ls'),
                                    case([(Reklame.disabled==0,"N"),
                                          (Reklame.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Pemilik, Rekening, Jalan, Kelurahan
                            ).filter(Reklame.pemilik_id   == Pemilik.id, 
                                     Reklame.rekening_id  == Rekening.id, 
                                     Reklame.kelurahan_id == Kelurahan.id, 
                                     Reklame.jalan_id     == Jalan.id, 
                                     Reklame.jenis_id     == Jenis.id,                                  
                            ).order_by(Reklame.kode, 	 					 	 										 
                            ).all()
            generator = opreklame2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        elif url_dict['act']=='transaksi' :
            query = DBSession.query(Transaksi.kode.label('tr_kd'),
                                    Transaksi.nama.label('tr_nm'),
                                    Transaksi.kode_reklame.label('tr_nopd'),
                                    Transaksi.npwpd.label('tr_npwpd'),
                                    Transaksi.no_skpd.label('tr_skpd'),
                                    Transaksi.no_bayar.label('tr_byr'),
                                    Transaksi.no_sk_ipr.label('tr_ipr'),
                                    Transaksi.periode_awal.label('tr_aw'),
                                    Transaksi.periode_akhir.label('tr_ak'),
                                    Transaksi.jml_bayar.label('tr_jml'),
                                    Reklame.nama.label('op_nm'),
                                    case([(Transaksi.disabled==0,"N"),
                                          (Transaksi.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Reklame
                            ).filter(Transaksi.id == transaksi_id,
                                     Transaksi.reklame_id == Reklame.id,                            
                            ).order_by(Transaksi.kode, 	 					 	 										 
                            ).all()
            generator = transaksi_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
            
        elif url_dict['act']=='transaksi2' :
            query = DBSession.query(Transaksi.kode.label('tr_kd'),
                                    Transaksi.nama.label('tr_nm'),
                                    Transaksi.kode_reklame.label('tr_nopd'),
                                    Transaksi.npwpd.label('tr_npwpd'),
                                    Transaksi.no_skpd.label('tr_skpd'),
                                    Transaksi.no_bayar.label('tr_byr'),
                                    Transaksi.no_sk_ipr.label('tr_ipr'),
                                    Transaksi.periode_awal.label('tr_aw'),
                                    Transaksi.periode_akhir.label('tr_ak'),
                                    Transaksi.jml_bayar.label('tr_jml'),
                                    Reklame.nama.label('op_nm'),
                                    case([(Transaksi.disabled==0,"N"),
                                          (Transaksi.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Reklame
                            ).filter(Transaksi.reklame_id == Reklame.id,                       
                            ).order_by(Transaksi.kode, 	 					 	 										 
                            ).all()
            generator = transaksi2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
		
        ###############################		
		## Khusus untuk modul master ##
        ###############################	
		
        elif url_dict['act']=='kecamatan' :
            query = DBSession.query(Kecamatan.kode.label('kec_kd'),
                                    Kecamatan.nama.label('kec_nm'),
                                    case([(Kecamatan.disabled==0,"N"),
                                          (Kecamatan.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Kecamatan.id == kec_id, 	  	 		 										 
                            ).all()
            generator = master_kecamatan_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
		
        elif url_dict['act']=='kecamatan2' :
            query = DBSession.query(Kecamatan.kode.label('kec_kd'),
                                    Kecamatan.nama.label('kec_nm'),
                                    case([(Kecamatan.disabled==0,"N"),
                                          (Kecamatan.disabled==1,"Y")], else_="").label('dis'),	
                            ).order_by(Kecamatan.kode, 				 		 										 
                            ).all()
            generator = master_kecamatan2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
		
        elif url_dict['act']=='kelurahan' :
            query = DBSession.query(Kelurahan.kode.label('kel_kd'),
                                    Kelurahan.nama.label('kel_nm'),
                                    Kecamatan.nama.label('kec_nm'),
                                    case([(Kelurahan.disabled==0,"N"),
                                          (Kelurahan.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Kecamatan
                            ).filter(Kelurahan.id == kel_id, 
                                     Kelurahan.kecamatan_id == Kecamatan.id                            
                            ).all()
            generator = master_kelurahan_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response	
		
        elif url_dict['act']=='kelurahan2' :
            query = DBSession.query(Kelurahan.kode.label('kel_kd'),
                                    Kelurahan.nama.label('kel_nm'),
                                    Kecamatan.nama.label('kec_nm'),
                                    case([(Kelurahan.disabled==0,"N"),
                                          (Kelurahan.disabled==1,"Y")], else_="").label('dis'),	
                            ).join(Kecamatan
                            ).filter(Kelurahan.kecamatan_id == Kecamatan.id 	
                            ).order_by(Kelurahan.kode, 	 				 										 
                            ).all()
            generator = master_kelurahan2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='kelas_jalan' :
            query = DBSession.query(KelasJalan.kode.label('kls_kd'),
                                    KelasJalan.nama.label('kls_nm'),
                                    KelasJalan.nilai.label('kls_ni'),
                                    case([(KelasJalan.disabled==0,"N"),
                                          (KelasJalan.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(KelasJalan.id == kls_jln_id, 						
                            ).all()
            generator = master_kelas_jalan_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='kelas_jalan2' :
            query = DBSession.query(KelasJalan.kode.label('kls_kd'),
                                    KelasJalan.nama.label('kls_nm'),
                                    KelasJalan.nilai.label('kls_ni'),
                                    case([(KelasJalan.disabled==0,"N"),
                                          (KelasJalan.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(KelasJalan.kode, 						
                            ).all()
            generator = master_kelas_jalan2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
		
        elif url_dict['act']=='jalan' :
            query = DBSession.query(Jalan.kode.label('jln_kd'),
                                    Jalan.nama.label('jln_nm'),
                                    KelasJalan.nama.label('kls_nm'),
                                    case([(Jalan.disabled==0,"N"),
                                          (Jalan.disabled==1,"Y")], else_="").label('dis'),
                            ).join(KelasJalan
                            ).filter(Jalan.id == jalan_id, 
                                     Jalan.kelas_jalan_id == KelasJalan.id                            
                            ).all()
            generator = master_jalan_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response	
		
        elif url_dict['act']=='jalan2' :
            query = DBSession.query(Jalan.kode.label('jln_kd'),
                                    Jalan.nama.label('jln_nm'),
                                    KelasJalan.nama.label('kls_nm'),
                                    case([(Jalan.disabled==0,"N"),
                                          (Jalan.disabled==1,"Y")], else_="").label('dis'),
                            ).join(KelasJalan
                            ).filter(Jalan.kelas_jalan_id == KelasJalan.id 	
                            ).order_by(Jalan.kode, 	 				 										 
                            ).all()
            generator = master_jalan2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='pemilik' :
            query = DBSession.query(Pemilik.kode.label('p_kd'),
                                    Pemilik.nama.label('p_nm'),
                                    Pemilik.alamat.label('p_almt'),
                                    Pemilik.telephone.label('p_nt'),
                                    Pemilik.mobile.label('p_nf'),
                                    case([(Pemilik.disabled==0,"N"),
                                          (Pemilik.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Pemilik.id == pemilik_id, 						
                            ).all()
            generator = master_pemilik_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='pemilik2' :
            query = DBSession.query(Pemilik.kode.label('p_kd'),
                                    Pemilik.nama.label('p_nm'),
                                    Pemilik.alamat.label('p_almt'),
                                    Pemilik.telephone.label('p_nt'),
                                    Pemilik.mobile.label('p_nf'),
                                    case([(Pemilik.disabled==0,"N"),
                                          (Pemilik.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Pemilik.nama, 						
                            ).all()
            generator = master_pemilik2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response	
			
        elif url_dict['act']=='ketinggian' :
            query = DBSession.query(Ketinggian.kode.label('ket_kd'),
                                    Ketinggian.nama.label('ket_nm'),
                                    Ketinggian.nilai.label('ket_ni'),
                                    Ketinggian.tinggi_min.label('ket_min'),
                                    Ketinggian.tinggi_max.label('ket_max'),
                                    case([(Ketinggian.disabled==0,"N"),
                                          (Ketinggian.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Ketinggian.id == tinggi_id, 						
                            ).all()
            generator = master_ketinggian_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='ketinggian2' :
            query = DBSession.query(Ketinggian.kode.label('ket_kd'),
                                    Ketinggian.nama.label('ket_nm'),
                                    Ketinggian.nilai.label('ket_ni'),
                                    Ketinggian.tinggi_min.label('ket_min'),
                                    Ketinggian.tinggi_max.label('ket_max'),
                                    case([(Ketinggian.disabled==0,"N"),
                                          (Ketinggian.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Ketinggian.kode, 						
                            ).all()
            generator = master_ketinggian2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response			
		
        elif url_dict['act']=='nsr' :
            query = DBSession.query(Jenis.kode.label('nsr_kd'),
                                    Jenis.nama.label('nsr_nm'),
                                    Jenis.nilai.label('nsr_ni'),
                                    Rekening.nama.label('rek_nm'),
                                    case([(Jenis.disabled==0,"N"),
                                          (Jenis.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Rekening
                            ).filter(Jenis.id == nsr_id, 
                                     Jenis.rekening_id == Rekening.id                            
                            ).all()
            generator = master_nsr_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response	
		
        elif url_dict['act']=='nsr2' :
            query = DBSession.query(Jenis.kode.label('nsr_kd'),
                                    Jenis.nama.label('nsr_nm'),
                                    Jenis.nilai.label('nsr_ni'),
                                    Rekening.nama.label('rek_nm'),
                                    case([(Jenis.disabled==0,"N"),
                                          (Jenis.disabled==1,"Y")], else_="").label('dis'),
                            ).join(Rekening
                            ).filter(Jenis.rekening_id == Rekening.id 	
                            ).order_by(Jenis.kode, 	 				 										 
                            ).all()
            generator = master_nsr2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='strategis' :
            query = DBSession.query(Nssr.kode.label('kls_kd'),
                                    Nssr.nama.label('kls_nm'),
                                    Nssr.nilai.label('kls_ni'),
                                    Nssr.luas_min.label('kls_min'),
                                    Nssr.luas_max.label('kls_max'),
                                    case([(Nssr.disabled==0,"N"),
                                          (Nssr.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Nssr.id == strategis_id, 						
                            ).all()
            generator = master_strategis_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='strategis2' :
            query = DBSession.query(Nssr.kode.label('kls_kd'),
                                    Nssr.nama.label('kls_nm'),
                                    Nssr.nilai.label('kls_ni'),
                                    Nssr.luas_min.label('kls_min'),
                                    Nssr.luas_max.label('kls_max'),
                                    case([(Nssr.disabled==0,"N"),
                                          (Nssr.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Nssr.kode, 						
                            ).all()
            generator = master_strategis2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='njop' :
            query = DBSession.query(Njop.kode.label('kls_kd'),
                                    Njop.nama.label('kls_nm'),
                                    Njop.nilai.label('kls_ni'),
                                    Njop.luas_min.label('kls_min'),
                                    Njop.luas_max.label('kls_max'),
                                    case([(Njop.disabled==0,"N"),
                                          (Njop.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Njop.id == njop_id, 						
                            ).all()
            generator = master_njop_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='njop2' :
            query = DBSession.query(Njop.kode.label('kls_kd'),
                                    Njop.nama.label('kls_nm'),
                                    Njop.nilai.label('kls_ni'),
                                    Njop.luas_min.label('kls_min'),
                                    Njop.luas_max.label('kls_max'),
                                    case([(Njop.disabled==0,"N"),
                                          (Njop.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Njop.kode, 						
                            ).all()
            generator = master_njop2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='lokasi' :
            query = DBSession.query(Lokasi.kode.label('kls_kd'),
                                    Lokasi.nama.label('kls_nm'),
                                    Lokasi.nilai.label('kls_ni'),
                                    case([(Lokasi.disabled==0,"N"),
                                          (Lokasi.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Lokasi.id == lokasi_id, 						
                            ).all()
            generator = master_lokasi_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='lokasi2' :
            query = DBSession.query(Lokasi.kode.label('kls_kd'),
                                    Lokasi.nama.label('kls_nm'),
                                    Lokasi.nilai.label('kls_ni'),
                                    case([(Lokasi.disabled==0,"N"),
                                          (Lokasi.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Lokasi.kode, 						
                            ).all()
            generator = master_lokasi2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='sudut' :
            query = DBSession.query(Sudut.kode.label('kls_kd'),
                                    Sudut.nama.label('kls_nm'),
                                    Sudut.nilai.label('kls_ni'),
                                    case([(Sudut.disabled==0,"N"),
                                          (Sudut.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Sudut.id == sudut_id, 						
                            ).all()
            generator = master_sudut_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='sudut2' :
            query = DBSession.query(Sudut.kode.label('kls_kd'),
                                    Sudut.nama.label('kls_nm'),
                                    Sudut.nilai.label('kls_ni'),
                                    case([(Sudut.disabled==0,"N"),
                                          (Sudut.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Sudut.kode, 						
                            ).all()
            generator = master_sudut2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
			
        elif url_dict['act']=='bahan' :
            query = DBSession.query(Bahan.kode.label('kls_kd'),
                                    Bahan.nama.label('kls_nm'),
                                    Bahan.nilai.label('kls_ni'),
                                    case([(Bahan.disabled==0,"N"),
                                          (Bahan.disabled==1,"Y")], else_="").label('dis'),
                            ).filter(Bahan.id == bahan_id, 						
                            ).all()
            generator = master_bahan_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response		
			
        elif url_dict['act']=='bahan2' :
            query = DBSession.query(Bahan.kode.label('kls_kd'),
                                    Bahan.nama.label('kls_nm'),
                                    Bahan.nilai.label('kls_ni'),
                                    case([(Bahan.disabled==0,"N"),
                                          (Bahan.disabled==1,"Y")], else_="").label('dis'),
                            ).order_by(Bahan.kode, 						
                            ).all()
            generator = master_bahan2_Generator()
            pdf = generator.generate(query)
            response=req.response
            response.content_type="application/pdf"
            response.content_disposition='filename=output.pdf' 
            response.write(pdf)
            return response
	
			
######################################################################			
#########################  JASPER GENERATOR  #########################
######################################################################	
		
# Objek Pajak #
class opreklame_Generator(JasperGenerator):
    def __init__(self):
        super(opreklame_Generator, self).__init__()
        self.reportname = get_rpath('Transaksi_objek_pajak.jrxml')
        self.xpath = '/opreklame/objek_pajak'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'objek_pajak')
            ET.SubElement(xml_greeting, "op_kd").text   = row.op_kd
            ET.SubElement(xml_greeting, "op_nm").text   = row.op_nm
            ET.SubElement(xml_greeting, "pem_nm").text  = row.pem_nm
            ET.SubElement(xml_greeting, "rek_nm").text  = row.rek_nm
            ET.SubElement(xml_greeting, "kel_nm").text  = row.kel_nm
            ET.SubElement(xml_greeting, "jln_nm").text  = row.jln_nm
            ET.SubElement(xml_greeting, "op_nsr").text  = unicode(row.op_nsr)
            ET.SubElement(xml_greeting, "op_mk").text   = unicode(row.op_mk)
            ET.SubElement(xml_greeting, "op_jml").text  = unicode(row.op_jml)
            ET.SubElement(xml_greeting, "op_ls").text   = unicode(row.op_ls)
            ET.SubElement(xml_greeting, "dis").text     = unicode(row.dis)
        return self.root		
        
# Objek Pajak (all) #
class opreklame2_Generator(JasperGenerator):
    def __init__(self):
        super(opreklame2_Generator, self).__init__()
        self.reportname = get_rpath('Transaksi_objek_pajak_all.jrxml')
        self.xpath = '/opreklame/objek_pajak_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'objek_pajak_all')
            ET.SubElement(xml_greeting, "op_kd").text   = row.op_kd
            ET.SubElement(xml_greeting, "op_nm").text   = row.op_nm
            ET.SubElement(xml_greeting, "pem_nm").text  = row.pem_nm
            ET.SubElement(xml_greeting, "rek_nm").text  = row.rek_nm
            ET.SubElement(xml_greeting, "kel_nm").text  = row.kel_nm
            ET.SubElement(xml_greeting, "jln_nm").text  = row.jln_nm
            ET.SubElement(xml_greeting, "op_nsr").text  = unicode(row.op_nsr)
            ET.SubElement(xml_greeting, "op_mk").text   = unicode(row.op_mk)
            ET.SubElement(xml_greeting, "op_jml").text  = unicode(row.op_jml)
            ET.SubElement(xml_greeting, "op_ls").text   = unicode(row.op_ls)
            ET.SubElement(xml_greeting, "dis").text     = unicode(row.dis)
        return self.root	
        
# Transaksi Pajak #
class transaksi_Generator(JasperGenerator):
    def __init__(self):
        super(transaksi_Generator, self).__init__()
        self.reportname = get_rpath('Transaksi_pajak.jrxml')
        self.xpath = '/opreklame/transaksi'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'transaksi')
            ET.SubElement(xml_greeting, "tr_kd").text     = row.tr_kd
            ET.SubElement(xml_greeting, "tr_nm").text     = row.tr_nm
            ET.SubElement(xml_greeting, "tr_nopd").text   = row.tr_nopd
            ET.SubElement(xml_greeting, "tr_npwpd").text  = row.tr_npwpd
            ET.SubElement(xml_greeting, "tr_skpd").text   = row.tr_skpd
            ET.SubElement(xml_greeting, "tr_byr").text    = row.tr_byr
            ET.SubElement(xml_greeting, "tr_ipr").text    = row.tr_ipr
            ET.SubElement(xml_greeting, "tr_aw").text     = unicode(row.tr_aw)
            ET.SubElement(xml_greeting, "tr_ak").text     = unicode(row.tr_ak)
            ET.SubElement(xml_greeting, "tr_jml").text    = unicode(row.tr_jml)
            ET.SubElement(xml_greeting, "op_nm").text     = row.op_nm
            ET.SubElement(xml_greeting, "dis").text       = unicode(row.dis)
        return self.root
        
# Transaksi Pajak (all) #
class transaksi2_Generator(JasperGenerator):
    def __init__(self):
        super(transaksi2_Generator, self).__init__()
        self.reportname = get_rpath('Transaksi_pajak_all.jrxml')
        self.xpath = '/opreklame/transaksi_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'transaksi_all')
            ET.SubElement(xml_greeting, "tr_kd").text     = row.tr_kd
            ET.SubElement(xml_greeting, "tr_nm").text     = row.tr_nm
            ET.SubElement(xml_greeting, "tr_nopd").text   = row.tr_nopd
            ET.SubElement(xml_greeting, "tr_npwpd").text  = row.tr_npwpd
            ET.SubElement(xml_greeting, "tr_skpd").text   = row.tr_skpd
            ET.SubElement(xml_greeting, "tr_byr").text    = row.tr_byr
            ET.SubElement(xml_greeting, "tr_ipr").text    = row.tr_ipr
            ET.SubElement(xml_greeting, "tr_aw").text     = unicode(row.tr_aw)
            ET.SubElement(xml_greeting, "tr_ak").text     = unicode(row.tr_ak)
            ET.SubElement(xml_greeting, "tr_jml").text    = unicode(row.tr_jml)
            ET.SubElement(xml_greeting, "op_nm").text     = row.op_nm
            ET.SubElement(xml_greeting, "dis").text       = unicode(row.dis)
        return self.root	
        
# Laporan Objek Pajak #
class laporan_objek_Generator(JasperGenerator):
    def __init__(self):
        super(laporan_objek_Generator, self).__init__()
        self.reportname = get_rpath('Laporan_objek_pajak.jrxml')
        self.xpath = '/opreklame/objek_pajak_lap'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'objek_pajak_lap')
            ET.SubElement(xml_greeting, "op_kd").text   = row.op_kd
            ET.SubElement(xml_greeting, "op_nm").text   = row.op_nm
            ET.SubElement(xml_greeting, "pem_nm").text  = row.pem_nm
            ET.SubElement(xml_greeting, "rek_nm").text  = row.rek_nm
            ET.SubElement(xml_greeting, "kel_nm").text  = row.kel_nm
            ET.SubElement(xml_greeting, "jln_nm").text  = row.jln_nm
            ET.SubElement(xml_greeting, "op_nsr").text  = unicode(row.op_nsr)
            ET.SubElement(xml_greeting, "op_mk").text   = unicode(row.op_mk)
            ET.SubElement(xml_greeting, "op_jml").text  = unicode(row.op_jml)
            ET.SubElement(xml_greeting, "op_ls").text   = unicode(row.op_ls)
            ET.SubElement(xml_greeting, "dis").text     = unicode(row.dis)
        return self.root	
        
# Laporan Transaksi Pajak #
class laporan_transaksi_Generator(JasperGenerator):
    def __init__(self):
        super(laporan_transaksi_Generator, self).__init__()
        self.reportname = get_rpath('Laporan_transaksi_pajak.jrxml')
        self.xpath = '/opreklame/transaksi_lap'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'transaksi_lap')
            ET.SubElement(xml_greeting, "tr_kd").text     = row.tr_kd
            ET.SubElement(xml_greeting, "tr_nm").text     = row.tr_nm
            ET.SubElement(xml_greeting, "tr_nopd").text   = row.tr_nopd
            ET.SubElement(xml_greeting, "tr_npwpd").text  = row.tr_npwpd
            ET.SubElement(xml_greeting, "tr_skpd").text   = row.tr_skpd
            ET.SubElement(xml_greeting, "tr_byr").text    = row.tr_byr
            ET.SubElement(xml_greeting, "tr_ipr").text    = row.tr_ipr
            ET.SubElement(xml_greeting, "tr_aw").text     = unicode(row.tr_aw)
            ET.SubElement(xml_greeting, "tr_ak").text     = unicode(row.tr_ak)
            ET.SubElement(xml_greeting, "tr_jml").text    = unicode(row.tr_jml)
            ET.SubElement(xml_greeting, "op_nm").text     = row.op_nm
            ET.SubElement(xml_greeting, "dis").text       = unicode(row.dis)
        return self.root		
        
###############################		
## Khusus untuk modul master ##
###############################						

# Master Kecamatan #
class master_kecamatan_Generator(JasperGenerator):
    def __init__(self):
        super(master_kecamatan_Generator, self).__init__()
        self.reportname = get_rpath('Master_kecamatan.jrxml')
        self.xpath = '/opreklame/kecamatan'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kecamatan')
            ET.SubElement(xml_greeting, "kec_kd").text     = row.kec_kd
            ET.SubElement(xml_greeting, "kec_nm").text     = row.kec_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Kecamatan All #
class master_kecamatan2_Generator(JasperGenerator):
    def __init__(self):
        super(master_kecamatan2_Generator, self).__init__()
        self.reportname = get_rpath('Master_kecamatan_all.jrxml')
        self.xpath = '/opreklame/kecamatan_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kecamatan_all')
            ET.SubElement(xml_greeting, "kec_kd").text     = row.kec_kd
            ET.SubElement(xml_greeting, "kec_nm").text     = row.kec_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Kelurahan #
class master_kelurahan_Generator(JasperGenerator):
    def __init__(self):
        super(master_kelurahan_Generator, self).__init__()
        self.reportname = get_rpath('Master_kelurahan.jrxml')
        self.xpath = '/opreklame/kelurahan'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kelurahan')
            ET.SubElement(xml_greeting, "kel_kd").text     = row.kel_kd
            ET.SubElement(xml_greeting, "kel_nm").text     = row.kel_nm
            ET.SubElement(xml_greeting, "kec_nm").text     = row.kec_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Kelurahan All #
class master_kelurahan2_Generator(JasperGenerator):
    def __init__(self):
        super(master_kelurahan2_Generator, self).__init__()
        self.reportname = get_rpath('Master_kelurahan_all.jrxml')
        self.xpath = '/opreklame/kelurahan_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kelurahan_all')
            ET.SubElement(xml_greeting, "kel_kd").text     = row.kel_kd
            ET.SubElement(xml_greeting, "kel_nm").text     = row.kel_nm
            ET.SubElement(xml_greeting, "kec_nm").text     = row.kec_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Kelas Jalan #
class master_kelas_jalan_Generator(JasperGenerator):
    def __init__(self):
        super(master_kelas_jalan_Generator, self).__init__()
        self.reportname = get_rpath('Master_kelas_jalan.jrxml')
        self.xpath = '/opreklame/kelas_jalan'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kelas_jalan')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Kelas Jalan All #
class master_kelas_jalan2_Generator(JasperGenerator):
    def __init__(self):
        super(master_kelas_jalan2_Generator, self).__init__()
        self.reportname = get_rpath('Master_kelas_jalan_all.jrxml')
        self.xpath = '/opreklame/kelas_jalan_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'kelas_jalan_all')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Jalan #
class master_jalan_Generator(JasperGenerator):
    def __init__(self):
        super(master_jalan_Generator, self).__init__()
        self.reportname = get_rpath('Master_jalan.jrxml')
        self.xpath = '/opreklame/jalan'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jalan')
            ET.SubElement(xml_greeting, "jln_kd").text     = row.jln_kd
            ET.SubElement(xml_greeting, "jln_nm").text     = row.jln_nm
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Jalan All #
class master_jalan2_Generator(JasperGenerator):
    def __init__(self):
        super(master_jalan2_Generator, self).__init__()
        self.reportname = get_rpath('Master_jalan_all.jrxml')
        self.xpath = '/opreklame/jalan_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'jalan_all')
            ET.SubElement(xml_greeting, "jln_kd").text     = row.jln_kd
            ET.SubElement(xml_greeting, "jln_nm").text     = row.jln_nm
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Pemilik #
class master_pemilik_Generator(JasperGenerator):
    def __init__(self):
        super(master_pemilik_Generator, self).__init__()
        self.reportname = get_rpath('Master_pemilik.jrxml')
        self.xpath = '/opreklame/pemilik'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'pemilik')
            ET.SubElement(xml_greeting, "p_kd").text     = row.p_kd
            ET.SubElement(xml_greeting, "p_nm").text     = row.p_nm
            ET.SubElement(xml_greeting, "p_almt").text   = row.p_almt
            ET.SubElement(xml_greeting, "p_nt").text     = row.p_nt
            ET.SubElement(xml_greeting, "p_nf").text     = row.p_nf
            ET.SubElement(xml_greeting, "dis").text      = unicode(row.dis)
        return self.root		
		
# Master Pemilik All #
class master_pemilik2_Generator(JasperGenerator):
    def __init__(self):
        super(master_pemilik2_Generator, self).__init__()
        self.reportname = get_rpath('Master_pemilik_all.jrxml')
        self.xpath = '/opreklame/pemilik_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'pemilik_all')
            ET.SubElement(xml_greeting, "p_kd").text     = row.p_kd
            ET.SubElement(xml_greeting, "p_nm").text     = row.p_nm
            ET.SubElement(xml_greeting, "p_almt").text   = row.p_almt
            ET.SubElement(xml_greeting, "p_nt").text     = row.p_nt
            ET.SubElement(xml_greeting, "p_nf").text     = row.p_nf
            ET.SubElement(xml_greeting, "dis").text      = unicode(row.dis)
        return self.root
        
# Master Ketinggian #
class master_ketinggian_Generator(JasperGenerator):
    def __init__(self):
        super(master_ketinggian_Generator, self).__init__()
        self.reportname = get_rpath('Master_ketinggian.jrxml')
        self.xpath = '/opreklame/ketinggian'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'ketinggian')
            ET.SubElement(xml_greeting, "ket_kd").text     = row.ket_kd
            ET.SubElement(xml_greeting, "ket_nm").text     = row.ket_nm
            ET.SubElement(xml_greeting, "ket_ni").text     = unicode(row.ket_ni)
            ET.SubElement(xml_greeting, "ket_min").text    = unicode(row.ket_min)
            ET.SubElement(xml_greeting, "ket_max").text    = unicode(row.ket_max)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Ketinggian All #
class master_ketinggian2_Generator(JasperGenerator):
    def __init__(self):
        super(master_ketinggian2_Generator, self).__init__()
        self.reportname = get_rpath('Master_ketinggian_all.jrxml')
        self.xpath = '/opreklame/ketinggian_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'ketinggian_all')
            ET.SubElement(xml_greeting, "ket_kd").text     = row.ket_kd
            ET.SubElement(xml_greeting, "ket_nm").text     = row.ket_nm
            ET.SubElement(xml_greeting, "ket_ni").text     = unicode(row.ket_ni)
            ET.SubElement(xml_greeting, "ket_min").text    = unicode(row.ket_min)
            ET.SubElement(xml_greeting, "ket_max").text    = unicode(row.ket_max)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Nilai Sewa Reklame #
class master_nsr_Generator(JasperGenerator):
    def __init__(self):
        super(master_nsr_Generator, self).__init__()
        self.reportname = get_rpath('Master_nsr.jrxml')
        self.xpath = '/opreklame/nsr'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'nsr')
            ET.SubElement(xml_greeting, "nsr_kd").text     = row.nsr_kd
            ET.SubElement(xml_greeting, "nsr_nm").text     = row.nsr_nm
            ET.SubElement(xml_greeting, "nsr_ni").text     = unicode(row.nsr_ni)
            ET.SubElement(xml_greeting, "rek_nm").text     = row.rek_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Nilai Sewa Reklame All #
class master_nsr2_Generator(JasperGenerator):
    def __init__(self):
        super(master_nsr2_Generator, self).__init__()
        self.reportname = get_rpath('Master_nsr_all.jrxml')
        self.xpath = '/opreklame/nsr_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'nsr_all')
            ET.SubElement(xml_greeting, "nsr_kd").text     = row.nsr_kd
            ET.SubElement(xml_greeting, "nsr_nm").text     = row.nsr_nm
            ET.SubElement(xml_greeting, "nsr_ni").text     = unicode(row.nsr_ni)
            ET.SubElement(xml_greeting, "rek_nm").text     = row.rek_nm
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Nilai Satuan Strategis #
class master_strategis_Generator(JasperGenerator):
    def __init__(self):
        super(master_strategis_Generator, self).__init__()
        self.reportname = get_rpath('Master_strategis.jrxml')
        self.xpath = '/opreklame/strategis'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'strategis')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "kls_min").text    = unicode(row.kls_min)
            ET.SubElement(xml_greeting, "kls_max").text    = unicode(row.kls_max)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Nilai Satuan Strategis All #
class master_strategis2_Generator(JasperGenerator):
    def __init__(self):
        super(master_strategis2_Generator, self).__init__()
        self.reportname = get_rpath('Master_strategis_all.jrxml')
        self.xpath = '/opreklame/strategis_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'strategis_all')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "kls_min").text    = unicode(row.kls_min)
            ET.SubElement(xml_greeting, "kls_max").text    = unicode(row.kls_max)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Nilai Jual Objek Pajak #
class master_njop_Generator(JasperGenerator):
    def __init__(self):
        super(master_njop_Generator, self).__init__()
        self.reportname = get_rpath('Master_njop.jrxml')
        self.xpath = '/opreklame/njop'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'njop')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "kls_min").text    = unicode(row.kls_min)
            ET.SubElement(xml_greeting, "kls_max").text    = unicode(row.kls_max)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Nilai Jual Objek Pajak All #
class master_njop2_Generator(JasperGenerator):
    def __init__(self):
        super(master_njop2_Generator, self).__init__()
        self.reportname = get_rpath('Master_njop_all.jrxml')
        self.xpath = '/opreklame/njop_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'njop_all')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "kls_min").text    = unicode(row.kls_min)
            ET.SubElement(xml_greeting, "kls_max").text    = unicode(row.kls_max)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Lokasi Pasang #
class master_lokasi_Generator(JasperGenerator):
    def __init__(self):
        super(master_lokasi_Generator, self).__init__()
        self.reportname = get_rpath('Master_lokasi.jrxml')
        self.xpath = '/opreklame/lokasi'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'lokasi')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Lokasi Pasang All #
class master_lokasi2_Generator(JasperGenerator):
    def __init__(self):
        super(master_lokasi2_Generator, self).__init__()
        self.reportname = get_rpath('Master_lokasi_all.jrxml')
        self.xpath = '/opreklame/lokasi_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'lokasi_all')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Sudut Pandang #
class master_sudut_Generator(JasperGenerator):
    def __init__(self):
        super(master_sudut_Generator, self).__init__()
        self.reportname = get_rpath('Master_sudut.jrxml')
        self.xpath = '/opreklame/sudut'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'sudut')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Sudut Pandang All #
class master_sudut2_Generator(JasperGenerator):
    def __init__(self):
        super(master_sudut2_Generator, self).__init__()
        self.reportname = get_rpath('Master_sudut_all.jrxml')
        self.xpath = '/opreklame/sudut_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'sudut_all')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root
        
# Master Bahan #
class master_bahan_Generator(JasperGenerator):
    def __init__(self):
        super(master_bahan_Generator, self).__init__()
        self.reportname = get_rpath('Master_bahan.jrxml')
        self.xpath = '/opreklame/bahan'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'bahan')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root		
		
# Master Bahan All #
class master_bahan2_Generator(JasperGenerator):
    def __init__(self):
        super(master_bahan2_Generator, self).__init__()
        self.reportname = get_rpath('Master_bahan_all.jrxml')
        self.xpath = '/opreklame/bahan_all'
        self.root = ET.Element('opreklame') 

    def generate_xml(self, tobegreeted):
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'bahan_all')
            ET.SubElement(xml_greeting, "kls_kd").text     = row.kls_kd
            ET.SubElement(xml_greeting, "kls_nm").text     = row.kls_nm
            ET.SubElement(xml_greeting, "kls_ni").text     = unicode(row.kls_ni)
            ET.SubElement(xml_greeting, "dis").text        = unicode(row.dis)
        return self.root