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
    FaktorLain, Rekening
    )
from datatables import ColumnDT, DataTables
from datetime import datetime
from ...tools import create_now,_DTnumberformat

SESS_ADD_FAILED = 'faktorlain add failed'
SESS_EDIT_FAILED = 'faktorlain edit failed'

########                    
# List #
########    
@view_config(route_name='reklame-faktorlain', renderer='templates/faktorlain/list.pt',
             permission='reklame-faktorlain')
def view_list(request):
    return dict(project='TiRek')
    
##########                    
# Action #
##########    
@view_config(route_name='reklame-faktorlain-act', renderer='json',
             permission='reklame-faktorlain-act')
def faktorlain_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('tarif'))
        columns.append(ColumnDT('status'))
        
        query = DBSession.query(FaktorLain)
        rowTable = DataTables(req, FaktorLain, query, columns)
        return rowTable.output_result()
    
    elif url_dict['act']=='hon':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(FaktorLain.id, 
                               FaktorLain.kode, 
                               FaktorLain.nama,
                               FaktorLain.tarif,
                       ).filter(FaktorLain.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['tarif']    = k[3]
            r.append(d)
        return r   
           
    elif url_dict['act']=='hok':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(FaktorLain.id, 
                               FaktorLain.kode, 
                               FaktorLain.nama,
                               FaktorLain.tarif,
                       ).filter(FaktorLain.kode.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[1]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['tarif']    = k[3]
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
        q = DBSession.query(FaktorLain).filter_by(id=uid)
        nsr = q.first()
    else:
        nsr = None
        
    q = DBSession.query(FaktorLain).filter_by(kode=value['kode'])
    found = q.first()
    if nsr:
        if found and found.id != nsr.id:
            err_kode()
    elif found:
        err_kode()
        
    if 'nama' in value: # optional
        found = FaktorLain.get_by_nama(value['nama'])
        if nsr:
            if found and found.id != nsr.id:
                err_nama()
        elif found:
            err_nama()

@colander.deferred
def deferred_status(node, kw):
    values = kw.get('daftar_status', [])
    return widget.SelectWidget(values=values)
    
STATUS = (
    (1, 'Active'),
    (0, 'Inactive'),
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
    tarif            = colander.SchemaNode(
                      colander.Integer(),
                      oid = "tarif",
                      title = "Tarif",)
    status        = colander.SchemaNode(
                      colander.String(),
                      widget=deferred_status,
                      oid = "status",)

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
    row1 = Rekening()
    return row1
    
def save(values, user, row=None):
    if not row:
        row = FaktorLain()
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
    request.session.flash('faktorlain reklame %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('reklame-faktorlain'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='reklame-faktorlain-add', renderer='templates/faktorlain/add.pt',
             permission='reklame-faktorlain-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                request.session.flash('Error Kode atau Nama','error')
                return dict(form=form)				
                return HTTPFound(location=request.route_url('reklame-faktorlain-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(FaktorLain).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'faktorlain reklame ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='reklame-faktorlain-edit', renderer='templates/faktorlain/edit.pt',
             permission='reklame-faktorlain-edit')
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
@view_config(route_name='reklame-faktorlain-delete', renderer='templates/faktorlain/delete.pt',
             permission='reklame-faktorlain-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    uid = row.id
    
    if not row:
        return id_not_found(request)
        
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            try:
                msg = 'faktorlain reklame ID %d %s sudah dihapus.' % (row.id, row.nama)
                q.delete()
                DBSession.flush()
                request.session.flash(msg)
            except ValidationFailure, e:
                request.session.flash('Error saat menghapus data','error')
                return dict(form=form)
            #save_request(dict(controls), request, row)
        return route_list(request)
    return dict(row=row,form=form.render())
