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
    Kecamatan, Kelurahan, Njop, KelasJalan, Jalan, Pemilik, Nssr, Rekening, Reklame, Transaksi
    )
from datatables import ColumnDT, DataTables
from datetime import datetime
from ...tools import create_now,_DTnumberformat

SESS_ADD_FAILED = 'Nilai Jual Objek Pajak Reklame add failed'
SESS_EDIT_FAILED = 'Nilai Jual Objek Pajak Reklame edit failed'

########                    
# List #
########    
@view_config(route_name='reklame-njop', renderer='templates/njop/list.pt',
             permission='reklame-njop')
def view_list(request):
    return dict(project='Pajak Reklame')
    
##########                    
# Action #
##########    
@view_config(route_name='reklame-njop-act', renderer='json',
             permission='reklame-njop-act')
def view_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('luas_min', filter=_DTnumberformat))
        columns.append(ColumnDT('luas_max', filter=_DTnumberformat))
        columns.append(ColumnDT('nilai',    filter=_DTnumberformat))
        columns.append(ColumnDT('status'))
        
        query = DBSession.query(Njop)
        rowTable = DataTables(req, Njop, query, columns)
        return rowTable.output_result()
        
    elif url_dict['act']=='hon':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Njop.id, 
                               Njop.kode, 
                               Njop.nama, 
                               Njop.nilai,
                       ).filter(Njop.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['nilai']   = k[3]
            r.append(d)
        return r   
           
    elif url_dict['act']=='hok':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Njop.id, 
                               Njop.kode, 
                               Njop.nama,
                               Njop.nilai,
                       ).filter(Njop.kode.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[1]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['nilai']   = k[3]
            r.append(d)
        return r    
    elif url_dict['act']=='search':
         items = dict(request.POST.items())
         panjang = 'panjang' in items and float(items['panjang']) or 1.0
         lebar   = 'lebar' in items and float(items['lebar']) or 1.0
         row = Njop.search_by_luas(items['jenis_id'],panjang*lebar)
         if row:
            return {"value" : row.nilai}
         else:
            return  
            
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
        q = DBSession.query(Njop).filter_by(id=uid)
        strategis = q.first()
    else:
        strategis = None
        
    q = DBSession.query(Njop).filter_by(kode=value['kode'])
    found = q.first()
    if strategis:
        if found and found.id != strategis.id:
            err_kode()
    elif found:
        err_kode()
        
    if 'nama' in value: # optional
        found = Njop.get_by_nama(value['nama'])
        if strategis:
            if found and found.id != strategis.id:
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
                    title = "Kode",)
    nama          = colander.SchemaNode(
                    colander.String(),
                    oid = "nama",
                    title = "Uraian",)
    nilai         = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    #missing=colander.drop,
                    oid = "nilai",
                    title = "Nilai")
    luas_min      = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    #missing=colander.drop,
                    oid = "luas_min",
                    title = "Luas Min")
    luas_max      = colander.SchemaNode(
                    colander.Integer(),
                    default = 0,
                    #missing=colander.drop,
                    oid = "luas_max",
                    title = "Luas Max")
    jenis_reklame_id  = colander.SchemaNode(
                    colander.String(),
                    default = 0,
                    #missing=colander.drop,
                    oid = "jenis_reklame_id",
                    title = "Jenis Reklame")
                     
    jenis_reklame_nm  = colander.SchemaNode(
                    colander.String(),
                    #missing=colander.drop,
                    oid = "jenis_reklame_nm",
                    title = "Jenis Reklame")
    status      = colander.SchemaNode(
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
        row = Njop()
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
    request.session.flash('Nilai Jual Objek Pajak Reklame %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('reklame-njop'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='reklame-njop-add', renderer='templates/njop/add.pt',
             permission='reklame-njop-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)				
                return HTTPFound(location=request.route_url('reklame-njop-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(Njop).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'Nilai Jual Objek Pajak Reklame ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='reklame-njop-edit', renderer='templates/njop/edit.pt',
             permission='reklame-njop-edit')
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
    values['jenis_reklame_nm'] = row.jenis_reklame.nama
    form.set_appstruct(values)
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='reklame-njop-delete', renderer='templates/njop/delete.pt',
             permission='reklame-njop-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    uid = row.id
    
    if not row:
        return id_not_found(request)
        
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            msg = 'Nilai Jual Objek Pajak Reklame ID %d %s sudah dihapus.' % (row.id, row.nama)
            q.delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row,form=form.render())
