from email.utils import parseaddr
from sqlalchemy import not_
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

SESS_ADD_FAILED = 'Pemilik add failed'
SESS_EDIT_FAILED = 'Pemilik edit failed'

########                    
# List #
########    
@view_config(route_name='reklame-pemilik', renderer='templates/pemilik/list.pt',
             permission='reklame-pemilik')
def view_list(request):
    return dict(project='Pajak Reklame')
    
##########                    
# Action #
##########    
@view_config(route_name='reklame-pemilik-act', renderer='json',
             permission='reklame-pemilik-act')
def pemilik_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('alamat'))
        columns.append(ColumnDT('telephone'))
        columns.append(ColumnDT('mobile'))
        columns.append(ColumnDT('disabled'))
        
        query = DBSession.query(Pemilik)
        rowTable = DataTables(req, Pemilik, query, columns)
        return rowTable.output_result()
        
    elif url_dict['act']=='hon_pemilik':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Pemilik.id, 
                               Pemilik.kode, 
                               Pemilik.nama,
                               Pemilik.alamat, 
                               Pemilik.telephone,
                               Pemilik.mobile,
                       ).filter(Pemilik.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['alamat']  = k[3]
            d['telp']    = k[4]
            d['mobile']  = k[5]
            r.append(d)
        return r   
           
    elif url_dict['act']=='hok_pemilik':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Pemilik.id, 
                               Pemilik.kode, 
                               Pemilik.nama,
                               Pemilik.alamat, 
                               Pemilik.telephone,
                               Pemilik.mobile,
                       ).filter(Pemilik.kode.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[1]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['alamat']  = k[3]
            d['telp']    = k[4]
            d['mobile']  = k[5]
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
        q = DBSession.query(Pemilik).filter_by(id=uid)
        pemilik = q.first()
    else:
        pemilik = None
        
    q = DBSession.query(Pemilik).filter_by(kode=value['kode'])
    found = q.first()
    if pemilik:
        if found and found.id != pemilik.id:
            err_kode()
    elif found:
        err_kode()
        
    if 'nama' in value: # optional
        found = Pemilik.get_by_nama(value['nama'])
        if pemilik:
            if found and found.id != pemilik.id:
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
    kode          = colander.SchemaNode(
                    colander.String(),
                    oid = "kode",
                    title = "NIK / NPWP",)
    nama          = colander.SchemaNode(
                    colander.String(),
                    oid = "nama",
                    title = "Nama",)
    alamat        = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid = "alamat",
                    title = "Alamat")
    telephone     = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid = "telephone",
                    title = "No.Telp")
    mobile        = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid = "mobile",
                    title = "No.Mobile")
    disabled      = colander.SchemaNode(
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
    
def save(values, user, row=None):
    if not row:
        row = Pemilik()
        row.create_uid = user.id
        row.created    = datetime.now()
    else:
        row.update_uid = user.id
        row.updated    = datetime.now()
    
    row.from_dict(values)
    DBSession.add(row)
    DBSession.flush()
    return row
    
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, request.user, row)
    request.session.flash('Pemilik %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('reklame-pemilik'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='reklame-pemilik-add', renderer='templates/pemilik/add.pt',
             permission='reklame-pemilik-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)				
                return HTTPFound(location=request.route_url('reklame-pemilik-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(Pemilik).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'Pemilik ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='reklame-pemilik-edit', renderer='templates/pemilik/edit.pt',
             permission='reklame-pemilik-edit')
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
    form.set_appstruct(values)
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='reklame-pemilik-delete', renderer='templates/pemilik/delete.pt',
             permission='reklame-pemilik-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    uid = row.id
    
    if not row:
        return id_not_found(request)
        
    a = DBSession.query(Reklame).filter(Reklame.pemilik_id==uid).first()
    if a:
        request.session.flash('Data tidak bisa dihapus, karena sudah masuk di Objek Pajak.', 'error')
        return route_list(request)
        
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            msg = 'Pemilik ID %d %s sudah dihapus.' % (row.id, row.nama)
            q.delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())
