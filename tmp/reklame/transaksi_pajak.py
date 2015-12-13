from email.utils import parseaddr
from sqlalchemy import not_, or_
from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from ...models import(
    DBSession,
    )
from ...models.reklame import (
    Kecamatan, Kelurahan, KelasJalan, Jalan, Jenis, Sudut, Lokasi, Pemilik, Rekening, Reklame, Transaksi
    )
from datatables import ColumnDT, DataTables
from datetime import datetime
from ...tools import create_now,_DTnumberformat,_DTstrftime

SESS_ADD_FAILED = 'Transaksi Pajak add failed'
SESS_EDIT_FAILED = 'Transaksi Pajak edit failed'

########                    
# List #
########    
@view_config(route_name='reklame-transaksi', renderer='templates/transaksi/list.pt',
             permission='reklame-transaksi')
def view_list(request):
    return dict(project='Pajak Reklame')
    
##########                    
# Action #
##########    
@view_config(route_name='reklame-transaksi-act', renderer='json',
             permission='reklame-transaksi-act')
def transaksi_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('no_skpd'))
        # columns.append(ColumnDT('kode_reklame'))
        # columns.append(ColumnDT('reklames.nama'))
        columns.append(ColumnDT('periode_awal',  filter=_DTstrftime))
        columns.append(ColumnDT('periode_akhir', filter=_DTstrftime))
        columns.append(ColumnDT('jml_terhutang',     filter=_DTnumberformat))
        columns.append(ColumnDT('status'))
        
        query = DBSession.query(Transaksi)
        rowTable = DataTables(req, Transaksi, query, columns)
        return rowTable.output_result()
             
    
#######    
# Add #
#######
def form_validator(form, value):
    def err_kode():
        raise colander.Invalid(form,
            'Kode %s sudah digunakan oleh ID %d' % (
                value['kode'], found.id))
    def err_nama():
        raise colander.Invalid(form,
            'Nama %s sudah digunakan oleh ID %d' % (
                value['nama'], found.id))
                
    if 'id' in form.request.matchdict:
        uid = form.request.matchdict['id']
        q = DBSession.query(Transaksi).filter_by(id=uid)
        transaksi = q.first()
    else:
        transaksi = None
        
        
    if 'nama' in value: # optional
        found = Transaksi.get_by_nama(value['nama'])
        if transaksi:
            if found and found.id != transaksi.id:
                err_nama()
        elif found:
            err_nama()

@colander.deferred
def deferred_status(node, kw):
    values = kw.get('daftar_status', [])
    return widget.SelectWidget(values=values)
    
STATUS = (
    (0, 'Inactive'),
    (1, 'Active'),
    )    

@colander.deferred    
def deferred_sudut(node, kw):
    values = kw.get('is_sudut', [])
    return widget.SelectWidget(values=values)
    
IS_SUDUT = (
    ('1 Arah', '1 Arah'),
    ('2 Arah', '2 Arah'),
    ('3 Arah', '3 Arah'),
    ('4 Arah', '4 Arah'),
    ('>4 Arah', '>4 Arah'),
    ('Berjalan/Kendaraan', 'Berjalan/Kendaraan'),
    ('Indoor', 'Indoor'),
    )

# Untuk pilihan Bersinar
@colander.deferred
def deferred_bersinar(node, kw):
    values = kw.get('daftar_bersinar', [])
    return widget.SelectWidget(values=values)
    
IS_BERSINAR = (
    (0, 'Tidak'),
    (1, 'Ya'),
    )     
    
# Untuk pilihan Menempel
@colander.deferred
def deferred_menempel(node, kw):
    values = kw.get('daftar_menempel', [])
    return widget.SelectWidget(values=values)
    
IS_MENEMPEL = (
    (0, 'Tidak'),
    (1, 'Ya'),
    )
    
# Untuk pilihan Dalam Ruang
@colander.deferred
def deferred_druang(node, kw):
    values = kw.get('daftar_druang', [])
    return widget.SelectWidget(values=values)
    
IS_DRUANG = (
    (0, 'Tidak'),
    (1, 'Ya'),
    )     
    
# Untuk pilihan Lahan
@colander.deferred
def deferred_lahan(node, kw):
    values = kw.get('daftar_lahan', [])
    return widget.SelectWidget(values=values)
    
IS_LAHAN = (
    (1, 'Pemda'),
    (2, 'Swasta'),
    )     


class AddSchema(colander.Schema):
    widgetMoney = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                                 
    kode          = colander.SchemaNode(
                    colander.String(),
                    oid = "kode",
                    title = "Kode",
                    missing=colander.drop)
    nama          = colander.SchemaNode(
                    colander.String(),
                    oid = "nama",
                    title = "Naskah",)
    no_permohonan = colander.SchemaNode(
                    colander.String(),
                    oid="no_permohonan",
                    title="Permohonan")
    id_permohonan = colander.SchemaNode(
                    colander.Integer(),
                    #missing=colander.drop,
                    oid="id_permohonan",
                    title="ID")
    tgl_permohonan = colander.SchemaNode(
                    colander.Date(),
                    #missing=colander.drop,
                    oid="tgl_permohonan",
                    title="Tanggal")
    nama_pemohon  = colander.SchemaNode(
                    colander.String(),
                    oid="nama_pemohon",
                    title="Pemohon",)
    alamat_pemohon = colander.SchemaNode(
                    colander.String(),
                    oid="alamat_pemohon",
                    title="Alamat",)
    no_sk_ipr     = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid="no_sk_ipr",
                    title="No.SK IPR")
    tgl_sk_ipr    = colander.SchemaNode(
                    colander.Date(),
                    #missing=colander.drop,
                    oid="tgl_sk_ipr",
                    title="Tanggal")
    periode_awal  = colander.SchemaNode(
                    colander.Date(),
                    oid="periode_awal",
                    title="Periode")
    periode_akhir = colander.SchemaNode(
                    colander.Date(),
                    oid="periode_akhir",
                    title="Tgl akhir")
    npwpd         = colander.SchemaNode(
                    colander.String(),
                    oid="npwpd",
                    title="NPWPD",)
    nama_wp       = colander.SchemaNode(
                    colander.String(),
                    oid="nama_wp",
                    title="Nama WP",)
    no_skpd       = colander.SchemaNode(
                    colander.String(),
                    oid="no_skpd",
                    title="No.SKPD")
    tgl_skpd      = colander.SchemaNode(
                    colander.Date(),
                    oid="tgl_skpd",
                    title="Tanggal")
    jenis_reklame_id      = colander.SchemaNode(
                    colander.Integer(),
                    oid="jenis_reklame_id",
                    missing=colander.drop)
    jenis_reklame_nm      = colander.SchemaNode(
                    colander.String(),
                    oid="jenis_reklame_nm",
                    title="Jenis",)
    jenis_reklame_ni      = colander.SchemaNode(
                    colander.Decimal(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="jenis_reklame_ni",
                    title="NJOP",
                    default=1)
    masa_pajak_id      = colander.SchemaNode(
                    colander.Integer(),
                    oid="masa_pajak_id",
                    missing=colander.drop)
    masa_pajak_nm  = colander.SchemaNode(
                    colander.String(),
                    oid="masa_pajak_nm",
                    title="Masa Pajak",)
    pembagi        = colander.SchemaNode(
                    colander.Decimal(),
                    oid="pembagi",
                    title="Pembagi",
                    default=1.0)
    accres        = colander.SchemaNode(
                    colander.Integer(),
                    oid="accres",
                    title="Accres",
                    default=0)
                                    
    panjang       = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="panjang",
                    title="Panjang",
                    default=1.00)
    lebar         = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="lebar",
                    title="Lebar",
                    default=1.00)
    luas          = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="luas",
                    title="Luas",
                    default=1.00)

    muka          = colander.SchemaNode(
                    colander.Integer(),
                    oid="muka",
                    title="Muka",
                    default=1)
    jumlah_titik  = colander.SchemaNode(
                    colander.Integer(),
                    oid="jumlah_titik",
                    title="Jml Titik",
                    default=1)
                    
    jml_luas  = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="jml_luas",
                    title="Jml Luas",
                    default=1)
                    
    nsr          = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="nsr",
                    title="Jml. NSR")
                    
    ketinggian_id   = colander.SchemaNode(
                    colander.String(),
                    oid="ketinggian_id",
                    missing=colander.drop)
    ketinggian_nm   = colander.SchemaNode(
                    colander.String(),
                    oid="ketinggian_nm",
                    title="Ketinggian",)
    ketinggian_ni   = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="ketinggian_ni",
                    title="Nilai",
                    default=0)
    tinggi        = colander.SchemaNode(
                    colander.Integer(),
                    oid="tinggi",
                    title="Tinggi",
                    default=1)
    jml_ketinggian = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="jml_ketinggian",
                    title="Jml Ket.",
                    default=0)                    
    jenis_nssr_id = colander.SchemaNode(
                    colander.Integer(),
                    oid="nssr_id",)
    jenis_nssr_kd = colander.SchemaNode(
                    colander.String(),
                    oid="nssr_kd",
                    title="NSSR",)                    
    jenis_nssr_nm = colander.SchemaNode(
                    colander.String(),
                    oid="nssr_nm",
                    title="NSSR",)                    
    nssr_ni = colander.SchemaNode(
                    colander.Float(),
                    oid="nssr_ni",
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    title="Nilai NSSR",
                    default = 0,)                    
    nssr = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="nssr",
                    title="Jml. NSSR",
                    default = 0,)  
    kelas_jalan_id = colander.SchemaNode(
                    colander.String(),
                    oid="kelas_jalan_id",)
    kelas_jalan_kd = colander.SchemaNode(
                    colander.String(),
                    oid="kelas_jalan_kd",
                    title="Kelas Jalan",)    
    kelas_jalan_nm = colander.SchemaNode(
                    colander.String(),
                    oid="kelas_jalan_nm",
                    title="Kls. Jalan",)                    
    kelas_jalan_ni = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="kelas_jalan_ni",
                    title="Nilai Klas",
                    default = 0,)                    
    sudut_pandang_id      = colander.SchemaNode(
                    colander.Integer(),
                    oid="sudut_pandang_id",
                    missing=colander.drop)
    sudut_pandang_kd      = colander.SchemaNode(
                    colander.String(),
                    missing=colander.drop,
                    oid="sudut_pandang_kd",
                    title="Sdt Pdg",)
    sudut_pandang_nm      = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid="sudut_pandang_nm",
                    title="Sdt Pandang",)
    sudut_pandang_ni = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="sudut_pandang_ni",
                    title="Nilai SP",
                    default = 0,)
    lokasi_pasang_id     = colander.SchemaNode(
                    colander.Integer(),
                    oid="lokasi_pasang_id",
                    missing=colander.drop)
    lokasi_pasang_kd     = colander.SchemaNode(
                    colander.String(),
                    missing=colander.drop,
                    oid="lokasi_pasang_kd",
                    title="Lokasi",)
    lokasi_pasang_nm     = colander.SchemaNode(
                    colander.String(),
                    oid="lokasi_pasang_nm",
                    title="Lokasi",)
    lokasi_pasang_ni = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="lokasi_pasang_ni",
                    title="Nilai Lok",
                    default = 0,)                    
                
    faktor_lain_id   = colander.SchemaNode(
                    colander.Integer(),
                    missing=colander.drop,
                    oid="faktor_lain_id",
                    default=1)
    faktor_lain_kd   = colander.SchemaNode(
                    colander.String(),
                    missing=colander.drop,
                    oid="faktor_lain_kd",
                    title="Faktor Lain")
    faktor_lain_nm   = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid="faktor_lain_nm",
                    title="Faktor Lain")
    faktor_lain_ni   = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1, 'allowNegative':True}),
                oid="faktor_lain_ni",
                title="Persen",
                default=0)
    dasar         = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="dasar",
                    title="Dasar",
                    default=0)
    tarif         = colander.SchemaNode(
                    colander.Integer(),
                    oid="tarif",
                    title="Tarif",
                    default=0)
    pokok     = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="pokok",
                    title="Pokok",
                    default=0)
    denda         = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="denda",
                    title="Denda",
                    default=0)
    bunga         = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="bunga",
                    title="Bunga",
                    default=0)
    kompensasi    = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="kompensasi",
                    title="Kompensasi",
                    default=0)
    kenaikan    = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    oid="kenaikan",
                    title="Kenaikan",
                    default=0)
    jml_terhutang = colander.SchemaNode(
                    colander.Float(),
                    widget = widget.MoneyInputWidget(
                                 options={'allowZero':True, 'precision':1}),
                    missing=colander.drop,
                    oid="jml_terhutang",
                    title="Terhutang")
                    
    status        = colander.SchemaNode(
                    colander.Integer(),
                    widget=deferred_status)
    
    no_bayar      = colander.SchemaNode(
                    colander.String(),
                    oid="no_bayar",
                    missing=colander.drop,
                    title="No.Bayar")
    tgl_bayar     = colander.SchemaNode(
                    colander.Date(),
                    missing=colander.drop,
                    oid="tgl_bayar",
                    title="Tanggal")

                    # reklame_id    = colander.SchemaNode(
                    # colander.Integer(),
                    # oid="reklame_id",
                    # missing=colander.drop)
    # kode_reklame  = colander.SchemaNode(
                    # colander.String(),
                    # missing=colander.drop,
                    # oid="kode_reklame",
                    # title="NOPR",)
    # reklame_nm    = colander.SchemaNode(
                    # colander.String(),
                    # missing=colander.drop,
                    # oid="reklame_nm",
                    # title="Objek.Pajak",)
    
    # pemilik_id    = colander.SchemaNode(
                    # colander.Integer(),
                    # oid="pemilik_id",
                    # missing=colander.drop)

    rekening_id   = colander.SchemaNode(
                    colander.Integer(),
                    oid="rekening_id",
                    missing=colander.drop)
    rekening_nm   = colander.SchemaNode(
                    colander.String(),
                    oid="rekening_nm",
                    title="Rekening",
                    missing=colander.drop,
                    )

    # lahan_id      = colander.SchemaNode(
                    # colander.Integer(),
                    # oid="lahan",
                    # title="Lahan",
                    # widget=deferred_lahan)
    # bersinar      = colander.SchemaNode(
                    # colander.Integer(),
                    # oid="bersinar",
                    # title="Bersinar",
                    # widget=deferred_bersinar)
    # menempel      = colander.SchemaNode(
                    # colander.Integer(),
                    # oid="menempel",
                    # title="Menempel",
                    # widget=deferred_menempel)
    # dalam_ruang   = colander.SchemaNode(
                    # colander.Integer(),
                    # oid="dalam_ruang",
                    # title="Dlm Ruang",
                    # widget=deferred_druang)
    #nopd          = colander.SchemaNode(
    #                colander.String(),
    #                #missing=colander.drop,
    #                oid="nopd",
    #                title="NOPD",)
class EditSchema(AddSchema):
    id = colander.SchemaNode(
                   colander.Integer(),
                   oid="id")
                    
def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(daftar_status=STATUS,
                         #daftar_lahan=IS_LAHAN,
                         #daftar_bersinar=IS_BERSINAR,
                         #daftar_menempel=IS_MENEMPEL,
                         #daftar_druang=IS_DRUANG,
                         )
    schema.request = request
    return Form(schema, buttons=('save','cancel'))

def save_request2(row1=None):
    row1 = Reklame()
    return row1
    
def save(values, user, row=None):
    if not row:
        row = Transaksi()
        row.create_uid = user.id
        row.created    = datetime.now()
    else:
        row.update_uid = user.id
        row.updated    = datetime.now()
    
    row.from_dict(values) 
    
    if not row.kode:
        a  = int(row.id_permohonan)
        b  = row.no_permohonan
        no = "00%d" % a
        id = no[-3:] 
        #no_permohonan + id_permohonan (007001001-001)
        row.kode = "%s" % b + "-%s" % id        
    
    DBSession.add(row)
    DBSession.flush()
    
    return row
    
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, request.user, row)
    request.session.flash('Transaksi Pajak %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('reklame-transaksi'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='reklame-transaksi-add', renderer='templates/transaksi/add.pt',
             permission='reklame-transaksi-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                request.session.flash(e.message, 'error')
                return dict(form=form)				
                return HTTPFound(location=request.route_url('reklame-transaksi-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(Transaksi).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'Transaksi Pajak ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='reklame-transaksi-edit', renderer='templates/transaksi/edit.pt',
             permission='reklame-transaksi-edit')
def view_edit(request):
    row = query_id(request).first()
    if not row:
        return id_not_found(request)
    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            save_request(dict(controls), request, row)
        return route_list(request)
    elif SESS_EDIT_FAILED in request.session:
        return session_failed(request, SESS_EDIT_FAILED)
    values = row.to_dict()
    print '------------------>', values['ketinggian_ni']
    values['jenis_reklame_nm'] = row.jenis_reklames and row.jenis_reklames.nama or ''
    #values['jenis_reklame_ni'] = row.jenis_reklames.njop.nilai or ''
    values['ketinggian_nm'] = row.ketinggians and row.ketinggians.nama or ''
    #values['ketinggian_ni'] = row and row.ketinggians.ketinggian_ni or 0.0
    values['jenis_nssr_nm'] = row.jenis_nssr and row.jenis_nssr.nama or ''
    values['jenis_nssr_kd'] = row.jenis_nssr and row.jenis_nssr.kode or ''
    values['kelas_jalan_nm'] = row.kelas_jalans and row.kelas_jalans.nama or ''
    values['kelas_jalan_kd'] = row.kelas_jalans and row.kelas_jalans.kode or ''
    values['sudut_pandang_nm'] = row.sudut_pandangs and row.sudut_pandangs.nama or ''
    values['sudut_pandang_kd'] = row.sudut_pandangs and row.sudut_pandangs.kode or ''
    values['lokasi_pasang_nm'] = row.lokasi_pasangs and row.lokasi_pasangs.nama or ''
    values['lokasi_pasang_kd'] = row.lokasi_pasangs and row.lokasi_pasangs.kode or ''
    values['faktor_lain_nm'] = row.faktor_lains and row.faktor_lains.nama or ''
    values['faktor_lain_kd'] = row.faktor_lains and row.faktor_lains.kode or ''
    values['masa_pajak_nm'] = row.masa_pajaks and row.masa_pajaks.nama or ''
    
    form.set_appstruct(values)
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='reklame-transaksi-delete', renderer='templates/transaksi/delete.pt',
             permission='reklame-transaksi-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    if not row:
        return id_not_found(request)
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            msg = 'Transaksi Pajak ID %d %s sudah dihapus.' % (row.id, row.nama)
            q.delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())
