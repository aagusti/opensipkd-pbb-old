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
    Kecamatan, Kelurahan, KelasJalan, Jalan, Pemilik, Rekening, Reklame, Transaksi
    )
from datatables import ColumnDT, DataTables
from datetime import datetime
from ...tools import create_now

SESS_ADD_FAILED = 'Jalan add failed'
SESS_EDIT_FAILED = 'Jalan edit failed'

########                    
# List #
########    
@view_config(route_name='reklame-jalan', renderer='templates/jalan/list.pt',
             permission='reklame-jalan')
def view_list(request):
    return dict(project='Pajak Reklame')
    
##########                    
# Action #
##########    
@view_config(route_name='reklame-jalan-act', renderer='json',
             permission='reklame-jalan-act')
def jalan_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('kelas_jalans.nama'))
        columns.append(ColumnDT('disabled'))
        
        query = DBSession.query(Jalan)
        rowTable = DataTables(req, Jalan, query, columns)
        return rowTable.output_result()
    
        
    elif url_dict['act']=='hon':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Jalan.id, 
                               Jalan.kode, 
                               Jalan.nama
                       ).filter(Jalan.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            d['nama']    = k[2]
            r.append(d)
        return r   
           
    elif url_dict['act']=='hok':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Jalan.id, 
                               Jalan.kode, 
                               Jalan.nama
                       ).filter(Jalan.kode.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[1]
            d['kode']    = k[1]
            d['nama']    = k[2]
            r.append(d)
        return r    
        
    elif url_dict['act']=='hon_jal_op':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Jalan.id, 
                               Jalan.kode, 
                               Jalan.nama,
                               KelasJalan.nama
                       ).filter(Jalan.kelas_jalan_id == KelasJalan.id, 
                                Jalan.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['jal']     = k[3]
            r.append(d)
        return r      
    
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
        q = DBSession.query(Jalan).filter_by(id=uid)
        jalan = q.first()
    else:
        jalan = None
        
    q = DBSession.query(Jalan).filter_by(kode=value['kode'])
    found = q.first()
    if jalan:
        if found and found.id != jalan.id:
            err_kode()
    elif found:
        err_kode()
        
    if 'nama' in value: # optional
        found = Jalan.get_by_nama(value['nama'])
        if jalan:
            if found and found.id != jalan.id:
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

class AddSchema(colander.Schema):
    kode            = colander.SchemaNode(
                      colander.String(),
                      oid = "kode",
                      title = "Kode",)
    nama            = colander.SchemaNode(
                      colander.String(),
                      oid = "nama",
                      title = "Nama",)
    kelas_jalan_id  = colander.SchemaNode(
                      colander.Integer(),
                      oid="kelas_jalan_id",
                      missing=colander.drop)
    kelas_jalan_nm  = colander.SchemaNode(
                      colander.String(),
                      #missing=colander.drop,
                      oid="kelas_jalan_nm",
                      title="Kelas",)
    disabled        = colander.SchemaNode(
                      colander.Integer(),
                      widget=deferred_status)

class EditSchema(AddSchema):
    id = colander.SchemaNode(
                   colander.Integer(),
                   oid="id")
                    

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(daftar_status=STATUS)
    schema.request = request
    return Form(schema, buttons=('save','cancel'))

def save_request1(row1=None):
    row1 = KelasJalan()
    return row1
    
def save(values, user, row=None):
    if not row:
        row = Jalan()
        row.create_uid = user.id
        row.created    = datetime.now()
    else:
        row.update_uid = user.id
        row.updated    = datetime.now()
    
    row.from_dict(values)
    DBSession.add(row)
    DBSession.flush()
    
    #Untuk update disabled pada Kelas Jalan
    a = row.kelas_jalan_id
    row1 = DBSession.query(KelasJalan).filter(KelasJalan.id==a).first()   
    row1.disabled=1
    save_request1(row1)
    
    return row
    
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, request.user, row)
    request.session.flash('Jalan %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('reklame-jalan'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='reklame-jalan-add', renderer='templates/jalan/add.pt',
             permission='reklame-jalan-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)				
                return HTTPFound(location=request.route_url('reklame-jalan-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(Jalan).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'Jalan ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='reklame-jalan-edit', renderer='templates/jalan/edit.pt',
             permission='reklame-jalan-edit')
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
    values['kelas_jalan_id'] = row and row.kelas_jalan_id    or 0
    values['kelas_jalan_nm'] = row and row.kelas_jalans.nama or ''
    form.set_appstruct(values)
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='reklame-jalan-delete', renderer='templates/jalan/delete.pt',
             permission='reklame-jalan-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    uid = row.id
    
    if not row:
        return id_not_found(request)
        
    a = DBSession.query(Reklame).filter(Reklame.jalan_id==uid).first()
    if a:
        request.session.flash('Data tidak bisa dihapus, karena sudah masuk di Objek Pajak.', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            msg = 'Jalan ID %d %s sudah dihapus.' % (row.id, row.nama)
            q.delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())
